"""Test: card_mastery_state.

Begins on main, runs the card-mastery collection flow, ends on main. A no-op
(no mastery rewards available) is still a pass — the function returning True
means it navigated cleanly.

Precondition: MEmu VM running, signed in to Clash Royale, on the main menu.

Run directly:
    py tests/clash-royale/jobs/test_card_mastery.py
"""

from __future__ import annotations

from pyclashbot.bot.card_mastery_state import card_mastery_state
from pyclashbot.bot.nav import wait_for_clash_main_menu


def run_test(emulator, logger) -> tuple[bool, str]:
    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't begin on clash main")

    if card_mastery_state(emulator, logger) is False:
        return (False, "Failed during card_mastery_state")

    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't end on clash main")

    return (True, "")
