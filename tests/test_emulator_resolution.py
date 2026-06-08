"""Offline unit tests for backend/serial resolution (runs under `make test`).

Pure functions, no emulator: fakes for cache / isatty / choices / menu callback.
"""

from __future__ import annotations

import pytest

from tests._emulator_support import resolve_backend, resolve_serial

CHOICES = ["bluestacks", "adb"]  # a macOS-shaped available set


def _never_called(choices):
    raise AssertionError("interactive menu should not be invoked")


def _picks(value):
    # A menu callback that returns `value` (None models a non-tty / aborted prompt).
    return lambda choices: value


# --- resolve_backend: precedence ---------------------------------------------


def test_arg_wins_and_does_not_persist():
    backend, persist = resolve_backend("adb", {"emulator": "bluestacks"}, "bluestacks", CHOICES, _never_called)
    assert (backend, persist) == ("adb", False)


def test_cache_beats_ini_default():
    backend, persist = resolve_backend(None, {"emulator": "adb"}, "bluestacks", CHOICES, _never_called)
    assert (backend, persist) == ("adb", False)


def test_ini_default_used_when_no_arg_or_cache():
    backend, persist = resolve_backend(None, {}, "bluestacks", CHOICES, _never_called)
    assert (backend, persist) == ("bluestacks", False)


def test_menu_used_last_and_persists():
    backend, persist = resolve_backend(None, {}, "memu", CHOICES, _picks("adb"))
    assert (backend, persist) == ("adb", True)


# --- resolve_backend: platform gating ----------------------------------------


def test_unsupported_arg_is_hard_error():
    with pytest.raises(pytest.UsageError):
        resolve_backend("memu", {}, "bluestacks", CHOICES, _never_called)


def test_unsupported_cache_is_skipped():
    # "memu" cache (copied from a Windows box) is skipped; ini default wins.
    backend, persist = resolve_backend(None, {"emulator": "memu"}, "adb", CHOICES, _never_called)
    assert (backend, persist) == ("adb", False)


def test_unsupported_ini_default_falls_through_to_menu():
    backend, persist = resolve_backend(None, {}, "memu", CHOICES, _picks("bluestacks"))
    assert (backend, persist) == ("bluestacks", True)


def test_unresolvable_with_no_menu_pick_raises():
    # Non-tty / aborted menu -> callback returns None -> hard error, no hang.
    with pytest.raises(pytest.UsageError):
        resolve_backend(None, {}, "memu", CHOICES, _picks(None))


# --- resolve_serial -----------------------------------------------------------


def test_serial_arg_is_sticky():
    serial, persist = resolve_serial("127.0.0.1:5555", {})
    assert (serial, persist) == ("127.0.0.1:5555", True)


def test_serial_falls_back_to_cache_without_persisting():
    serial, persist = resolve_serial(None, {"adb_serial": "emulator-5554"})
    assert (serial, persist) == ("emulator-5554", False)


def test_serial_none_when_absent_everywhere():
    serial, persist = resolve_serial(None, {})
    assert (serial, persist) == (None, False)


def test_invalid_serial_arg_raises():
    with pytest.raises(pytest.UsageError):
        resolve_serial("bad serial!!", {})
