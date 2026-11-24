"""Guest runtimes and the readiness/onboarding hook, all with fakes."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest

from pyclashbot.supervisor.guest import (
    AvdRuntime,
    CommandResult,
    DockerRuntime,
    GuestManager,
    adb_emu_kill_argv,
    avd_create_argv,
    avd_delete_argv,
    child_launch_kwargs,
    docker_list_owned_argv,
    docker_remove_argv,
    docker_run_argv,
    emulator_start_argv,
    spawn_child,
)
from pyclashbot.supervisor.spec import GuestSpec

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


class FakeRunner:
    def __init__(self, stdout: str = "") -> None:
        self.calls: list[list[str]] = []
        self.stdout = stdout

    def __call__(self, argv: Sequence[str], *, timeout: float | None = None) -> CommandResult:
        self.calls.append(list(argv))
        stdout = self.stdout if list(argv[:2]) == ["docker", "ps"] else ""
        return CommandResult(returncode=0, stdout=stdout)


class FakeRuntime:
    def __init__(self, ready_results: Sequence[bool] = (True,)) -> None:
        self.calls: list[tuple[str, str]] = []
        self.ready_results = list(ready_results)

    def ensure(self, spec: GuestSpec) -> None:
        self.calls.append(("ensure", spec.serial))

    def stop(self, spec: GuestSpec) -> None:
        self.calls.append(("stop", spec.serial))

    def is_running(self, spec: GuestSpec) -> bool:
        return True

    def ready(self, spec: GuestSpec, *, timeout: float) -> bool:
        self.calls.append(("ready", spec.serial))
        return self.ready_results.pop(0) if self.ready_results else True


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


class FakeChild:
    def __init__(self, pid: int = 321) -> None:
        self.pid = pid
        self.killed = False

    def poll(self) -> int | None:
        return None

    def wait(self, timeout: float | None = None) -> int:
        return 0

    def terminate(self) -> None:
        return None

    def kill(self) -> None:
        self.killed = True


def test_docker_run_argv_carries_identity_labels_and_ports() -> None:
    spec = GuestSpec.for_index(1)
    argv = docker_run_argv(spec)

    assert argv[:2] == ["docker", "run"]
    assert spec.container_name in argv
    assert f"pyclashbot.supervisor.guest={spec.serial}" in argv
    assert f"ADB_SERIAL={spec.serial}" in argv
    assert "ADB_MDNS=0" in argv
    assert f"127.0.0.1:{spec.server_port}:5037" in argv
    assert f"127.0.0.1:{spec.device_port}:5555" in argv
    assert "kill-server" not in " ".join(argv)


def test_docker_list_and_remove_are_label_scoped() -> None:
    spec = GuestSpec.for_index(0)
    assert docker_list_owned_argv(spec)[-1] == f"label=pyclashbot.supervisor.guest={spec.serial}"
    assert docker_remove_argv(["abc", "def"]) == ["docker", "rm", "-f", "abc", "def"]


def test_docker_runtime_stops_only_labelled_containers() -> None:
    runner = FakeRunner(stdout="abc123\ndef456\n")
    runtime = DockerRuntime(runner)
    spec = GuestSpec.for_index(0)

    runtime.stop(spec)

    assert runner.calls[0][:2] == ["docker", "ps"]
    assert runner.calls[1] == ["docker", "rm", "-f", "abc123", "def456"]
    assert all("kill-server" not in " ".join(call) for call in runner.calls)


def test_docker_runtime_stop_without_matches_runs_no_remove() -> None:
    runner = FakeRunner(stdout="")
    DockerRuntime(runner).stop(GuestSpec.for_index(0))
    assert [call[:2] for call in runner.calls] == [["docker", "ps"]]


def test_docker_runtime_ensure_recreates_then_runs() -> None:
    runner = FakeRunner(stdout="abc123\n")
    runtime = DockerRuntime(runner)
    spec = GuestSpec.for_index(0)

    runtime.ensure(spec)

    assert [call[:2] for call in runner.calls] == [["docker", "ps"], ["docker", "rm"], ["docker", "run"]]


def test_docker_runtime_ready_tracks_labelled_containers() -> None:
    spec = GuestSpec.for_index(0)
    assert DockerRuntime(FakeRunner(stdout="abc\n")).ready(spec, timeout=1.0) is True
    assert DockerRuntime(FakeRunner(stdout="")).ready(spec, timeout=1.0) is False


def test_avd_argv_uses_the_explicit_serial_and_no_global_kill() -> None:
    spec = GuestSpec.for_index(0)
    stop_argv = adb_emu_kill_argv(spec)
    assert stop_argv == ["adb", "-s", spec.serial, "emu", "kill"]
    assert avd_delete_argv(spec)[:3] == ["avdmanager", "delete", "avd"]
    assert avd_create_argv(spec)[:3] == ["avdmanager", "create", "avd"]
    assert emulator_start_argv(spec)[:4] == ["emulator", "-avd", spec.avd_name, "-port"]
    assert emulator_start_argv(spec)[4] == str(spec.device_port - 1)
    assert "kill-server" not in " ".join(emulator_start_argv(spec))


def test_avd_runtime_ensure_recreates_and_spawns_with_guest_env() -> None:
    runner = FakeRunner()
    spawned: list[tuple[list[str], Mapping[str, str] | None]] = []

    def spawn(argv: Sequence[str], env: Mapping[str, str] | None = None) -> FakeChild:
        spawned.append((list(argv), env))
        return FakeChild()

    runtime = AvdRuntime(runner, spawn=spawn)
    spec = GuestSpec.for_index(1)
    runtime.ensure(spec)

    assert [call[0] for call in runner.calls] == ["adb", "avdmanager", "avdmanager"]
    assert spawned and spawned[0][0][:2] == ["emulator", "-avd"]
    assert spawned[0][1] is not None and spawned[0][1]["ADB_SERIAL"] == spec.serial
    assert runtime.is_running(spec) is True

    runtime.stop(spec)
    assert runner.calls[-1] == ["avdmanager", "delete", "avd", "-n", spec.avd_name]


def test_child_launch_kwargs_starts_a_new_session_on_posix() -> None:
    kwargs = child_launch_kwargs()
    if sys.platform == "win32":
        assert "creationflags" in kwargs
    else:
        assert kwargs == {"start_new_session": True}


def test_spawn_child_uses_explicit_env_without_a_shell(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_popen(argv: list[str], **kwargs: object) -> FakeChild:
        captured["argv"] = argv
        captured.update(kwargs)
        return FakeChild()

    monkeypatch.setattr("pyclashbot.supervisor.guest.subprocess.Popen", fake_popen)
    spec = GuestSpec.for_index(0)
    spawn_child(["emulator", "-avd", spec.avd_name], spec.env())

    assert captured["argv"] == ["emulator", "-avd", spec.avd_name]
    assert captured["env"] == spec.env()
    assert "shell" not in captured


def test_guest_manager_runs_onboarding_only_after_readiness() -> None:
    clock = FakeClock()
    runtime = FakeRuntime(ready_results=(False, True))
    seen: list[GuestSpec] = []
    manager = GuestManager(
        runtime,
        onboarding=lambda spec: seen.append(spec) or True,
        ready_timeout=10.0,
        poll_interval=1.0,
        sleep=clock.sleep,
        clock=clock,
    )
    spec = GuestSpec.for_index(0)

    assert manager.start(spec) is True
    assert runtime.calls == [
        ("stop", spec.serial),
        ("ensure", spec.serial),
        ("ready", spec.serial),
        ("ready", spec.serial),
    ]
    assert seen == [spec]
    assert clock.now == 1.0


def test_guest_manager_times_out_without_readiness() -> None:
    clock = FakeClock()
    runtime = FakeRuntime(ready_results=(False, False, False))
    manager = GuestManager(
        runtime,
        ready_timeout=2.0,
        poll_interval=1.0,
        sleep=clock.sleep,
        clock=clock,
    )
    assert manager.start(GuestSpec.for_index(0)) is False
    assert clock.now >= 2.0


def test_guest_manager_treats_onboarding_false_as_not_ready() -> None:
    clock = FakeClock()
    runtime = FakeRuntime(ready_results=(True, True, True))
    manager = GuestManager(
        runtime,
        onboarding=lambda spec: False,
        ready_timeout=2.0,
        poll_interval=1.0,
        sleep=clock.sleep,
        clock=clock,
    )
    assert manager.start(GuestSpec.for_index(0)) is False
    assert clock.now >= 2.0
