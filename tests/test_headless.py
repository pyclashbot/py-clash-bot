"""Tests for the headless entry point and the tkinter-free import graph."""

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
    """No serial and no $ADB_SERIAL is a usage error."""
    monkeypatch.delenv("ADB_SERIAL", raising=False)
    args = parse_args([])
    assert args.adb_serial is None
    assert args.emulator == "emuctl"


def test_parse_args_reads_env_serial(monkeypatch: pytest.MonkeyPatch) -> None:
    """$ADB_SERIAL is the default serial."""
    monkeypatch.setenv("ADB_SERIAL", "127.0.0.1:5555")
    assert parse_args([]).adb_serial == "127.0.0.1:5555"


def test_build_jobs_defaults_to_emuctl() -> None:
    """The headless default backend is emuctl, targeting the given serial."""
    jobs = build_jobs(parse_args(["--adb-serial", "127.0.0.1:5555"]))
    assert jobs["emulator"] is EmulatorType.EMUCTL
    assert jobs[UIField.ADB_SERIAL.value] == "127.0.0.1:5555"
    assert jobs[UIField.CLASSIC_1V1_USER_TOGGLE.value] is True


def test_build_jobs_can_select_builtin_adb() -> None:
    """--emulator adb selects the repo's own ADB controller."""
    jobs = build_jobs(parse_args(["--adb-serial", "emulator-5554", "--emulator", "adb"]))
    assert jobs["emulator"] is EmulatorType.ADB


def test_parse_args_reads_adb_path_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """$ADB_PATH and $ADB_SERVER_PORT supply the adb binary defaults."""
    monkeypatch.setenv("ADB_PATH", "/opt/platform-tools/adb")
    monkeypatch.setenv("ADB_SERVER_PORT", "5038")
    args = parse_args(["--adb-serial", "127.0.0.1:5555"])
    assert args.adb_path == "/opt/platform-tools/adb"
    assert args.adb_server_port == 5038
    assert parse_args(["--adb-serial", "x:1", "--adb-path", "/tmp/adb"]).adb_path == "/tmp/adb"


def test_build_jobs_carries_adb_path_and_port() -> None:
    """The adb binary settings travel in the worker jobs dict."""
    jobs = build_jobs(
        parse_args(["--adb-serial", "127.0.0.1:5555", "--adb-path", "/tmp/adb", "--adb-server-port", "5038"])
    )
    assert jobs["adb_path"] == "/tmp/adb"
    assert jobs["adb_server_port"] == 5038


def test_worker_passes_adb_path_to_emuctl(monkeypatch: pytest.MonkeyPatch) -> None:
    """WorkerProcess forwards the adb settings when constructing EmuctlController."""
    from pyclashbot.bot import worker as worker_module

    captured: dict[str, object] = {}

    class _FakeController:
        def __init__(self, **kwargs: object) -> None:
            captured.update(kwargs)

        def restart(self) -> bool:
            return True

    monkeypatch.setattr(worker_module, "get_emulator_registry", lambda: {EmulatorType.EMUCTL: _FakeController})
    jobs = build_jobs(
        parse_args(["--adb-serial", "127.0.0.1:5555", "--adb-path", "/tmp/adb", "--adb-server-port", "5038"])
    )
    worker = worker_module.WorkerProcess(jobs, None, None, "unused.log")  # ty: ignore[invalid-argument-type]
    logger = object()

    assert worker._setup_emulator(jobs, logger) is not None  # ty: ignore[invalid-argument-type]
    assert captured.pop("logger") is logger
    assert captured == {
        "device_serial": "127.0.0.1:5555",
        "adb_path": "/tmp/adb",
        "adb_server_port": 5038,
    }


def test_build_jobs_applies_overrides(tmp_path: Path) -> None:
    """A --jobs file overrides individual toggles."""
    overrides = tmp_path / "jobs.json"
    overrides.write_text(
        json.dumps({UIField.CLASSIC_1V1_USER_TOGGLE.value: False}),
        encoding="utf-8",
    )
    jobs = build_jobs(parse_args(["--adb-serial", "127.0.0.1:5555", "--jobs", str(overrides)]))
    assert jobs[UIField.CLASSIC_1V1_USER_TOGGLE.value] is False


def test_interface_enums_do_not_import_tkinter() -> None:
    """The bot core must be importable without tkinter (headless Linux)."""
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
    """`python -m pyclashbot.headless --help` works with no X display."""
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
    """The lazy re-exports still resolve for GUI consumers."""
    import pyclashbot.interface as interface

    assert "PyClashBotUI" in interface.__all__
    with pytest.raises(AttributeError):
        _ = interface.not_a_real_symbol


def test_emuctl_controller_is_registered_for_headless() -> None:
    """The emuctl backend is selectable through the registry."""
    from pyclashbot.emulators import get_emulator_registry

    registry = get_emulator_registry()
    assert EmulatorType.EMUCTL in registry
    module = importlib.import_module("pyclashbot.emulators.emuctl")
    assert registry[EmulatorType.EMUCTL] is module.EmuctlController
