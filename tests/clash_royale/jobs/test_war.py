"""Test: war_state.

Begins on main, runs the clan war flow, ends on main. Requires an active clan
war with a deck ready to battle.

Precondition: MEmu VM running, signed in to Clash Royale, on the main menu.

Run directly:
    py tests/clash_royale/jobs/test_war.py
"""

from __future__ import annotations

from pyclashbot.bot.nav import wait_for_clash_main_menu
from pyclashbot.bot.war import war_state


def run_test(emulator, logger) -> tuple[bool, str]:
    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't begin on clash main")

    if war_state(emulator, logger) is False:
        return (False, "Failed during war_state")

    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't end on clash main")

    return (True, "")
