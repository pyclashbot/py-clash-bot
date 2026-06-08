"""Test: randomize_deck_state.

Begins on main, randomizes deck 2, ends on main.

Precondition: MEmu VM running, signed in to Clash Royale, on the main menu.
"""

from __future__ import annotations

from pyclashbot.bot.deck import randomize_deck_state
from pyclashbot.bot.nav import wait_for_clash_main_menu

DECK_NUMBER = 2


def run_test(emulator, logger) -> tuple[bool, str]:
    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't begin on clash main")

    if randomize_deck_state(emulator, logger, DECK_NUMBER) is False:
        return (False, f"Failed during randomize_deck_state(deck_number={DECK_NUMBER})")

    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't end on clash main")

    return (True, "")
