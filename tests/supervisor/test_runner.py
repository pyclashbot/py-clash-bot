"""Process-per-guest supervision: groups, lock, backoff, shutdown."""

from __future__ import annotations

import signal
import subprocess
from typing import TYPE_CHECKING

import pytest

from pyclashbot.supervisor.alloc import GuestAllocator
from pyclashbot.supervisor.runner import (
    AlreadyRunningError,
    AlreadySupervisedError,
    Backoff,
    RestartBudgetExceededError,
    SingleInstanceLock,
    Supervisor,
    guest_child_argv,
    guest_child_env,
)

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence

    from pyclashbot.supervisor.spec import GuestSpec


class FakeChild:
    def __init__(self, pid: int = 100, *, hang_waits: int = 0) -> None:
        self.pid = pid
        self.hang_waits = hang_waits
        self.waits = 0
        self.terminated = 0
        self.killed = 0
        self._rc: int | None = None

    def poll(self) -> int | None:
        return self._rc

    def wait(self, timeout: float | None = None) -> int:
        self.waits += 1
        if self.hang_waits > 0:
            self.hang_waits -= 1
            raise subprocess.TimeoutExpired("guest", timeout or 0.0)
        self._rc = 0
        return 0

    def terminate(self) -> None:
        self.terminated += 1

    def kill(self) -> None:
        self.killed += 1


class FakeManager:
    def __init__(self) -> None:
        self.recreated: list[str] = []
        self.stopped: list[str] = []
        self.ready: list[str] = []

    def recreate(self, spec: GuestSpec) -> None:
        self.recreated.append(spec.serial)

    def stop(self, spec: GuestSpec) -> None:
        self.stopped.append(spec.serial)

    def wait_ready(self, spec: GuestSpec, *, timeout: float | None = None) -> bool:
        self.ready.append(spec.serial)
        return True


class Spawner:
    def __init__(self, *children: FakeChild) -> None:
        self.children = list(children)
        self.calls: list[tuple[list[str], dict[str, str]]] = []

    def __call__(self, argv: Sequence[str], env: Mapping[str, str]) -> FakeChild:
        self.calls.append((list(argv), dict(env)))
        return self.children.pop(0)


class SignalRecorder:
    def __init__(self) -> None:
        self.calls: list[tuple[int, int]] = []

    def __call__(self, pid: int, sig: int) -> None:
        self.calls.append((pid, sig))


@pytest.fixture
def spec() -> GuestSpec:
    return GuestAllocator().allocate(0)


def _supervisor(
    manager: FakeManager, spawner: Spawner, signals: SignalRecorder, sleeps: list[float], tmp_path
) -> Supervisor:
    return Supervisor(
        manager,
        spawn=spawner,
        signal_group=signals,
        lock_path=tmp_path / "supervisor.lock",
        max_restarts=2,
        backoff=Backoff(initial=0.5, multiplier=2.0, maximum=10.0),
        sleep=sleeps.append,
    )


def test_backoff_grows_and_caps() -> None:
    backoff = Backoff(initial=0.5, multiplier=2.0, maximum=3.0)
    assert [backoff.next_delay() for _ in range(4)] == [0.5, 1.0, 2.0, 3.0]
    backoff.reset()
    assert backoff.next_delay() == 0.5


def test_single_instance_lock_is_exclusive(tmp_path) -> None:
    path = tmp_path / "supervisor.lock"
    first = SingleInstanceLock(path)
    second = SingleInstanceLock(path)

    first.acquire()
    with pytest.raises(AlreadyRunningError):
        second.acquire()

    first.release()
    second.acquire()
    second.release()


def test_single_instance_lock_context_releases(tmp_path) -> None:
    path = tmp_path / "supervisor.lock"
    with SingleInstanceLock(path) as lock:
        assert lock.held is True
    assert lock.held is False
    with SingleInstanceLock(path) as again:
        assert again.held is True


