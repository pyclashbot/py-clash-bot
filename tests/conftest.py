"""Shared fixtures for the emulator integration suites.

`--integration` turns the suite on: it flips the default `-m "not emulator"` to
`-m emulator` and resolves which backend to drive. Without it, a bare `pytest`
never constructs an emulator or prompts.
"""

from __future__ import annotations

import os
import sys

import pytest

from pyclashbot.emulators.base import EmulatorNotReadyError
from tests._emulator_support import (
    attach_emulator,
    available_cli_choices,
    prompt_backend_menu,
    resolve_backend,
    resolve_serial,
)

_BACKEND_KEY = pytest.StashKey[str]()
_SERIAL_KEY = pytest.StashKey[str | None]()


def _emulator_choices() -> list[str]:
    """Platform-available backend aliases, guarded so a failed registry probe
    can't throw out of a pytest hook."""
    try:
        choices = available_cli_choices()
    except Exception:
        choices = []
    # Fall back to the full alias list if the registry can't be probed; resolution
    # then fails with a more specific error.
    return choices or ["memu", "bluestacks", "google-play", "adb"]


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="Run the live-emulator suite: select a backend, boot it, drive Clash Royale.",
    )
    parser.addoption(
        "--emulator",
        action="store",
        default=None,
        # No argparse `choices=`: resolve_backend() is the single, unit-tested
        # validator (and gives a platform-aware error message).
        help="Emulator backend for the integration suite. One-off override (not persisted).",
    )
    parser.addoption(
        "--adb-serial",
        action="store",
        default=None,
        help="ADB device serial (host:port). Sticky: persisted for later runs.",
    )
    parser.addini(
        "emulator_default",
        type="string",
        default="memu",
        help="Backend used when no --emulator arg or cached choice applies.",
    )


def _make_interactive_menu(config: pytest.Config):
    """A menu callback that suspends capture only when actually invoked.

    pytest swaps sys.stdin for a non-tty stub under capture, so the menu needs the
    real stdin briefly. We suspend global capture (in_=True) just around the prompt
    and resume immediately — never on the cache/arg path.
    """

    def menu(choices: list[str]) -> str | None:
        capman = config.pluginmanager.getplugin("capturemanager")
        active = capman is not None and bool(capman.is_capturing())
        if active:
            capman.suspend_global_capture(in_=True)
        try:
            if not sys.stdin.isatty():
                return None
            return prompt_backend_menu(choices)
        finally:
            if active:
                capman.resume_global_capture()

    return menu


def pytest_configure(config: pytest.Config) -> None:
    if not config.getoption("--integration"):
        return

    # Flip the default deselection (read lazily at collection, so setting it here
    # works). Intentionally overwrites any user-supplied `-m` under --integration.
    config.option.markexpr = "emulator"

    # No GUI/human here: fail fast on a not-ready emulator instead of hanging on a
    # "Retry" prompt. Set for the whole run (dedicated integration run, never unset).
    # TRANSITIONAL — see is_noninteractive() in pyclashbot/emulators/base.py.
    os.environ["PYCLASHBOT_NONINTERACTIVE"] = "1"

    choices = _emulator_choices()
    # Prior picks persist across runs via pytest's own cache (.pytest_cache/);
    # the resolvers stay pure by taking a plain dict, so they're unit-tested
    # without a pytest Config. Inspect with `pytest --cache-show 'pyclashbot/*'`.
    cache = {
        "emulator": config.cache.get("pyclashbot/emulator", None),
        "adb_serial": config.cache.get("pyclashbot/adb_serial", None),
    }

    backend, persist_backend = resolve_backend(
        config.getoption("--emulator"),
        cache,
        config.getini("emulator_default"),
        choices,
        _make_interactive_menu(config),
    )
    serial, persist_serial = resolve_serial(config.getoption("--adb-serial"), cache)

    if persist_backend:
        config.cache.set("pyclashbot/emulator", backend)
    if persist_serial:
        config.cache.set("pyclashbot/adb_serial", serial)

    config.stash[_BACKEND_KEY] = backend
    config.stash[_SERIAL_KEY] = serial


@pytest.fixture(scope="session")
def logger():
    from pyclashbot.utils.logger import Logger

    return Logger()


@pytest.fixture(scope="session")
def emulator(request: pytest.FixtureRequest, logger):
    backend = request.config.stash[_BACKEND_KEY]
    serial = request.config.stash[_SERIAL_KEY]

    # Hard-abort (pytest.exit, not skip): a missing/not-ready emulator would chain
    # false negatives across the ordered suite. attach_emulator constructs the
    # controller then boots it via restart(), so "not set up" surfaces here rather
    # than as a per-test failure.
    try:
        emu = attach_emulator(backend, logger, device_serial=serial)
    except EmulatorNotReadyError as e:
        pytest.exit(f"ABORTING: {backend} emulator is not ready: {e}", returncode=1)
    if emu is None:
        pytest.exit(f"ABORTING: could not attach to the {backend} emulator", returncode=1)

    return emu
