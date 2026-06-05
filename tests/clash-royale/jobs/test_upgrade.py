"""Test: upgrade_cards_state.

Begins on main, runs the upgrade-cards flow, ends on main. A no-op upgrade
(no cards available to upgrade) is still a pass — the function returning True
means it navigated cleanly.

Precondition: MEmu VM running, signed in to Clash Royale, on the main menu.

Run directly:
    py tests/clash-royale/jobs/test_upgrade.py
"""

from __future__ import annotations

from pyclashbot.bot.nav import wait_for_clash_main_menu
from pyclashbot.bot.upgrade_state import upgrade_cards_state


def run_test(emulator, logger) -> tuple[bool, str]:
    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't begin on clash main")

    if upgrade_cards_state(emulator, logger) is False:
        return (False, "Failed during upgrade_cards_state")

    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't end on clash main")

    return (True, "")
