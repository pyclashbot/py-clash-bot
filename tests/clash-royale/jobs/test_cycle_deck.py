"""Test: select_deck_state (deck cycling).

Begins on main, selects deck 1 of a 10-deck cycle, ends on main. Asserts the
returned selected_deck_number is sane (in range 1..deck_count).

Precondition: MEmu VM running, signed in to Clash Royale, on the main menu.

Run directly:
    py tests/clash-royale/jobs/test_cycle_deck.py
"""

from __future__ import annotations

from pyclashbot.bot.deck import select_deck_state
from pyclashbot.bot.nav import wait_for_clash_main_menu

DECK_CYCLE_INDEX = 1
DECK_COUNT = 10


def run_test(emulator, logger) -> tuple[bool, str]:
    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't begin on clash main")

    success, selected_deck_number = select_deck_state(emulator, logger, DECK_CYCLE_INDEX, DECK_COUNT)
    if not success or selected_deck_number is None:
        return (False, f"Failed during select_deck_state(index={DECK_CYCLE_INDEX}, count={DECK_COUNT})")
    if not (1 <= selected_deck_number <= DECK_COUNT):
        return (
            False,
            f"Failed during select_deck_state: selected_deck_number={selected_deck_number} out of range 1..{DECK_COUNT}",
        )

    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't end on clash main")

    return (True, "")
