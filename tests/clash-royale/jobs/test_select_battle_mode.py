"""Test: select_mode across all three battle modes.

Begins on main, selects each of Classic 1v1, Classic 2v2, and Trophy Road in
turn (verifying each is reported as selected before moving on), ends on main.

Note: select_mode() in nav.py doesn't currently call wait_for_clash_main_menu
on exit (see backlog: "Fix select_mode end-on-main contract"), so this test
adds its own wait between iterations.

Precondition: MEmu VM running, signed in to Clash Royale, on the main menu.

Run directly:
    py tests/clash-royale/jobs/test_select_battle_mode.py
"""

from __future__ import annotations

from pyclashbot.bot.nav import select_mode, wait_for_clash_main_menu
from pyclashbot.bot.state_detect import check_if_battle_mode_is_selected

MODES = ("Classic 1v1", "Classic 2v2", "Trophy Road")


def run_test(emulator, logger) -> tuple[bool, str]:
    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't begin on clash main")

    for mode in MODES:
        if select_mode(emulator, mode) is False:
            return (False, f"Failed during select_mode({mode!r})")
        if not wait_for_clash_main_menu(emulator, logger):
            return (False, f"Didn't return to clash main after select_mode({mode!r})")
        if not check_if_battle_mode_is_selected(emulator, mode):
            return (False, f"Failed during check_if_battle_mode_is_selected({mode!r})")

    if not wait_for_clash_main_menu(emulator, logger):
        return (False, "Didn't end on clash main")

    return (True, "")
