import time

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
    select_mode,
    wait_for_clash_main_menu,
)
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.utils.cancellation import interruptible_sleep
from pyclashbot.utils.logger import Logger


# Pixel criteria to detect upgrade emoji
def pixel_indicates_upgradable(bgr):
    b, g, r = bgr
    return g >= 240 and b <= 120 and r <= 40


# This indicates the green upgrade emoji. If we click it twice, the card upgrade menu will be opened.
UPGRADE_POINTS = [
    (53, 263),  # 1
    (140, 263),  # 2
    (225, 263),  # 3
    (312, 263),  # 4
    (52, 403),  # 5
    (139, 402),  # 6
    (225, 402),  # 7
    (311, 402),  # 8
]

FIRST_UPGRADE_BUTTON_COORD = (241, 542)
SECOND_UPGRADE_BUTTON_COORD = (241, 478)
DEADSPACE_COORD = (10, 323)
CLOSE_CARD_PAGE_COORD = (355, 238)

PIXEL_TOLERANCE = 30  # tol

COIN_INSUFFICIENT_COORD = (359, 210)  #  Cord of the close button of gold popup
COIN_INSUFFICIENT_BGR = (49, 53, 254)

CARD_UPGRADE_MENU_COORD = (346, 185)  #  Cord of the close button of card upgrade menu
CARD_UPGRADE_MENU_BGR = (69, 69, 253)


def detect_upgradable_cards(emulator):
    img = emulator.screenshot()
    upgradable = []  # it will be garbage collected right?

    for i, (x, y) in enumerate(UPGRADE_POINTS, start=1):
        if pixel_indicates_upgradable(img[y][x]):
            upgradable.append(i)

    return upgradable


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
        interruptible_sleep(3)

        x, y = UPGRADE_POINTS[card_index - 1]

        logger.change_status(status=f"Upgrading card index: {card_index}")

        # First click (card upgrade emoji)
        emulator.click(x, y)
        interruptible_sleep(2)

        # Click again(click the green upgrade emoji to open the upgrade bar)
        emulator.click(x + 15, y - 15)
        logger.change_status(status="Clicking the upgrade button for this card")
        interruptible_sleep(2)

        img = emulator.screenshot()
        pixel = img[CARD_UPGRADE_MENU_COORD[1]][CARD_UPGRADE_MENU_COORD[0]]
        if not pixel_is_equal(pixel, CARD_UPGRADE_MENU_BGR, PIXEL_TOLERANCE):
            logger.log("Card upgrade menu did not open, skipping to next card")
            logger.change_status(status="Clicking deadspace after attemping upgrading this card")

            # just reduced iteration count
            for i in range(3):
                emulator.click(DEADSPACE_COORD[0], DEADSPACE_COORD[1])
                interruptible_sleep(1)

            continue  # Skip

        logger.log("On card upgrade menu")
        logger.change_status(status="On card upgrade menu")

        emulator.click(FIRST_UPGRADE_BUTTON_COORD[0], FIRST_UPGRADE_BUTTON_COORD[1])
        logger.change_status(status="Clicking the first upgrade button for this card")
        interruptible_sleep(2)

        # COIN check
        img = emulator.screenshot()
        pixel = img[COIN_INSUFFICIENT_COORD[1]][COIN_INSUFFICIENT_COORD[0]]
        if pixel_is_equal(pixel, COIN_INSUFFICIENT_BGR, PIXEL_TOLERANCE):
            logger.log("Cannot upgrade this card: not enough coins")
            logger.change_status(status="Not enough coins passing")

        else:
            logger.log("Upgraded a card!")
            upgraded_a_card = True
            prev_card_upgrades = logger.get_card_upgrades()
            logger.add_card_upgraded()
            card_upgrades = logger.get_card_upgrades()
            logger.log(
                f"Incremented cards upgraded from {prev_card_upgrades} to {card_upgrades}",
            )

        interruptible_sleep(2)

        emulator.click(SECOND_UPGRADE_BUTTON_COORD[0], SECOND_UPGRADE_BUTTON_COORD[1])
        logger.change_status(status="Clicking the second upgrade button for this card")
        interruptible_sleep(2)
        logger.change_status(status="Upgraded a card!")

        # Check for card upgrade menu close button
        img = emulator.screenshot()
        pixel = img[CARD_UPGRADE_MENU_COORD[1]][CARD_UPGRADE_MENU_COORD[0]]
        if pixel_is_equal(pixel, CARD_UPGRADE_MENU_BGR, PIXEL_TOLERANCE):
            emulator.click(CLOSE_CARD_PAGE_COORD[0], CLOSE_CARD_PAGE_COORD[1])
            interruptible_sleep(2)

        # Deadspace Clicks
        # just reduced iteration count
        for i in range(3):
            emulator.click(DEADSPACE_COORD[0], DEADSPACE_COORD[1])
            logger.change_status(status="Clicking deadspace after attemping upgrading this card")
            interruptible_sleep(1)

    return upgraded_a_card


def upgrade_cards_state(emulator, logger: Logger):
    logger.change_status(status="Upgrade cards state")

    # if not on clash main, return restart
    print("Making sure on clash main before upgrading cards")

    if not check_if_on_clash_main_menu(emulator):
        logger.change_status("Not on Clash main menu at start of upgrade_cards_state()")
        return False

    # select Trophy Road mode
    logger.change_status(status="Selecting Trophy Road mode")
    if not select_mode(emulator, "Trophy Road"):
        logger.change_status("Failed to select Trophy Road mode")
        return False

    # get to card page
    logger.change_status(status="Getting to card page")
    if get_to_card_page_from_clash_main(emulator, logger) == "restart":
        logger.change_status(
            status="Error 0751389: Failed to get to card page from Clash main in Upgrade State",
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

    emulator.click(211, 607)
    interruptible_sleep(1)
    emulator.click(243, 600)
    interruptible_sleep(2)

    if not wait_for_clash_main_menu(emulator, logger, deadspace_click=False):
        logger.change_status("Failed to wait for Clash main menu after upgrading cards")
        return False

    logger.update_time_of_last_card_upgrade(time.time())
    return True


if __name__ == "__main__":
    pass
