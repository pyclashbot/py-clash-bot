"""Process-per-guest supervision.

One child process per guest, each in its own session/process group, with a
single-instance flock, bounded restart backoff, and a shutdown that signals the
group (then kills it) before stopping only that guest's own container/AVD.
"""

from __future__ import annotations

import logging
import os
import signal
import subprocess
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from pyclashbot.supervisor.guest import spawn_child

if TYPE_CHECKING:
    from pyclashbot.supervisor.guest import ChildProcess
    from pyclashbot.supervisor.spec import GuestSpec

logger = logging.getLogger(__name__)

DEFAULT_LOCK_PATH = Path("pyclashbot-supervisor.lock")
DEFAULT_STOP_TIMEOUT_S = 5.0

SpawnFn = Callable[[Sequence[str], Mapping[str, str]], "ChildProcess"]
SignalGroupFn = Callable[[int, int], None]


class GuestLifecycle(Protocol):
    def recreate(self, spec: GuestSpec) -> None: ...

    def stop(self, spec: GuestSpec) -> None: ...


class SupervisorError(RuntimeError):
    """Base class for supervisor lifecycle failures."""


class AlreadyRunningError(SupervisorError):
    """Another supervisor already holds the single-instance lock."""

    def __init__(self, path: Path) -> None:
        super().__init__(f"another supervisor is already running (lock: {path})")
        self.path = path


class AlreadySupervisedError(SupervisorError):
    """A guest is already being supervised."""

    def __init__(self, serial: str) -> None:
        super().__init__(f"guest {serial!r} is already supervised")
        self.serial = serial


class RestartBudgetExceededError(SupervisorError):
    """Backoff retries for a guest were exhausted."""

    def __init__(self, serial: str, failures: int) -> None:
        super().__init__(f"guest {serial!r} exceeded {failures} restart attempts")
        self.serial = serial
        self.failures = failures


@dataclass(slots=True)
class Backoff:
    """Exponential, capped restart delay; reset after a healthy run."""

    initial: float = 0.5
    multiplier: float = 2.0
    maximum: float = 30.0
    jitter: Callable[[], float] | None = None
    _attempt: int = field(default=0, init=False)

    def next_delay(self) -> float:
        delay = min(self.maximum, self.initial * (self.multiplier**self._attempt))
        self._attempt += 1
        if self.jitter is not None:
            delay = min(self.maximum, max(0.0, delay * self.jitter()))
        return delay

    def reset(self) -> None:
        self._attempt = 0


class SingleInstanceLock:
    """Exclusive, non-blocking OS file lock around one supervisor process."""

    def __init__(self, path: Path | str = DEFAULT_LOCK_PATH) -> None:
        self.path = Path(path)
        self._fd: int | None = None

    @property
    def held(self) -> bool:
        return self._fd is not None

    def acquire(self) -> None:
        if self._fd is not None:
            return
        fd = os.open(self.path, os.O_CREAT | os.O_RDWR, 0o600)
        try:
            _lock_fd(fd)
        except OSError:
            os.close(fd)
            raise AlreadyRunningError(self.path) from None
        os.write(fd, f"{os.getpid()}\n".encode())
        self._fd = fd
        logger.debug("supervisor lock acquired path=%s", self.path)

    def release(self) -> None:
        fd = self._fd
        if fd is None:
            return
        self._fd = None
        try:
            _unlock_fd(fd)
        finally:
            os.close(fd)
            logger.debug("supervisor lock released path=%s", self.path)

    def __enter__(self) -> SingleInstanceLock:
        self.acquire()
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.release()


def _lock_fd(fd: int) -> None:
    if sys.platform == "win32":
        import msvcrt

        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        return
    import fcntl

    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)


def _unlock_fd(fd: int) -> None:
    if sys.platform == "win32":
        import msvcrt

        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        return
    import fcntl

    fcntl.flock(fd, fcntl.LOCK_UN)


def guest_child_argv(spec: GuestSpec) -> list[str]:
    """The child targets the guest's explicit serial, never discovery order."""
    return [
        sys.executable,
        "-m",
        "pyclashbot.headless",
        "--emulator",
        "emuctl",
        "--adb-serial",
        spec.serial,
        "--adb-server-port",
        str(spec.server_port),
    ]


