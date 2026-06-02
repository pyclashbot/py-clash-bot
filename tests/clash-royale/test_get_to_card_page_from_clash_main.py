"""Nav test #10: get_to_card_page_from_clash_main.

Precondition: MEmu VM `pyclashbot-136` running, signed in, on main menu.

Flow:
  1. Wait for main.
  2. Call get_to_card_page_from_clash_main(); assert return == "good".
  3. Confirm with check_if_on_card_page() == True.
  4. Finally: return to main.
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


def test_get_to_card_page_from_clash_main() -> None:
    logger = Logger()
    emu = MemuEmulatorController(logger, debug_mode=True)

    assert wait_for_clash_main_menu(emu, logger), "precondition: never reached main menu"

    try:
        result = get_to_card_page_from_clash_main(emu, logger)
        print(f"[+] get_to_card_page_from_clash_main returned: {result!r}")
        assert result == "good", f"expected 'good', got {result!r}"

        assert check_if_on_card_page(emu) is True, "after navigation, check_if_on_card_page should be True"
        print("[+] confirmed on card page")

    finally:
        return_to_clash_main_from_card_page(emu, logger)


if __name__ == "__main__":
    try:
        test_get_to_card_page_from_clash_main()
    except AssertionError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    print("PASS")
