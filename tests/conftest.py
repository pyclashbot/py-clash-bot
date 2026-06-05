"""Shared fixtures for the emulator integration suites."""

from __future__ import annotations

import pytest

from tests._emulator_support import attach_emulator, available_cli_choices, check_preconditions

# Preserves the old `EMULATOR=memu make test` default.
_DEFAULT_EMULATOR = "memu"


def _emulator_choices() -> list[str]:
    try:
        choices = available_cli_choices()
    except Exception:
        choices = []
    # Fall back to the full alias list if the registry can't be probed; the
    # attach step will fail with a more specific error.
    return choices or ["memu", "bluestacks", "google-play", "adb"]


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--emulator",
        action="store",
        default=None,
        choices=_emulator_choices(),
        help="Emulator backend to attach to for @pytest.mark.emulator tests. "
        "Must already be running on the Clash Royale main menu. Defaults to 'memu'.",
    )


@pytest.fixture(scope="session")
def logger():
    from pyclashbot.utils.logger import Logger

    return Logger()


@pytest.fixture(scope="session")
def emulator(request: pytest.FixtureRequest, logger):
    # Hard-abort (pytest.exit, not skip) on a bad precondition — continuing
    # would chain false negatives across the ordered suite.
    cli_alias = request.config.getoption("--emulator") or _DEFAULT_EMULATOR

    emu = attach_emulator(cli_alias, logger)
    if emu is None:
        pytest.exit(f"ABORTING: could not attach to the {cli_alias} emulator", returncode=1)

    ok, msg = check_preconditions(emu, cli_alias)
    if not ok:
        pytest.exit(f"ABORTING: {msg}", returncode=1)

    return emu
