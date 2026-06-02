"""Nav test #11: check_if_on_card_page — positive + negative branches.

Precondition: MEmu VM `pyclashbot-136` running, signed in, on main menu.

Flow:
  1. Wait for main.
  2. Negative: check_if_on_card_page() -> False (we're at main).
  3. Navigate to card page.
  4. Positive: check_if_on_card_page() -> True.
  5. Finally: return to main.
"""

from __future__ import annotations

import sys

from pyclashbot.bot.nav import (
    check_if_on_card_page,
    get_to_card_page_from_clash_main,
    return_to_clash_main_from_card_page,
    wait_for_clash_main_menu,
)
from pyclashbot.emulators.memu import MemuEmulatorController
from pyclashbot.utils.logger import Logger


def test_check_if_on_card_page_both_branches() -> None:
    logger = Logger()
    emu = MemuEmulatorController(logger, debug_mode=True)

    assert wait_for_clash_main_menu(emu, logger), "precondition: never reached main menu"

    try:
        # negative
        assert check_if_on_card_page(emu) is False, "check_if_on_card_page should be False when on main menu"
        print("[+] negative: not detected on main")

        # navigate
        result = get_to_card_page_from_clash_main(emu, logger)
        assert result == "good", f"failed to reach card page (got {result!r})"

        # positive
        assert check_if_on_card_page(emu) is True, "check_if_on_card_page should be True when on card page"
        print("[+] positive: detected on card page")

    finally:
        return_to_clash_main_from_card_page(emu, logger)


if __name__ == "__main__":
    try:
        test_check_if_on_card_page_both_branches()
    except AssertionError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    print("PASS")
