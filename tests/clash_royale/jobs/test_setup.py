"""Setup-as-test: confirm Clash Royale is installed before the job suite runs.

Booting + reaching the main menu happens in controller construction (the fixture
aborts cleanly if it can't), so this only guards the install precondition.
"""

from __future__ import annotations

from pyclashbot.emulators.base import CLASH_ROYALE_PACKAGE


def run_app_installed(emulator, logger) -> tuple[bool, str]:
    # Never calls start_app — that would block on the install-wait prompt loop.
    if not emulator.is_app_installed(CLASH_ROYALE_PACKAGE):
        return (False, f"{CLASH_ROYALE_PACKAGE} is not installed on the emulator")
    return (True, "")