def test_child_argv_and_env_pin_the_explicit_serial(spec: GuestSpec) -> None:
    argv = guest_child_argv(spec)
    env = guest_child_env(spec, base={"PATH": "/bin", "ADB_SERIAL": "wrong"})

    assert spec.serial in argv
    assert argv[argv.index("--adb-serial") + 1] == spec.serial
    assert argv[argv.index("--adb-server-port") + 1] == str(spec.server_port)
    assert "kill-server" not in " ".join(argv)
    assert env["ADB_SERIAL"] == spec.serial
    assert env["ADB_MDNS"] == "0"
    assert env["PATH"] == "/bin"


def test_start_recreates_then_spawns_the_guest(spec: GuestSpec, tmp_path) -> None:
    manager = FakeManager()
    child = FakeChild(pid=777)
    spawner = Spawner(child)
    supervisor = _supervisor(manager, spawner, SignalRecorder(), [], tmp_path)

    assert supervisor.start(spec) is child
    assert manager.recreated == [spec.serial]
    assert spawner.calls[0][1]["ADB_SERIAL"] == spec.serial
    assert supervisor.handles[spec.serial].process is child

    with pytest.raises(AlreadySupervisedError):
        supervisor.start(spec)


def test_restart_backs_off_then_exhausts_budget(spec: GuestSpec, tmp_path) -> None:
    manager = FakeManager()
    signals = SignalRecorder()
    spawner = Spawner(FakeChild(pid=1), FakeChild(pid=2), FakeChild(pid=3))
    sleeps: list[float] = []
    supervisor = _supervisor(manager, spawner, signals, sleeps, tmp_path)
    supervisor.start(spec)

    supervisor.restart(spec)
    supervisor.restart(spec)
    assert sleeps == [0.5, 1.0]
    assert manager.recreated == [spec.serial, spec.serial, spec.serial]
    assert supervisor.handles[spec.serial].failures == 2

    with pytest.raises(RestartBudgetExceededError):
        supervisor.restart(spec)

    supervisor.mark_healthy(spec)
    assert supervisor.handles[spec.serial].failures == 0
    assert supervisor.backoff.next_delay() == 0.5


def test_stop_signals_the_group_then_stops_owned_guest(spec: GuestSpec, tmp_path) -> None:
    manager = FakeManager()
    signals = SignalRecorder()
    child = FakeChild(pid=321)
    supervisor = _supervisor(manager, Spawner(child), signals, [], tmp_path)
    supervisor.start(spec)

    supervisor.stop(spec)

    assert signals.calls == [(321, signal.SIGTERM)]
    assert child.killed == 0
    assert manager.stopped == [spec.serial]
    assert spec.serial not in supervisor.handles


def test_stop_escalates_to_sigkill_when_sigterm_is_ignored(spec: GuestSpec, tmp_path) -> None:
    manager = FakeManager()
    signals = SignalRecorder()
    child = FakeChild(pid=322, hang_waits=1)
    supervisor = _supervisor(manager, Spawner(child), signals, [], tmp_path)
    supervisor.start(spec)

    supervisor.stop(spec)

    assert signals.calls == [(322, signal.SIGTERM), (322, getattr(signal, "SIGKILL", signal.SIGTERM))]
    assert child.killed == 1
    assert manager.stopped == [spec.serial]


def test_shutdown_stops_every_guest_and_releases_the_lock(tmp_path) -> None:
    manager = FakeManager()
    specs = GuestAllocator().allocate_range(0, 2)
    supervisor = _supervisor(manager, Spawner(FakeChild(1), FakeChild(2)), SignalRecorder(), [], tmp_path)
    supervisor.lock.acquire()
    for spec in specs:
        supervisor.start(spec)

    supervisor.shutdown()

    assert sorted(manager.stopped) == sorted(spec.serial for spec in specs)
    assert supervisor.handles == {}
    assert supervisor.lock.held is False


def test_defaults_never_issue_a_global_adb_kill_server(spec: GuestSpec) -> None:
    argv = guest_child_argv(spec)
    assert "kill-server" not in argv
    assert "--adb-server-port" in argv
    assert guest_child_env(spec)["ADB_MDNS"] == "0"
