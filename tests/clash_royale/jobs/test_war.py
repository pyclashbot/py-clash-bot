"""Test: war_state full flow.

Begins on main, runs war_state (main -> war -> fill decks -> find+start battle ->
play -> exit -> main), ends on main. The "no more war battles available" branch
is a valid success path.

Precondition: MEmu VM running, signed in to Clash Royale, in a clan that has the
War tab visible, on main.
"""

from __future__ import annotations

from pyclashbot.bot.nav import wait_for_clash_main_menu
from pyclashbot.bot.war import war_state


def run_test(emulator, logger) -> tuple[bool, str]:
    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't begin on clash main")

    if not war_state(emulator, logger):
        return (False, "Failed during war_state")

    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't end on clash main")

    return (True, "")
