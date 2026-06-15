"""Offline coverage for ADB command construction (argv, no shell).

Pins that ``adb()`` and ``discover_devices()`` build proper argv lists and route
through the timeout helper with ``shell`` never involved, without any hardware.
The helper is monkeypatched to capture the argv and return a canned result.
"""

import subprocess

from pyclashbot.emulators import adb_base
from pyclashbot.emulators.adb_base import AdbBasedController


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


def test_adb_builds_device_scoped_argv(monkeypatch):
    seen = _capture(monkeypatch)
    _make_controller().adb("shell input tap 1 2")

    assert seen["argv"] == ["adb", "-s", "127.0.0.1:5555", "shell", "input", "tap", "1", "2"]
    assert "shell" not in seen["kwargs"]  # never a shell=True kwarg
    assert seen["kwargs"]["timeout"] == 30


def test_adb_includes_server_port(monkeypatch):
    seen = _capture(monkeypatch)
    _make_controller(adb_server_port=5037).adb("shell wm size")

    assert seen["argv"] == ["adb", "-P", "5037", "-s", "127.0.0.1:5555", "shell", "wm", "size"]


def test_adb_omits_serial_for_server_command(monkeypatch):
    seen = _capture(monkeypatch)
    _make_controller().adb("devices")

    assert seen["argv"] == ["adb", "devices"]


def test_adb_binary_output_requests_bytes(monkeypatch):
    seen = _capture(monkeypatch)
    _make_controller().adb("exec-out screencap -p", binary_output=True)

    assert seen["argv"] == ["adb", "-s", "127.0.0.1:5555", "exec-out", "screencap", "-p"]
    assert seen["kwargs"]["text"] is False


def test_discover_devices_builds_argv_and_parses(monkeypatch):
    stdout = "List of devices attached\n127.0.0.1:5555\tdevice\nemulator-5554\tdevice\n"
    seen = _capture(monkeypatch, stdout=stdout)

    devices = AdbBasedController.discover_devices()

    assert devices == ["127.0.0.1:5555", "emulator-5554"]
    assert seen["argv"][-1] == "devices"
    assert seen["argv"][0] == "adb"
