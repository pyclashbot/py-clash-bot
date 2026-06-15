import time

from pyclashbot.bot.coords import (
    CARD_UPGRADE_MENU_BGR,
    CARD_UPGRADE_MENU_COORD,
    CLOSE_CARD_PAGE_COORD,
    COIN_INSUFFICIENT_BGR,
    COIN_INSUFFICIENT_COORD,
    DEADSPACE_COORD,
    FIRST_UPGRADE_BUTTON_COORD,
    SECOND_UPGRADE_BUTTON_COORD,
    UPGRADE_PIXEL_TOLERANCE,
    UPGRADE_POINTS,
    UPGRADE_RETURN_TO_MAIN_COORD_1,
    UPGRADE_RETURN_TO_MAIN_COORD_2,
)
from pyclashbot.bot.find import detect_upgradable_cards
from pyclashbot.bot.nav import (
    get_to_card_page_from_clash_main,
    select_mode,
    wait_for_clash_main_menu,
)
from pyclashbot.bot.state_detect import check_if_on_clash_main_menu
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.utils.logger import Logger


def upgrade_card(emulator, upgradable, logger: Logger):
    """Upgrades a card if it is upgradable.

    Args:
    ----
        emulator (int): The index of the virtual machine to perform the upgrade on.
        logger (Logger): The logger object to use for logging.
        index (int): The index of the card to upgrade.
        upgrade_list (list[bool]): A list of bool values indicating whether each card is upgradable.

    Returns:
    -------
        None

    """
    print("\n")

    logger.change_status(status="Scrolling to top before starting upgrades")

    if not upgradable:
        logger.change_status(status="No upgradable cards found")
        return False

    logger.change_status(status=f"Upgradable cards: {' '.join(map(str, upgradable))}")

    upgraded_a_card = False

    for card_index in upgradable:
        # Found at nav.py scroll_down
        start_y = 200
        end_y = 400
        x = 10
        emulator.swipe(x, start_y, x, end_y)
        time.sleep(3)

        x, y = UPGRADE_POINTS[card_index - 1]

        logger.change_status(status=f"Upgrading card index: {card_index}")

        # First click (card upgrade emoji)
        emulator.click(x, y)
        time.sleep(2)

        # Click again(click the green upgrade emoji to open the upgrade bar)
        emulator.click(x + 15, y - 15)
        logger.change_status(status="Clicking the upgrade button for this card")
        time.sleep(2)

        img = emulator.screenshot()
        pixel = img[CARD_UPGRADE_MENU_COORD[1]][CARD_UPGRADE_MENU_COORD[0]]
        if not pixel_is_equal(pixel, CARD_UPGRADE_MENU_BGR, UPGRADE_PIXEL_TOLERANCE):
            logger.log("Card upgrade menu did not open, skipping to next card")
            logger.change_status(status="Clicking deadspace after attempting to upgrade this card")

            # just reduced iteration count
            for i in range(3):
                emulator.click(DEADSPACE_COORD[0], DEADSPACE_COORD[1])
                time.sleep(1)

            continue  # Skip

        logger.log("On card upgrade menu")
        logger.change_status(status="On card upgrade menu")

        emulator.click(FIRST_UPGRADE_BUTTON_COORD[0], FIRST_UPGRADE_BUTTON_COORD[1])
        logger.change_status(status="Clicking the first upgrade button for this card")
        time.sleep(2)

        # COIN check
        img = emulator.screenshot()
        pixel = img[COIN_INSUFFICIENT_COORD[1]][COIN_INSUFFICIENT_COORD[0]]
        if pixel_is_equal(pixel, COIN_INSUFFICIENT_BGR, UPGRADE_PIXEL_TOLERANCE):
            logger.log("Cannot upgrade this card: not enough coins")
            logger.change_status(status="Not enough coins — skipping card")

        else:
            logger.log("Upgraded a card!")
            upgraded_a_card = True
            prev_card_upgrades = logger.get_card_upgrades()
            logger.add_card_upgraded()
            card_upgrades = logger.get_card_upgrades()
            logger.log(
                f"Incremented cards upgraded from {prev_card_upgrades} to {card_upgrades}",
            )

        time.sleep(2)

        emulator.click(SECOND_UPGRADE_BUTTON_COORD[0], SECOND_UPGRADE_BUTTON_COORD[1])
        logger.change_status(status="Clicking the second upgrade button for this card")
        time.sleep(2)
        logger.change_status(status="Upgraded a card!")

        # Check for card upgrade menu close button
        img = emulator.screenshot()
        pixel = img[CARD_UPGRADE_MENU_COORD[1]][CARD_UPGRADE_MENU_COORD[0]]
        if pixel_is_equal(pixel, CARD_UPGRADE_MENU_BGR, UPGRADE_PIXEL_TOLERANCE):
            emulator.click(CLOSE_CARD_PAGE_COORD[0], CLOSE_CARD_PAGE_COORD[1])
            time.sleep(2)

        # Deadspace Clicks
        # just reduced iteration count
        for i in range(3):
            emulator.click(DEADSPACE_COORD[0], DEADSPACE_COORD[1])
            logger.change_status(status="Clicking deadspace after attempting to upgrade this card")
            time.sleep(1)

    return upgraded_a_card


def upgrade_cards_state(emulator, logger: Logger):
    logger.change_status(status="Upgrading cards")

    # if not on clash main, return restart
    print("Making sure on clash main before upgrading cards")

    if not check_if_on_clash_main_menu(emulator):
        logger.change_status("Not on main menu — cannot upgrade cards")
        return False

    if not select_mode(emulator, "Trophy Road", logger):
        logger.change_status("Failed to select Trophy Road mode")
        return False

    # get to card page
    logger.change_status(status="Getting to card page")
    if get_to_card_page_from_clash_main(emulator, logger) == "restart":
        logger.change_status(
            status="Failed to open card page from main menu",
        )
        return False

    # Determine upgradable cards
    upgradable = detect_upgradable_cards(emulator)

    # Start upgrading if there are upgradable cards
    upgraded = upgrade_card(emulator, upgradable, logger)
    if not upgraded:
        logger.change_status("No cards were upgraded because none were upgradable")

    # Return main menu
    logger.change_status(status="Done upgrading cards")

    emulator.click(UPGRADE_RETURN_TO_MAIN_COORD_1[0], UPGRADE_RETURN_TO_MAIN_COORD_1[1])
    time.sleep(1)
    emulator.click(UPGRADE_RETURN_TO_MAIN_COORD_2[0], UPGRADE_RETURN_TO_MAIN_COORD_2[1])
    time.sleep(2)

    if not wait_for_clash_main_menu(emulator, logger, deadspace_click=False):
        logger.change_status("Timed out waiting for main menu after upgrading cards")
        return False

    logger.update_time_of_last_card_upgrade(time.time())
    return True


if __name__ == "__main__":
    pass
