import time

from pyclashbot.bot.coords import (
    CONFIRM_UPGRADE_PRINCESS_BUTTON_COORD,
    DEADSPACE_COORD,
    PRINCESS_CARD_BUTTON_COORD,
    PRINCESS_CARD_PAGE_OK_BUTTON_COORD,
    PRINCESS_INFO_BUTTON_COORD_LOCATION_1,
    PRINCESS_UPGRADE_BUTTON_COORD_LOCATION_1,
    PRINCESS_UPGRADE_BUTTON_COORD_LOCATION_2,
    UPGRADE_PRINCESS_BUTTON_2_COORD,
)
from pyclashbot.bot.nav import (
    get_to_card_page_from_clash_main,
    return_to_clash_main_from_card_page,
)
from pyclashbot.bot.state_detect import (
    check_for_princess_card_info_button_location_1,
    check_for_princess_card_info_button_location_2,
    check_for_princess_card_info_button_location_3,
    check_for_princess_upgrade_location_1,
    check_for_princess_upgrade_location_2,
    check_if_on_clash_main_menu,
)
from pyclashbot.utils.logger import Logger


def upgrade_princess_state(emulator, logger: Logger) -> bool:
    """WIP princess-upgrade state: main → card page → open princess → info/upgrade → main."""
    logger.change_status(status="[PRINCESS] Starting princess upgrade state")

    logger.log("[PRINCESS] Verifying we are on the clash main menu")
    if not check_if_on_clash_main_menu(emulator):
        logger.change_status("[PRINCESS] Not on main menu — cannot upgrade princess")
        return False
    logger.log("[PRINCESS] Confirmed on main menu")

    logger.change_status("[PRINCESS] Navigating to card page from main menu")
    if get_to_card_page_from_clash_main(emulator, logger) == "restart":
        logger.change_status("[PRINCESS] Failed to open card page from main menu")
        return False
    logger.log("[PRINCESS] Reached the card page")

    logger.change_status(f"[PRINCESS] Clicking princess card at {PRINCESS_CARD_BUTTON_COORD}")
    emulator.click(*PRINCESS_CARD_BUTTON_COORD)
    logger.log("[PRINCESS] Waiting 2s for the princess card overlay to open")
    time.sleep(2)

    # Detect which of the four overlays is showing.
    logger.log("[PRINCESS] Running button detections (info L1/L2, upgrade L1/L2)")
    info_1 = check_for_princess_card_info_button_location_1(emulator)
    info_2 = check_for_princess_card_info_button_location_2(emulator)
    info_3 = check_for_princess_card_info_button_location_3(emulator)
    logger.log(
        f"[PRINCESS] info location #1 = {info_1}, #2 = {info_2}, #3 = {info_3}",
    )

    # Info button (any spot) -> dismiss it and head back to main.
    if info_1 or info_2 or info_3:
        which = "#1" if info_1 else "#2" if info_2 else "#3"
        logger.change_status(f"[PRINCESS] Info button detected at location {which}")
        logger.change_status(
            f"[PRINCESS] Clicking card page OK button at {PRINCESS_INFO_BUTTON_COORD_LOCATION_1}",
        )
        emulator.click(*PRINCESS_INFO_BUTTON_COORD_LOCATION_1)
        logger.log("[PRINCESS] Waiting 2s after dismissing info button")
        time.sleep(2)

        logger.change_status("[PRINCESS] Returning to main menu from card page")
        if not return_to_clash_main_from_card_page(emulator, logger):
            logger.change_status("[PRINCESS] Failed to return to main menu after info dismiss")
            return False
        logger.change_status("[PRINCESS] Done (info path) — back on main menu")
        return True

    # Upgrade button (either location) -> single location-dependent click.
    upgrade_1 = check_for_princess_upgrade_location_1(emulator)
    upgrade_2 = check_for_princess_upgrade_location_2(emulator)
    logger.log(f"[PRINCESS] upgrade location #1 = {upgrade_1}, upgrade location #2 = {upgrade_2}")

    if upgrade_1:
        upgrade_coord = PRINCESS_UPGRADE_BUTTON_COORD_LOCATION_1
        logger.change_status("[PRINCESS] Upgrade button detected at location #1")
    elif upgrade_2:
        upgrade_coord = PRINCESS_UPGRADE_BUTTON_COORD_LOCATION_2
        logger.change_status("[PRINCESS] Upgrade button detected at location #2")
    else:
        logger.change_status("[PRINCESS] Neither princess info nor upgrade button found — aborting")
        return False

    logger.change_status(f"[PRINCESS] Clicking upgrade button at {upgrade_coord}")
    emulator.click(*upgrade_coord)
    logger.log("[PRINCESS] Waiting 2s after first upgrade click")
    time.sleep(2)

    logger.change_status(
        f"[PRINCESS] Clicking second upgrade button at {UPGRADE_PRINCESS_BUTTON_2_COORD}",
    )
    emulator.click(*UPGRADE_PRINCESS_BUTTON_2_COORD)
    logger.log("[PRINCESS] Waiting 2s after second upgrade click")
    time.sleep(2)

    logger.change_status(
        f"[PRINCESS] Confirming upgrade at {CONFIRM_UPGRADE_PRINCESS_BUTTON_COORD}",
    )
    emulator.click(*CONFIRM_UPGRADE_PRINCESS_BUTTON_COORD)
    logger.log("[PRINCESS] Waiting 5s for the upgrade animation/confirmation")
    time.sleep(5)

    logger.change_status(f"[PRINCESS] Clicking deadspace at {DEADSPACE_COORD}")
    emulator.click(*DEADSPACE_COORD)
    logger.log("[PRINCESS] Waiting 5s after deadspace click")
    time.sleep(5)

    logger.change_status(
        f"[PRINCESS] Clicking card page OK button at {PRINCESS_CARD_PAGE_OK_BUTTON_COORD}",
    )
    emulator.click(*PRINCESS_CARD_PAGE_OK_BUTTON_COORD)
    logger.log("[PRINCESS] Waiting 3s after card page OK button before navigating to main")
    time.sleep(3)

    logger.change_status("[PRINCESS] Returning to main menu from card page")
    if not return_to_clash_main_from_card_page(emulator, logger):
        logger.change_status("[PRINCESS] Failed to return to main menu after upgrade")
        return False

    logger.change_status("[PRINCESS] Done (upgrade path) — back on main menu")
    return True


if __name__ == "__main__":
    pass
