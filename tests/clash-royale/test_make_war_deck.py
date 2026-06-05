"""Harness: make_war_deck — assumes emulator on the war page with the slot empty."""

from __future__ import annotations

import sys

from pyclashbot.bot.war import make_war_deck
from pyclashbot.emulators.memu import MemuEmulatorController
from pyclashbot.utils.logger import Logger

DECK_INDEX = 1


def test_make_war_deck() -> None:
    logger = Logger()
    emu = MemuEmulatorController(logger, debug_mode=True)
    result = make_war_deck(emu, logger, DECK_INDEX)
    print(f"make_war_deck({DECK_INDEX}) -> {result}")
    assert result is True


if __name__ == "__main__":
    try:
        test_make_war_deck()
    except AssertionError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    print("PASS")
