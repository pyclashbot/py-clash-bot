"""Guest lifecycle: docker/AVD re-create plus readiness and onboarding hooks.

Every side effect is injected so the skeleton is exercised offline. The docker
path only ever touches containers carrying this guest's label, and the AVD path
addresses the emulator by the guest's explicit serial — no global ``adb
kill-server`` and no discovery-order selection.
"""

from __future__ import annotations

import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence

    from pyclashbot.supervisor.spec import GuestSpec

DOCKER_LABEL_KEY = "pyclashbot.supervisor.guest"
DOCKER_INDEX_LABEL_KEY = "pyclashbot.supervisor.index"
DEFAULT_DOCKER_IMAGE = "pyclashbot/android:latest"
DEFAULT_CONTAINER_ADB_PORT = 5037
DEFAULT_CONTAINER_DEVICE_PORT = 5555
DEFAULT_AVD_SYSTEM_IMAGE = "system-images;android-30;google_apis;x86_64"
DEFAULT_AVD_DEVICE = "pixel"
DEFAULT_READY_TIMEOUT_S = 300.0


@dataclass(frozen=True, slots=True)
class CommandResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""

    @property
    def ok(self) -> bool:
        return self.returncode == 0


class CommandRunner(Protocol):
    """Runs a short-lived argv with no shell; returns captured text."""

    def __call__(self, argv: Sequence[str], *, timeout: float | None = None) -> CommandResult: ...


class ChildProcess(Protocol):
    """The Popen members the supervisor needs (structural, fake-friendly)."""

    @property
    def pid(self) -> int: ...

    def poll(self) -> int | None: ...

    def wait(self, timeout: float | None = None) -> int: ...

    def terminate(self) -> None: ...

    def kill(self) -> None: ...


class GuestRuntime(Protocol):
    """Container/emulator backend for one guest."""

    def ensure(self, spec: GuestSpec) -> None: ...

    def stop(self, spec: GuestSpec) -> None: ...

    def is_running(self, spec: GuestSpec) -> bool: ...

    def ready(self, spec: GuestSpec, *, timeout: float) -> bool: ...


def _default_runner(argv: Sequence[str], *, timeout: float | None = None) -> CommandResult:
    result = subprocess.run(
        list(argv),
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )
    return CommandResult(returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)


# ── docker argv builders (pure, testable) ──


def docker_run_argv(
    spec: GuestSpec,
    *,
    image: str = DEFAULT_DOCKER_IMAGE,
    container_adb_port: int = DEFAULT_CONTAINER_ADB_PORT,
    container_device_port: int = DEFAULT_CONTAINER_DEVICE_PORT,
) -> list[str]:
    return [
        "docker",
        "run",
        "-d",
        "--name",
        spec.container_name,
        "--label",
        f"{DOCKER_LABEL_KEY}={spec.serial}",
        "--label",
        f"{DOCKER_INDEX_LABEL_KEY}={spec.index}",
        "-e",
        f"ADB_SERIAL={spec.serial}",
        "-e",
        "ADB_MDNS=0",
        "-e",
        f"PYCLASHBOT_GUEST_IP={spec.ip}",
        "-p",
        f"127.0.0.1:{spec.server_port}:{container_adb_port}",
        "-p",
        f"127.0.0.1:{spec.device_port}:{container_device_port}",
        image,
    ]


def docker_list_owned_argv(spec: GuestSpec) -> list[str]:
    """List only containers labelled as this guest (never all containers)."""
    return ["docker", "ps", "-aq", "--filter", f"label={DOCKER_LABEL_KEY}={spec.serial}"]


def docker_remove_argv(container_ids: Sequence[str]) -> list[str]:
    return ["docker", "rm", "-f", *container_ids]


def adb_emu_kill_argv(spec: GuestSpec) -> list[str]:
    """Stop this guest's emulator through its explicit serial."""
    return ["adb", "-s", spec.serial, "emu", "kill"]


# ── AVD argv builders (pure, testable) ──


def avd_create_argv(
    spec: GuestSpec,
    *,
    system_image: str = DEFAULT_AVD_SYSTEM_IMAGE,
    device: str = DEFAULT_AVD_DEVICE,
) -> list[str]:
    return [
        "avdmanager",
        "create",
        "avd",
        "-n",
        spec.avd_name,
        "-k",
        system_image,
        "-d",
        device,
        "--force",
    ]


def avd_delete_argv(spec: GuestSpec) -> list[str]:
    return ["avdmanager", "delete", "avd", "-n", spec.avd_name]


def emulator_start_argv(spec: GuestSpec) -> list[str]:
    """The emulator's console port is adb-1, so its adb port is ``device_port``."""
    return [
        "emulator",
        "-avd",
        spec.avd_name,
        "-port",
        str(spec.device_port - 1),
        "-no-snapshot",
        "-no-audio",
        "-no-boot-anim",
    ]


# ── child process launch (groups + parent-death signal) ──


def child_launch_kwargs() -> dict[str, Any]:
    """A new session/process group so the supervisor can signal the whole tree."""
    if sys.platform == "win32":
        flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        flags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)
        return {"creationflags": flags}
    return {"start_new_session": True}


def _pdeathsig() -> None:  # pragma: no cover - executed only in a real child
    """Ask Linux to SIGTERM the child if the supervisor dies (best effort)."""
    try:
        import ctypes

        libc = ctypes.CDLL("libc.so.6", use_errno=True)
        libc.prctl(1, signal.SIGTERM)  # PR_SET_PDEATHSIG
    except Exception:
        return