def guest_child_env(spec: GuestSpec, *, base: Mapping[str, str] | None = None) -> dict[str, str]:
    env = dict(os.environ if base is None else base)
    env.update(spec.env())
    return env


def _signal_process_group(pid: int, sig: int) -> None:
    try:
        if sys.platform == "win32":
            os.kill(pid, sig)
        else:
            os.killpg(os.getpgid(pid), sig)
    except (ProcessLookupError, PermissionError, OSError):
        return


def _default_spawn(argv: Sequence[str], env: Mapping[str, str]) -> ChildProcess:
    return spawn_child(argv, env)


@dataclass(slots=True)
class GuestHandle:
    spec: GuestSpec
    process: ChildProcess
    failures: int = 0


class Supervisor:
    """Owns one managed child per guest and the shutdown contract around it."""

    def __init__(
        self,
        manager: GuestLifecycle,
        *,
        spawn: SpawnFn | None = None,
        signal_group: SignalGroupFn = _signal_process_group,
        lock_path: Path | str = DEFAULT_LOCK_PATH,
        max_restarts: int = 3,
        backoff: Backoff | None = None,
        stop_timeout: float = DEFAULT_STOP_TIMEOUT_S,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.manager = manager
        self._spawn = spawn or _default_spawn
        self._signal_group = signal_group
        self.lock = SingleInstanceLock(lock_path)
        self.max_restarts = max_restarts
        self.backoff = backoff or Backoff()
        self.stop_timeout = stop_timeout
        self._sleep = sleep
        self._handles: dict[str, GuestHandle] = {}

    @property
    def handles(self) -> dict[str, GuestHandle]:
        return dict(self._handles)

    def start(self, spec: GuestSpec) -> ChildProcess:
        if spec.serial in self._handles:
            raise AlreadySupervisedError(spec.serial)
        self.manager.recreate(spec)
        child = self._spawn(guest_child_argv(spec), guest_child_env(spec))
        self._handles[spec.serial] = GuestHandle(spec=spec, process=child)
        logger.debug("supervised guest serial=%s pid=%s", spec.serial, child.pid)
        return child

    def restart(self, spec: GuestSpec) -> ChildProcess:
        handle = self._handles.get(spec.serial)
        if handle is None:
            raise AlreadySupervisedError(spec.serial)
        if handle.failures >= self.max_restarts:
            raise RestartBudgetExceededError(spec.serial, handle.failures)
        delay = self.backoff.next_delay()
        self._sleep(delay)
        handle.failures += 1
        self._terminate_tree(handle.process, timeout=self.stop_timeout)
        self.manager.recreate(spec)
        handle.process = self._spawn(guest_child_argv(spec), guest_child_env(spec))
        logger.debug(
            "restarted guest serial=%s pid=%s attempt=%d delay=%.2fs",
            spec.serial,
            handle.process.pid,
            handle.failures,
            delay,
        )
        return handle.process

    def mark_healthy(self, spec: GuestSpec) -> None:
        handle = self._handles.get(spec.serial)
        if handle is not None:
            handle.failures = 0
        self.backoff.reset()

    def stop(self, spec: GuestSpec, *, timeout: float | None = None) -> None:
        handle = self._handles.pop(spec.serial, None)
        if handle is not None:
            self._terminate_tree(handle.process, timeout=self.stop_timeout if timeout is None else timeout)
        self.manager.stop(spec)

    def shutdown(self, *, timeout: float | None = None) -> None:
        for serial in list(self._handles):
            spec = self._handles[serial].spec
            self.stop(spec, timeout=timeout)
        self.backoff.reset()
        self.lock.release()

    def _terminate_tree(self, process: ChildProcess, *, timeout: float) -> None:
        if process.poll() is not None:
            return
        self._signal_group(process.pid, signal.SIGTERM)
        try:
            process.wait(timeout=timeout)
            return
        except (subprocess.TimeoutExpired, TimeoutError, OSError):
            logger.debug("guest pid=%s ignored SIGTERM; escalating", process.pid)
        kill_sig = getattr(signal, "SIGKILL", signal.SIGTERM)
        self._signal_group(process.pid, kill_sig)
        try:
            process.kill()
        except (ProcessLookupError, OSError):
            pass
        try:
            process.wait(timeout=timeout)
        except (subprocess.TimeoutExpired, TimeoutError, OSError):
            logger.warning("guest pid=%s did not reap after SIGKILL", process.pid)
