"""Unit tests for pyclashbot.utils.platform (no emulator required).

Run directly:
    uv run python tests/unit/test_platform.py

Or via the test runner:
    uv run python scripts/run_tests.py
"""

from __future__ import annotations

import os
import sys
from unittest.mock import patch

from pyclashbot.utils.platform import (
    Platform,
    get_app_data_dir,
    get_log_dir,
    get_platform,
    is_linux,
    is_macos,
    is_windows,
)

APP_NAME = "py-clash-bot"


def test_get_platform_darwin() -> None:
    with patch.object(sys, "platform", "darwin"):
        assert get_platform() == Platform.MACOS


def test_get_platform_linux() -> None:
    with patch.object(sys, "platform", "linux"):
        assert get_platform() == Platform.LINUX


def test_get_platform_windows() -> None:
    with patch.object(sys, "platform", "win32"):
        assert get_platform() == Platform.WINDOWS


def test_platform_predicates() -> None:
    with patch.object(sys, "platform", "darwin"):
        assert is_macos() is True
        assert is_windows() is False
        assert is_linux() is False

    with patch.object(sys, "platform", "win32"):
        assert is_windows() is True
        assert is_macos() is False

    with patch.object(sys, "platform", "linux"):
        assert is_linux() is True
        assert is_macos() is False


def test_get_app_data_dir_macos() -> None:
    with patch.object(sys, "platform", "darwin"):
        expected = os.path.join(os.path.expanduser("~/Library/Application Support"), APP_NAME)
        assert get_app_data_dir(APP_NAME) == expected


def test_get_app_data_dir_linux_default_xdg() -> None:
    with patch.object(sys, "platform", "linux"):
        env = {k: v for k, v in os.environ.items() if k != "XDG_DATA_HOME"}
        with patch.dict(os.environ, env, clear=True):
            expected = os.path.join(os.path.expanduser("~/.local/share"), APP_NAME)
            assert get_app_data_dir(APP_NAME) == expected


def test_get_app_data_dir_linux_custom_xdg() -> None:
    with patch.object(sys, "platform", "linux"):
        with patch.dict(os.environ, {"XDG_DATA_HOME": "/custom/data"}, clear=False):
            assert get_app_data_dir(APP_NAME) == os.path.join("/custom/data", APP_NAME)


def test_get_app_data_dir_windows() -> None:
    with patch.object(sys, "platform", "win32"):
        with patch.dict(os.environ, {"APPDATA": r"C:\Users\test\AppData\Roaming"}, clear=False):
            assert get_app_data_dir(APP_NAME) == os.path.join(r"C:\Users\test\AppData\Roaming", APP_NAME)


def test_get_log_dir_macos() -> None:
    with patch.object(sys, "platform", "darwin"):
        expected = os.path.join(os.path.expanduser("~/Library/Logs"), APP_NAME)
        assert get_log_dir(APP_NAME) == expected


def test_get_log_dir_linux_default_xdg() -> None:
    with patch.object(sys, "platform", "linux"):
        env = {k: v for k, v in os.environ.items() if k != "XDG_STATE_HOME"}
        with patch.dict(os.environ, env, clear=True):
            expected = os.path.join(os.path.expanduser("~/.local/state"), APP_NAME, "logs")
            assert get_log_dir(APP_NAME) == expected


def test_get_log_dir_windows() -> None:
    with patch.object(sys, "platform", "win32"):
        with patch.dict(os.environ, {"APPDATA": r"C:\Users\test\AppData\Roaming"}, clear=False):
            expected = os.path.join(r"C:\Users\test\AppData\Roaming", APP_NAME, "logs")
            assert get_log_dir(APP_NAME) == expected


def run_all() -> None:
    tests = [
        test_get_platform_darwin,
        test_get_platform_linux,
        test_get_platform_windows,
        test_platform_predicates,
        test_get_app_data_dir_macos,
        test_get_app_data_dir_linux_default_xdg,
        test_get_app_data_dir_linux_custom_xdg,
        test_get_app_data_dir_windows,
        test_get_log_dir_macos,
        test_get_log_dir_linux_default_xdg,
        test_get_log_dir_windows,
    ]
    for test_fn in tests:
        print(f"[+] {test_fn.__name__}")
        test_fn()


if __name__ == "__main__":
    try:
        run_all()
    except AssertionError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    print("PASS")