def spawn_child(
    argv: Sequence[str],
    env: Mapping[str, str] | None = None,
) -> ChildProcess:
    kwargs = child_launch_kwargs()
    if sys.platform.startswith("linux"):
        kwargs["preexec_fn"] = _pdeathsig
    return subprocess.Popen(
        list(argv),
        env=None if env is None else dict(env),
        **kwargs,
    )


# ── runtimes ──


class DockerRuntime:
    """Re-create and stop only the containers carrying this guest's label."""

    def __init__(
        self,
        runner: CommandRunner | None = None,
        *,
        image: str = DEFAULT_DOCKER_IMAGE,
        container_adb_port: int = DEFAULT_CONTAINER_ADB_PORT,
        container_device_port: int = DEFAULT_CONTAINER_DEVICE_PORT,
        timeout: float = 120.0,
    ) -> None:
        self._run = runner or _default_runner
        self.image = image
        self.container_adb_port = container_adb_port
        self.container_device_port = container_device_port
        self.timeout = timeout

    def _ids_for(self, spec: GuestSpec) -> list[str]:
        result = self._run(docker_list_owned_argv(spec), timeout=self.timeout)
        if not result.ok:
            return []
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    def stop(self, spec: GuestSpec) -> None:
        container_ids = self._ids_for(spec)
        if container_ids:
            self._run(docker_remove_argv(container_ids), timeout=self.timeout)

    def ensure(self, spec: GuestSpec) -> None:
        self.stop(spec)  # re-create, never adopt a half-broken container
        argv = docker_run_argv(
            spec,
            image=self.image,
            container_adb_port=self.container_adb_port,
            container_device_port=self.container_device_port,
        )
        result = self._run(argv, timeout=self.timeout)
        if not result.ok:
            raise RuntimeError(f"docker run failed for {spec.container_name}: {result.stderr.strip()}")

    def is_running(self, spec: GuestSpec) -> bool:
        return bool(self._ids_for(spec))

    def ready(self, spec: GuestSpec, *, timeout: float) -> bool:
        # Container liveness is the skeleton's readiness signal; onboarding is
        # layered on top by GuestManager.
        return self.is_running(spec)


class AvdRuntime:
    """Re-create an AVD and start its emulator as a supervised child."""

    def __init__(
        self,
        runner: CommandRunner | None = None,
        *,
        spawn: Callable[[Sequence[str], Mapping[str, str] | None], ChildProcess] | None = None,
        system_image: str = DEFAULT_AVD_SYSTEM_IMAGE,
        device: str = DEFAULT_AVD_DEVICE,
        timeout: float = 120.0,
    ) -> None:
        self._run = runner or _default_runner
        self._spawn = spawn or spawn_child
        self.system_image = system_image
        self.device = device
        self.timeout = timeout
        self._children: dict[str, ChildProcess] = {}

    def stop(self, spec: GuestSpec) -> None:
        self._run(adb_emu_kill_argv(spec), timeout=self.timeout)
        child = self._children.pop(spec.serial, None)
        if child is not None and child.poll() is None:
            child.terminate()
        self._run(avd_delete_argv(spec), timeout=self.timeout)

    def ensure(self, spec: GuestSpec) -> None:
        self.stop(spec)
        created = self._run(
            avd_create_argv(spec, system_image=self.system_image, device=self.device),
            timeout=self.timeout,
        )
        if not created.ok:
            raise RuntimeError(f"avdmanager create failed for {spec.avd_name}: {created.stderr.strip()}")
        self._children[spec.serial] = self._spawn(emulator_start_argv(spec), spec.env())

    def is_running(self, spec: GuestSpec) -> bool:
        child = self._children.get(spec.serial)
        return child is not None and child.poll() is None

    def ready(self, spec: GuestSpec, *, timeout: float) -> bool:
        return self.is_running(spec)


class GuestManager:
    """Recreate a guest, wait for runtime readiness, then run the onboarding hook."""

    def __init__(
        self,
        runtime: GuestRuntime,
        *,
        onboarding: Callable[[GuestSpec], bool] | None = None,
        ready_timeout: float = DEFAULT_READY_TIMEOUT_S,
        poll_interval: float = 1.0,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.runtime = runtime
        self.onboarding = onboarding
        self.ready_timeout = ready_timeout
        self.poll_interval = poll_interval
        self._sleep = sleep
        self._clock = clock

    def recreate(self, spec: GuestSpec) -> None:
        self.runtime.stop(spec)
        self.runtime.ensure(spec)

    def wait_ready(self, spec: GuestSpec, *, timeout: float | None = None) -> bool:
        budget = self.ready_timeout if timeout is None else timeout
        deadline = self._clock() + budget
        while self._clock() < deadline:
            if self.runtime.ready(spec, timeout=budget):
                if self.onboarding is None or self.onboarding(spec):
                    return True
            self._sleep(self.poll_interval)
        return False

    def start(self, spec: GuestSpec, *, timeout: float | None = None) -> bool:
        self.recreate(spec)
        return self.wait_ready(spec, timeout=timeout)

    def stop(self, spec: GuestSpec) -> None:
        self.runtime.stop(spec)

    def stop_all(self, specs: Sequence[GuestSpec]) -> None:
        for spec in specs:
            self.stop(spec)
