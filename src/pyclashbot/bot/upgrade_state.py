import numpy
import time
from pyclashbot.bot.navigation import (
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
    get_to_clash_main_from_card_page,
)
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.memu.client import click, screenshot
from pyclashbot.utils.logger import Logger


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
    (75, 327),
    (192, 341),
    (284, 340),
    (364, 340),
    (112, 448),
    (199, 447),
    (287, 454),
    (374, 448),
]
GREEN_COLOR = [56, 228, 72]

UPGRADE_BUTTON_COORDS = [
    (81, 327),
    (175, 327),
    (254, 327),
    (341, 327),
    (74, 447),
    (163, 447),
    (252, 447),
    (344, 447),
]


SECOND_UPGRADE_BUTTON_COORDS = (236, 574)
CONFIRM_UPGRADE_BUTTON_COORDS = (232, 508)
DEADSPACE_COORD = (10, 323)


def upgrade_cards_state(vm_index, logger: Logger, next_state):
    logger.log("Upgrade cards state")

    # if not on clash main, return restart
    if not check_if_on_clash_main_menu(vm_index):
        logger.log("Error 31570138 Not on clash main to being upgrade cards state")
        return "restart"

    # get to card page
    logger.log("Getting to card page")
    if get_to_card_page_from_clash_main(vm_index, logger) == "restart":
        logger.log(
            "Error 0751389 Failure getting to card page from clash main in Upgrade State"
        )
        return "restart"

    # get upgrade list
    logger.log("Reading which cards are upgradable")
    upgrade_list = get_upgradable_card_bool_list(vm_index, logger)

    print('Upgrade bool list is: ', upgrade_list)

    # for each upgradeable card, upgrade the card
    logger.log("Upgrading cards...")
    for index in range(8):
        logger.log(f"Handling card index: {index}")

        # if this card index is upgradable
        if upgrade_list[index]:
            logger.log("This card is upgradable")

            # click the card
            logger.log("Clicking the card")
            click(vm_index, CARD_COORDS[index][0], CARD_COORDS[index][1])
            time.sleep(1)

            # click the upgrade button
            logger.log("Clicking the upgrade button for this card")
            click(vm_index, UPGRADE_BUTTON_COORDS[index][0], CARD_COORDS[index][1])
            time.sleep(1)

            # click second upgrade button
            logger.log("Clicking the second upgrade button")
            click(
                vm_index,
                SECOND_UPGRADE_BUTTON_COORDS[0],
                SECOND_UPGRADE_BUTTON_COORDS[1],
            )
            time.sleep(1)

            # click confirm upgrade button
            logger.log("Clicking the confirm upgrade button")
            click(
                vm_index,
                CONFIRM_UPGRADE_BUTTON_COORDS[0],
                CONFIRM_UPGRADE_BUTTON_COORDS[1],
            )
            time.sleep(1)

            # click deadspace
            logger.log("Clicking deadspace")
            for _ in range(21):
                click(vm_index, DEADSPACE_COORD[0], DEADSPACE_COORD[1])
                time.sleep(0.33)

            logger.log("Upgraded this card...")

    logger.log("Done upgrading cards")

    # return to clash main
    if get_to_clash_main_from_card_page(vm_index, logger) == "restart":
        logger.log(
            "Error 13984713 Failure getting to clash main from card page after card upgrading"
        )
        return "restart"

    return next_state


def get_upgradable_card_bool_list(vm_index, logger: Logger):
    bool_list = []

    logger.log("Checking out which cards are upgradable")

    for index in range(8):
        this_card_coord = CARD_COORDS[index]
        this_upgrade_pixel_coord = UPGRADE_PIXEL_COORDS[index]

        # click the card
        click(vm_index, this_card_coord[0], this_card_coord[1])
        time.sleep(1)

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
    print(upgrade_cards_state(1, Logger(), "next_state"))

    # screenshot(1)

    # list = get_upgradable_card_bool_list(1, Logger())
    # print(list)
