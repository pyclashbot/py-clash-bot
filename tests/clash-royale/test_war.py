"""Harness: full war_state — assumes emulator is on the clash main menu."""

from __future__ import annotations

import sys

from pyclashbot.bot.state_detect import check_if_on_clash_main_menu
from pyclashbot.bot.war import war_state
from pyclashbot.emulators.memu import MemuEmulatorController
from pyclashbot.utils.logger import Logger


def test_war_state() -> None:
    logger = Logger()
    emu = MemuEmulatorController(logger, debug_mode=True)

    assert check_if_on_clash_main_menu(emu), "precondition: must start on main menu"

    result = war_state(emu, logger)
    print(f"war_state -> {result}")
    assert result is True, "expected war_state to succeed"
    assert check_if_on_clash_main_menu(emu), "expected to land back on main"


if __name__ == "__main__":
    try:
        test_war_state()
    except AssertionError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    print("PASS")
