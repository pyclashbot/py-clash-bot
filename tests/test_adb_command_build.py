"""Offline coverage for ADB command construction (argv, no shell).

Pins that ``adb()`` and ``discover_devices()`` build proper argv lists and route
through the timeout helper with ``shell`` never involved, without any hardware.
The helper is monkeypatched to capture the argv and return a canned result.
"""

import subprocess

import pytest

from pyclashbot.emulators import adb_base
from pyclashbot.emulators.adb_base import AdbBasedController
from pyclashbot.emulators.base import EmulatorNotReadyError


class _FakeAdb(AdbBasedController):
    """Concrete, cheap-to-build controller (base __init__ is bypassed)."""


def _make_controller(**attrs) -> _FakeAdb:
    ctrl = _FakeAdb.__new__(_FakeAdb)
    ctrl.device_serial = attrs.get("device_serial", "127.0.0.1:5555")
    ctrl.adb_path = attrs.get("adb_path", "adb")
    ctrl.adb_server_port = attrs.get("adb_server_port", None)
    ctrl.adb_env = attrs.get("adb_env", None)
    return ctrl


def _capture(monkeypatch, stdout: str = "ok"):
    seen: dict = {}

    def spy(argv, **kwargs):
        seen["argv"] = argv
        seen["kwargs"] = kwargs
        return subprocess.CompletedProcess(argv, 0, stdout, "")

    monkeypatch.setattr(adb_base, "run_command", spy)
    return seen


def test_adb_scopes_serial_via_argv(monkeypatch):
    seen = _capture(monkeypatch)
    _make_controller(adb_server_port=5041).adb("shell wm size")
    argv = seen["argv"]

    assert "-P" in argv and argv[argv.index("-P") + 1] == "5041"
    assert "-s" in argv and argv[argv.index("-s") + 1] == "127.0.0.1:5555"
    assert "wm" in argv  # the command itself made it in after shlex.split
    assert "shell" not in seen["kwargs"]  # never a shell=True kwarg


def test_adb_binary_requests_bytes(monkeypatch):
    seen = _capture(monkeypatch)
    _make_controller().adb("exec-out screencap -p", binary_output=True)

    assert seen["kwargs"]["text"] is False


def test_adb_raises_not_ready_on_timeout(monkeypatch):
    def spy(argv, **kwargs):
        raise subprocess.TimeoutExpired(argv, 30)

    monkeypatch.setattr(adb_base, "run_command", spy)

    with pytest.raises(EmulatorNotReadyError, match="timed out"):
        _make_controller().adb("shell pm list packages")


def test_discover_devices_raises_on_timeout(monkeypatch):
    def spy(argv, **kwargs):
        raise subprocess.TimeoutExpired(argv, 15)

    monkeypatch.setattr(adb_base, "run_command", spy)

    with pytest.raises(EmulatorNotReadyError, match="adb devices"):
        AdbBasedController.discover_devices()
