import time

import numpy

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    handle_clash_main_tab_notifications,
)
from pyclashbot.detection.image_rec import (
    check_line_for_color,
    pixel_is_equal,
    region_is_color,
)
from pyclashbot.memu.client import click, screenshot
from pyclashbot.utils.logger import Logger

UNLOCK_CHEST_BUTTON_COORD = (207, 412)
QUEUE_CHEST_BUTTON_COORD = (314, 357)


def open_chests_state(vm_index, logger: Logger, next_state: str):
    logger.change_status(status="Opening chests state")

    logger.change_status(status="Handling obstructing notifications")
    if handle_clash_main_tab_notifications(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 07531083150 Failure with handle_clash_main_tab_notifications"
        )
        return "restart"

    time.sleep(3)

    # if not on clash main return
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            status="ERROR 827358235 Not on clash main menu, returning to start state"
        )
        return "restart"

    logger.change_status(status="Opening chests...")
    # check which chests are available
    statuses = get_chest_statuses(vm_index)  # available/unavailable

    chest_index = 0
    for status in statuses:
        logger.log(f'Investigating chest #{chest_index} with status "{status}"')
        if status == "available":
            open_chest(vm_index, logger, chest_index)

        chest_index += 1

    time.sleep(3)

    return next_state


def get_chest_statuses(vm_index):
    iar = numpy.asarray(screenshot(vm_index))

    statuses = []

    # check chest 1
    chest_1_exists = False
    for x_index in range(66, 87):
        this_pixel = iar[533][x_index]
        if not pixel_is_equal([13, 92, 136], this_pixel, tol=35):
            statuses.append("available")
            chest_1_exists = True
            break

    if not chest_1_exists:
        statuses.append("unavailable")

    # check chest 2
    chest_2_exists = False
    for x_index in range(137, 168):
        this_pixel = iar[537][x_index]
        if not pixel_is_equal([31, 118, 158], this_pixel, tol=35):
            chest_2_exists = True
            statuses.append("available")
            break

    if not chest_2_exists:
        statuses.append("unavailable")

    # check chest 3
    chest_3_exists = False
    for x_index in range(248, 280):
        this_pixel = iar[536][x_index]
        if not pixel_is_equal([32, 117, 160], this_pixel, tol=35):
            chest_3_exists = True
            statuses.append("available")
            break

    if not chest_3_exists:
        statuses.append("unavailable")

    # check chest 4
    chest_4_exists = False
    for x_index in range(315, 348):
        this_pixel = iar[536][x_index]
        if not pixel_is_equal([20, 96, 142], this_pixel, tol=35):
            chest_4_exists = True
            statuses.append("available")
            break

    if not chest_4_exists:
        statuses.append("unavailable")

    return statuses


def open_chest(vm_index, logger, chest_index):
    chest_coords = [
        (77, 497),
        (164, 509),
        (254, 514),
        (339, 516),
    ]

    # click the chest
    coord = chest_coords[chest_index]
    click(vm_index, coord[0], coord[1])
    time.sleep(3)

    # if its unlockable, unlock it
    if check_if_chest_is_unlockable(vm_index):
        logger.add_chest_unlocked()
        click(vm_index, UNLOCK_CHEST_BUTTON_COORD[0], UNLOCK_CHEST_BUTTON_COORD[1])
        time.sleep(3)

    if check_if_can_queue_chest(vm_index):
        click(vm_index, QUEUE_CHEST_BUTTON_COORD[0], QUEUE_CHEST_BUTTON_COORD[1])
        time.sleep(3)

    # click deadspace a bunch if you just accidentally opened the chest
    click(vm_index, 20, 350, clicks=20, interval=0.3)


def check_if_can_queue_chest(vm_index):
    if not check_line_for_color(vm_index, 293, 345, 301, 354, (255, 255, 255)):
        return False
    if not check_line_for_color(vm_index, 338, 345, 329, 357, (255, 255, 255)):
        return False
    if not check_line_for_color(vm_index, 336, 369, 329, 358, (255, 255, 255)):
        return False

    if not region_is_color(
        vm_index,
        [
            280,
            360,
            16,
            8,
        ],
        (255, 188, 41),
    ):
        return False
    if not region_is_color(vm_index, [342, 354, 12, 16], (255, 188, 43)):
        return False
    return True


def check_if_chest_is_unlockable(vm_index):
    line1 = check_line_for_color(
        vm_index, x_1=163, y_1=392, x_2=186, y_2=423, color=(255, 190, 43)
    )
    line2 = check_line_for_color(
        vm_index, x_1=254, y_1=408, x_2=231, y_2=426, color=(255, 190, 43)
    )
    if line1 and line2:
        return True
    return False


if __name__ == "__main__":
    while 1:
        pass
