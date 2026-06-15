"""Shop daily free offer claim job.

Navigate to the Shop tab, scroll to find the free daily offer icon, click it,
confirm the collect, dismiss, then return to main.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING

from pyclashbot.bot.coords import (
    CONFIRM_COLLECT_DAILY_FREE_OFFER_BUTTON_COORDS,
    PAGINATE_SHOP_PAGE_BUTTON,
    SHOP_PAGE_DEADSPACE_COORD,
)
from pyclashbot.bot.find import locate_free_shop_offer_icon
from pyclashbot.bot.nav import (
    PAGE_MAIN,
    PAGE_SHOP,
    navigate_main_page,
)
from pyclashbot.bot.state_detect import (
    check_if_on_clash_main_menu,
    check_if_on_shop,
)

if TYPE_CHECKING:
    from pyclashbot.utils.logger import Logger

MAX_PAGINATE_ITERATIONS = 8


def _paginate_shop(emulator) -> None:
    emulator.click(*PAGINATE_SHOP_PAGE_BUTTON)
    time.sleep(1)


def shop_daily_state(emulator, logger: Logger) -> bool:
    logger.change_status("Collecting daily free shop offer...")

    if not check_if_on_clash_main_menu(emulator):
        logger.change_status("Not on main menu — cannot run shop daily offer")
        return False

    if not navigate_main_page(emulator, logger, PAGE_MAIN, PAGE_SHOP):
        logger.change_status("Failed to navigate to shop page")
        return False

    if not check_if_on_shop(emulator):
        logger.change_status("Did not land on shop page")
        return False

    found = None
    for _ in range(MAX_PAGINATE_ITERATIONS):
        coord = locate_free_shop_offer_icon(emulator)
        if coord is not None:
            found = coord
            break
        _paginate_shop(emulator)

    if found is None:
        logger.change_status("Daily free shop offer not found — returning to main menu")
        return navigate_main_page(emulator, logger, PAGE_SHOP, PAGE_MAIN)

    logger.change_status(f"Found daily free offer at {found}, claiming...")
    emulator.click(*found)
    time.sleep(2)

    emulator.click(*CONFIRM_COLLECT_DAILY_FREE_OFFER_BUTTON_COORDS)
    time.sleep(2)

    emulator.click(*SHOP_PAGE_DEADSPACE_COORD)
    time.sleep(1)

    return navigate_main_page(emulator, logger, PAGE_SHOP, PAGE_MAIN)
