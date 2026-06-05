"""Test: switch_account_state round-trip.

Begins on main on account slot 1, switches to slot 2, then switches back
to slot 1, ends on main. The round-trip means the rest of the test suite
always runs against the same account, even if a switch happened mid-flow.

Precondition: MEmu VM running, signed in to Clash Royale, on the main menu,
at least 2 accounts available, currently on slot 1.

Run via tests/clash-royale/test_all_clash.py.
"""

from __future__ import annotations

from pyclashbot.bot.account_switch import switch_account_state
from pyclashbot.bot.nav import wait_for_clash_main_menu


def run_test(emulator, logger) -> tuple[bool, str]:
    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't begin on clash main")

    if not switch_account_state(emulator, logger, 2):
        return (False, "Failed during switch_account_state(target_slot=2)")
    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't reach clash main after switch to slot 2")

    if not switch_account_state(emulator, logger, 1):
        return (False, "Failed during switch_account_state(target_slot=1) (return)")
    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't end on clash main")

    return (True, "")
