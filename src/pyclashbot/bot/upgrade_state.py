import time
from typing import Any

import numpy

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
    get_to_clash_main_from_card_page,
)
from pyclashbot.detection.image_rec import (
    check_line_for_color,
    pixel_is_equal,
    region_is_color,
)
from pyclashbot.memu.client import click, screenshot
from pyclashbot.utils.logger import Logger

CARD_COORDS: list[Any] = [
    (74, 252),
    (168, 247),
    (250, 247),
    (339, 245),
    (74, 406),
    (168, 406),
    (250, 406),
    (339, 406),
]

UPGRADE_PIXEL_COORDS: list[Any] = [
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
SECOND_UPGRADE_BUTTON_COORDS_CONDITION_1 = (239, 488)


CONFIRM_UPGRADE_BUTTON_COORDS = (232, 508)
CONFIRM_UPGRADE_BUTTON_COORDS_CONDITION_1 = (242, 413)


DEADSPACE_COORD = (10, 323)


CLOSE_BUY_GOLD_POPUP_COORD = (350, 208)

CLOSE_CARD_PAGE_COORD = (355, 238)


def upgrade_cards_state(vm_index, logger: Logger, next_state):
    logger.change_status(status="Upgrade cards state")
    logger.add_card_upgrade_attempt()
    # if not on clash main, return restart
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            status="Error 31570138 Not on clash main to being upgrade cards state"
        )
        return "restart"

    # get to card page
    logger.change_status(status="Getting to card page")
    if get_to_card_page_from_clash_main(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 0751389 Failure getting to card page from clash main in Upgrade State"
        )
        return "restart"

    # get upgrade list
    logger.change_status(status="Reading which cards are upgradable")
    upgrade_list = get_upgradable_card_bool_list(vm_index, logger)

    # for each upgradeable card, upgrade the card
    logger.change_status(status="Upgrading cards...")
    for index in range(8):
        upgrade_card(vm_index, logger, index, upgrade_list)

    logger.change_status(status="Done upgrading cards")

    # return to clash main
    if get_to_clash_main_from_card_page(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 1666713 Failure getting to clash main from card page after card upgrading"
        )
        return "restart"

    logger.update_time_of_last_card_upgrade(time.time())
    return next_state


def check_for_second_upgrade_button_condition_1(vm_index) -> bool:
    if not check_line_for_color(vm_index, 201, 473, 203, 503, (56, 228, 72)):
        return False
    if not check_line_for_color(vm_index, 275, 477, 276, 501, (56, 228, 72)):
        return False
    if not check_line_for_color(vm_index, 348, 153, 361, 153, (229, 36, 36)):
        return False

    return True


def check_for_confirm_upgrade_button_condition_1(vm_index) -> bool:
    if not check_line_for_color(vm_index, 201, 401, 201, 432, (56, 228, 72)):
        return False
    if not check_line_for_color(vm_index, 277, 399, 277, 431, (56, 228, 72)):
        return False
    if not check_line_for_color(vm_index, 347, 153, 361, 154, (111, 22, 29)):
        return False

    return True


def upgrade_card(vm_index, logger: Logger, index, upgrade_list) -> None:
    logger.change_status(status=f"Handling card index: {index}")

    # if this card index is upgradable
    if upgrade_list[index]:
        logger.change_status(status="This card is upgradable")

        # click the card
        logger.change_status(status="Clicking the card")
        click(vm_index, CARD_COORDS[index][0], CARD_COORDS[index][1])
        time.sleep(2)

        # click the upgrade button
        logger.change_status(status="Clicking the upgrade button for this card")
        coord = UPGRADE_BUTTON_COORDS[index]
        click(vm_index, coord[0], coord[1])
        time.sleep(2)

        # click second upgrade button
        logger.change_status(status="Clicking the second upgrade button")
        if check_for_second_upgrade_button_condition_1(vm_index):
            click(
                vm_index,
                SECOND_UPGRADE_BUTTON_COORDS_CONDITION_1[0],
                SECOND_UPGRADE_BUTTON_COORDS_CONDITION_1[1],
            )
        else:
            click(
                vm_index,
                SECOND_UPGRADE_BUTTON_COORDS[0],
                SECOND_UPGRADE_BUTTON_COORDS[1],
            )
        time.sleep(2)

        # click confirm upgrade button
        logger.change_status(status="Clicking the confirm upgrade button")

        if check_for_confirm_upgrade_button_condition_1(vm_index):
            click(
                vm_index,
                CONFIRM_UPGRADE_BUTTON_COORDS_CONDITION_1[0],
                CONFIRM_UPGRADE_BUTTON_COORDS_CONDITION_1[1],
            )
        else:
            click(
                vm_index,
                CONFIRM_UPGRADE_BUTTON_COORDS[0],
                CONFIRM_UPGRADE_BUTTON_COORDS[1],
            )
        time.sleep(2)

        # if gold popup doesnt exists: add to logger's upgrade stat
        if not check_for_missing_gold_popup(vm_index):
            prev_card_upgrades = logger.get_card_upgrades()
            logger.add_card_upgraded()

            card_upgrades = logger.get_card_upgrades()
            logger.log(
                f"Incremented cards upgraded from {prev_card_upgrades} to {card_upgrades}"
            )

        # close buy gold popup
        click(vm_index, CLOSE_BUY_GOLD_POPUP_COORD[0], CLOSE_BUY_GOLD_POPUP_COORD[1])
        time.sleep(2)

        # close card page
        click(vm_index, CLOSE_CARD_PAGE_COORD[0], CLOSE_CARD_PAGE_COORD[1])
        time.sleep(2)

        # click deadspace
        logger.change_status(status="Clicking deadspace")
        for _ in range(21):
            click(vm_index, DEADSPACE_COORD[0], DEADSPACE_COORD[1])
            time.sleep(0.33)

        logger.change_status(status="Upgraded this card...")


def get_upgradable_card_bool_list(vm_index, logger: Logger):
    bool_list = []

    logger.change_status(status="Checking out which cards are upgradable")

    for index in range(8):
        this_card_coord = CARD_COORDS[index]
        this_upgrade_pixel_coord = UPGRADE_PIXEL_COORDS[index]

        # click the card
        click(vm_index, this_card_coord[0], this_card_coord[1])
        time.sleep(2)

        # read the pixel
        this_pixel: numpy.ndarray[Any, numpy.dtype[Any]] = numpy.asarray(
            screenshot(vm_index)
        )[this_upgrade_pixel_coord[1]][this_upgrade_pixel_coord[0]]

        if pixel_is_equal(this_pixel, GREEN_COLOR, tol=35):  # type: ignore
            bool_list.append(True)
        else:
            bool_list.append(False)

    return bool_list


def check_for_missing_gold_popup(vm_index):
    if not check_line_for_color(
        vm_index, x_1=338, y_1=215, x_2=361, y_2=221, color=(153, 20, 17)
    ):
        return False
    if not check_line_for_color(
        vm_index, x_1=124, y_1=201, x_2=135, y_2=212, color=(255, 255, 255)
    ):
        return False

    if not check_line_for_color(vm_index, 224, 368, 236, 416, (56, 228, 72)):
        return False

    if not region_is_color(vm_index, [70, 330, 60, 70], (227, 238, 243)):
        return False

    return True


if __name__ == "__main__":
    pass
