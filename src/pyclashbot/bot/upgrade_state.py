import numpy
import time
from bot.navigation import (
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
    get_to_clash_main_from_card_page,
)
from detection.image_rec import pixel_is_equal
from memu.client import click, screenshot
from utils.logger import Logger


CARD_COORDS = [
    (74, 252),
    (168, 247),
    (250, 247),
    (339, 245),
    (74, 406),
    (168, 406),
    (250, 406),
    (339, 406),
]

UPGRADE_PIXEL_COORDS = [
    (44, 340),
    (133, 338),
    (284, 340),
    (306, 340),
    (112, 448),
    (199, 447),
    (287, 454),
    (374, 448),
]
GREEN_COLOR = [56, 228, 72]

UPGRADE_BUTTON_COORDS = [
    (80, 290),
    (163, 290),
    (252, 290),
    (337, 290),
    (74, 440),
    (164, 440),
    (250, 440),
    (334, 440),
]


SECOND_UPGRADE_BUTTON_COORDS = (236, 574)
CONFIRM_UPGRADE_BUTTON_COORDS = (232, 508)
DEADSPACE_COORD = (10, 323)


CLOSE_BUY_GOLD_POPUP_COORD = (350, 208)

CLOSE_CARD_PAGE_COORD = (355, 238)


def upgrade_cards_state(vm_index, logger: Logger, next_state):
    logger.change_status("Upgrade cards state")

    # if not on clash main, return restart
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            "Error 31570138 Not on clash main to being upgrade cards state"
        )
        return "restart"

    # get to card page
    logger.change_status("Getting to card page")
    if get_to_card_page_from_clash_main(vm_index, logger) == "restart":
        logger.change_status(
            "Error 0751389 Failure getting to card page from clash main in Upgrade State"
        )
        return "restart"

    # get upgrade list
    logger.change_status("Reading which cards are upgradable")
    upgrade_list = get_upgradable_card_bool_list(vm_index, logger)

    # for each upgradeable card, upgrade the card
    logger.change_status("Upgrading cards...")
    for index in range(8):
        upgrade_card(vm_index, logger, index, upgrade_list)

    logger.change_status("Done upgrading cards")

    # return to clash main
    if get_to_clash_main_from_card_page(vm_index, logger) == "restart":
        logger.change_status(
            "Error 13984713 Failure getting to clash main from card page after card upgrading"
        )
        return "restart"

    return next_state


def upgrade_card(vm_index, logger, index, upgrade_list):
    logger.change_status(f"Handling card index: {index}")
    print(f"Handling card index: {index}")

    # if this card index is upgradable
    if upgrade_list[index]:
        logger.change_status("This card is upgradable")

        # click the card
        logger.change_status("Clicking the card")
        click(vm_index, CARD_COORDS[index][0], CARD_COORDS[index][1])
        time.sleep(2)

        # click the upgrade button
        logger.change_status("Clicking the upgrade button for this card")
        coord = UPGRADE_BUTTON_COORDS[index]
        click(vm_index, coord[0], coord[1])
        time.sleep(2)

        # click second upgrade button
        logger.change_status("Clicking the second upgrade button")
        click(
            vm_index,
            SECOND_UPGRADE_BUTTON_COORDS[0],
            SECOND_UPGRADE_BUTTON_COORDS[1],
        )
        time.sleep(2)

        # click confirm upgrade button
        logger.change_status("Clicking the confirm upgrade button")
        click(
            vm_index,
            CONFIRM_UPGRADE_BUTTON_COORDS[0],
            CONFIRM_UPGRADE_BUTTON_COORDS[1],
        )
        time.sleep(2)

        #if gold popup doesnt exists: add to logger's upgrade stat


        # close buy gold popup
        click(vm_index, CLOSE_BUY_GOLD_POPUP_COORD[0], CLOSE_BUY_GOLD_POPUP_COORD[1])
        time.sleep(2)

        # close card page
        click(vm_index, CLOSE_CARD_PAGE_COORD[0], CLOSE_CARD_PAGE_COORD[1])
        time.sleep(2)

        # click deadspace
        logger.change_status("Clicking deadspace")
        for _ in range(21):
            click(vm_index, DEADSPACE_COORD[0], DEADSPACE_COORD[1])
            time.sleep(0.33)

        logger.change_status("Upgraded this card...")


def get_upgradable_card_bool_list(vm_index, logger: Logger):
    bool_list = []

    logger.change_status("Checking out which cards are upgradable")

    for index in range(8):
        this_card_coord = CARD_COORDS[index]
        this_upgrade_pixel_coord = UPGRADE_PIXEL_COORDS[index]

        # click the card
        click(vm_index, this_card_coord[0], this_card_coord[1])
        time.sleep(2)

        # read the pixel
        this_pixel = numpy.asarray(screenshot(vm_index))[this_upgrade_pixel_coord[1]][
            this_upgrade_pixel_coord[0]
        ]

        if pixel_is_equal(this_pixel, GREEN_COLOR, tol=35):  # type: ignore
            bool_list.append(True)
        else:
            bool_list.append(False)

    return bool_list


if __name__ == "__main__":
    pass
