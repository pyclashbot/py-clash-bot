"""Harness: which_war_decks_exist — assumes emulator on war page."""

from __future__ import annotations

import sys

from pyclashbot.bot.state_detect import which_war_decks_exist
from pyclashbot.emulators.memu import MemuEmulatorController
from pyclashbot.utils.logger import Logger

EXPECTED = {"deck1": False, "deck2": False, "deck3": True, "deck4": False}


def test_which_war_decks_exist() -> None:
    emu = MemuEmulatorController(Logger(), debug_mode=True)
    result = which_war_decks_exist(emu)
    print(f"which_war_decks_exist -> {result}")
    assert result == EXPECTED, f"expected {EXPECTED}, got {result}"


if __name__ == "__main__":
    try:
        test_which_war_decks_exist()
    except AssertionError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    print("PASS")
