"""Headless entry-point tests."""

from __future__ import annotations

import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from pyclashbot.emulators import EmulatorType
from pyclashbot.headless import build_jobs, parse_args
from pyclashbot.interface.enums import UIField

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_parse_args_requires_a_serial(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ADB_SERIAL", raising=False)
    args = parse_args([])
    assert args.adb_serial is None
    assert args.emulator == "emuctl"


def test_build_jobs_defaults_to_emuctl() -> None:
    jobs = build_jobs(parse_args(["--adb-serial", "127.0.0.1:5555"]))
    assert jobs["emulator"] is EmulatorType.EMUCTL
    assert jobs[UIField.ADB_SERIAL.value] == "127.0.0.1:5555"
    assert jobs[UIField.CLASSIC_1V1_USER_TOGGLE.value] is True


def test_build_jobs_can_select_builtin_adb() -> None:
    jobs = build_jobs(parse_args(["--adb-serial", "emulator-5554", "--emulator", "adb"]))
    assert jobs["emulator"] is EmulatorType.ADB


def test_parse_args_reads_adb_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ADB_PATH", "/opt/platform-tools/adb")
    monkeypatch.setenv("ADB_SERVER_PORT", "5038")
    args = parse_args(["--adb-serial", "127.0.0.1:5555"])
    assert args.adb_path == "/opt/platform-tools/adb"
    assert args.adb_server_port == 5038


@pytest.mark.parametrize(
    ("emulator_type", "serial"),
    [(EmulatorType.EMUCTL, "127.0.0.1:5555"), (EmulatorType.ADB, "emulator-5554")],
)
def test_worker_passes_adb_settings(monkeypatch: pytest.MonkeyPatch, emulator_type, serial: str) -> None:
    from pyclashbot.bot import worker as worker_module

    captured: dict[str, object] = {}

    class _FakeController:
        def __init__(self, **kwargs: object) -> None:
            captured.update(kwargs)

        def restart(self, *, ready=None) -> bool:
            return True

    monkeypatch.setattr(worker_module, "get_emulator_registry", lambda: {emulator_type: _FakeController})
    jobs = build_jobs(
        parse_args(
            [
                "--emulator",
                "adb" if emulator_type is EmulatorType.ADB else "emuctl",
                "--adb-serial",
                serial,
                "--adb-path",
                "/tmp/adb",
                "--adb-server-port",
                "5038",
            ]
        )
    )
    worker = worker_module.WorkerProcess(jobs, None, None, "unused.log")  # ty: ignore[invalid-argument-type]
    logger = object()

    assert worker._setup_emulator(jobs, logger) is not None  # ty: ignore[invalid-argument-type]
    assert captured.pop("logger") is logger
    assert captured == {"device_serial": serial, "adb_path": "/tmp/adb", "adb_server_port": 5038}


def test_default_jobs_cover_state_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    from pyclashbot.bot import states
    from pyclashbot.bot.states import StateHistory, StateOrder, state_tree
    from pyclashbot.utils.logger import Logger

    jobs = build_jobs(parse_args(["--adb-serial", "127.0.0.1:5555"]))
    required = {
        "upgrade_user_toggle",
        "random_decks_user_toggle",
        "cycle_decks_user_toggle",
        "upgrade_princess_user_toggle",
        "card_mastery_user_toggle",
        "disable_win_track_toggle",
    }
    assert required <= jobs.keys()

    logger = Logger(stats=None, timed=False)
    history = StateHistory(logger)
    order = StateOrder()
    monkeypatch.setattr(states.time, "sleep", lambda _seconds: None)
    monkeypatch.setattr(states, "mode_used_in_1v1", None)
    monkeypatch.setattr(states, "end_fight_state", lambda *args, **kwargs: True)

    class _UntouchableEmulator:
        def __getattr__(self, name: str) -> object:
            raise AssertionError(f"default jobs touched emulator.{name}")

    for state in [
        "start",
        "switch_account",
        "upgrade",
        "upgrade_princess",
        "card_mastery",
        "randomize_deck",
        "cycle_deck",
        "end_fight",
    ]:
        state_tree(_UntouchableEmulator(), logger, state, jobs, history, order)


@pytest.mark.parametrize(("cleanup_on_exit", "stopped"), [(True, True), (False, False)])
def test_worker_run_exit_code_and_cleanup(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, cleanup_on_exit: bool, stopped: bool
) -> None:
    from multiprocessing import Event, Queue

    from pyclashbot.bot import worker as worker_module

    class _FakeEmulator:
        stopped = False

        def stop(self) -> None:
            type(self).stopped = True

    fake = _FakeEmulator()
    worker = worker_module.WorkerProcess(
        {}, Queue(), Event(), str(tmp_path / "worker.log"), cleanup_on_exit=cleanup_on_exit
    )
    monkeypatch.setattr(worker, "_setup_emulator", lambda *args: fake)
    monkeypatch.setattr(worker, "_run_bot_loop", lambda *args: False)

    with pytest.raises(SystemExit) as excinfo:
        worker.run()

    assert excinfo.value.code == 1
    assert fake.stopped is stopped


def test_build_jobs_rejects_unknown_override(tmp_path: Path) -> None:
    overrides = tmp_path / "jobs.json"
    overrides.write_text(json.dumps({"not_a_ui_field": True}), encoding="utf-8")

    with pytest.raises(ValueError, match="unknown job key"):
        build_jobs(parse_args(["--adb-serial", "127.0.0.1:5555", "--jobs", str(overrides)]))


def test_build_jobs_applies_overrides(tmp_path: Path) -> None:
    overrides = tmp_path / "jobs.json"
    overrides.write_text(json.dumps({UIField.CLASSIC_1V1_USER_TOGGLE.value: False}), encoding="utf-8")
    jobs = build_jobs(parse_args(["--adb-serial", "127.0.0.1:5555", "--jobs", str(overrides)]))
    assert jobs[UIField.CLASSIC_1V1_USER_TOGGLE.value] is False


def test_interface_enums_do_not_import_tkinter() -> None:
    code = "import sys; import pyclashbot.interface.enums; print('tkinter' in sys.modules)"
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
        env={**os.environ, "DISPLAY": ""},
    )
    assert result.stdout.strip() == "False", result.stdout


def test_headless_help_runs_without_display() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pyclashbot.headless", "--help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, "DISPLAY": ""},
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "--adb-serial" in result.stdout


def test_lazy_interface_reexports_gui_symbols() -> None:
    import pyclashbot.interface as interface

    assert "PyClashBotUI" in interface.__all__
    with pytest.raises(AttributeError):
        _ = interface.not_a_real_symbol


def test_emuctl_controller_is_registered_for_headless() -> None:
    from pyclashbot.emulators import get_emulator_registry

    registry = get_emulator_registry()
    assert EmulatorType.EMUCTL in registry
    module = importlib.import_module("pyclashbot.emulators.emuctl")
    assert registry[EmulatorType.EMUCTL] is module.EmuctlController
