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
    read_cache,
    resolve_backend,
    resolve_serial,
    write_cache,
)

_BACKEND_KEY = pytest.StashKey[str]()
_SERIAL_KEY = pytest.StashKey[object]()


def _emulator_choices() -> list[str]:
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
        choices=_emulator_choices(),
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
    and resume immediately — never on the cache/arg path, which avoids leaving
    capture in a state that breaks pytest's own teardown reporting.
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

    # Flip the default deselection; read lazily at collection, so setting it here works.
    config.option.markexpr = "emulator"

    # No GUI/human here: controllers must fail fast on a not-ready emulator instead
    # of waiting forever on a "Retry" prompt.
    os.environ["PYCLASHBOT_NONINTERACTIVE"] = "1"

    choices = available_cli_choices()
    cache = read_cache()

    backend, persist_backend = resolve_backend(
        config.getoption("--emulator"),
        cache,
        config.getini("emulator_default"),
        choices,
        _make_interactive_menu(config),
    )
    serial, persist_serial = resolve_serial(config.getoption("--adb-serial"), cache)

    updates: dict = {}
    if persist_backend:
        updates["emulator"] = backend
    if persist_serial:
        updates["adb_serial"] = serial
    if updates:
        write_cache(updates)

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
    # false negatives across the ordered suite. Controllers boot + launch Clash in
    # construction, so "not set up" surfaces here rather than as a per-test failure.
    try:
        emu = attach_emulator(backend, logger, device_serial=serial)
    except EmulatorNotReadyError as e:
        pytest.exit(f"ABORTING: {backend} emulator is not ready: {e}", returncode=1)
    if emu is None:
        pytest.exit(f"ABORTING: could not attach to the {backend} emulator", returncode=1)

    return emu
