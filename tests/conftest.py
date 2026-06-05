"""pytest fixtures shared by the integration suites (clash-royale + memu).

Offline tests never touch these fixtures, so a bare `pytest` run (the default
`-m "not emulator"`) never attaches to hardware. Only `@pytest.mark.emulator`
tests request the `emulator` fixture, which attaches to an already-running
emulator and aborts the whole session if it isn't parked on the Clash main menu.
"""

from __future__ import annotations

import pytest

from tests._emulator_support import attach_emulator, available_cli_choices, check_preconditions

# Default backend when an emulator test runs and no --emulator was passed.
# Preserves the old `EMULATOR=memu make test` ergonomics.
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
    """Attach to a live emulator and verify it's on the Clash main menu.

    Hard-aborts the session (pytest.exit) on a failed precondition — a
    misconfigured emulator is an operator setup error, and continuing would
    chain false negatives across the ordered suite.
    """
    cli_alias = request.config.getoption("--emulator") or _DEFAULT_EMULATOR

    emu = attach_emulator(cli_alias, logger)
    if emu is None:
        pytest.exit(f"ABORTING: could not attach to the {cli_alias} emulator", returncode=1)

    ok, msg = check_preconditions(emu, cli_alias)
    if not ok:
        pytest.exit(f"ABORTING: {msg}", returncode=1)

    return emu
