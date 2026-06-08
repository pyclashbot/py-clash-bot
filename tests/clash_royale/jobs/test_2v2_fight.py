"""Test: end-to-end Classic 2v2 fight.

Begins on main, runs the full fight chain (start_fight -> do_fight_state ->
end_fight_state) for Classic 2v2, ends on main.

Precondition: MEmu VM running, signed in to Clash Royale, on the main menu.
Patience: a real 2v2 match takes minutes (and depends on matchmaking).
"""

from __future__ import annotations

from pyclashbot.bot.fight import do_fight_state, end_fight_state, start_fight
from pyclashbot.bot.nav import wait_for_clash_main_menu

MODE = "Classic 2v2"


def run_test(emulator, logger) -> tuple[bool, str]:
    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't begin on clash main")

    if start_fight(emulator, logger, MODE) is False:
        return (False, f"Failed during start_fight({MODE!r})")

    if do_fight_state(emulator, logger, False, MODE, False, False) is False:
        return (False, f"Failed during do_fight_state({MODE!r})")

    if end_fight_state(emulator, logger, False, False) is False:
        return (False, "Failed during end_fight_state")

    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't end on clash main")

    return (True, "")
