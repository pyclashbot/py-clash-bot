"""Nav test #9: check_if_on_clash_main_menu — positive + negative branches.

Precondition: MEmu VM `pyclashbot-136` is running and signed in to Clash Royale,
sitting on the main menu (or close to it).

Flow:
  1. Wait for main.
  2. Positive: check_if_on_clash_main_menu() -> True.
  3. Navigate to card page.
  4. Negative: check_if_on_clash_main_menu() -> False.
  5. Finally: return to main via return_to_clash_main_from_card_page().
"""

from __future__ import annotations

import sys

from pyclashbot.bot.nav import (
    get_to_card_page_from_clash_main,
    return_to_clash_main_from_card_page,
    wait_for_clash_main_menu,
)
from pyclashbot.bot.state_detect import check_if_on_clash_main_menu
from pyclashbot.emulators.memu import MemuEmulatorController
from pyclashbot.utils.logger import Logger


def test_check_if_on_clash_main_menu_both_branches() -> None:
    logger = Logger()
    emu = MemuEmulatorController(logger, debug_mode=True)

    assert wait_for_clash_main_menu(emu, logger), "precondition: never reached main menu"

    try:
        # positive
        assert check_if_on_clash_main_menu(emu) is True, "check_if_on_clash_main_menu should be True when on main menu"
        print("[+] positive: detected main")

        # navigate off main
        result = get_to_card_page_from_clash_main(emu, logger)
        assert result == "good", f"failed to reach card page (got {result!r})"

        # negative
        assert check_if_on_clash_main_menu(emu) is False, (
            "check_if_on_clash_main_menu should be False when on card page"
        )
        print("[+] negative: not detected on card page")

    finally:
        return_to_clash_main_from_card_page(emu, logger)


if __name__ == "__main__":
    try:
        test_check_if_on_clash_main_menu_both_branches()
    except AssertionError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    print("PASS")
