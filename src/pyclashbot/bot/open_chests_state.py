import time
from typing import Literal

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
CLASH_MAIN_DEADSPACE_COORD = (20, 350)


def open_chests_state(vm_index: int, logger: Logger, next_state: str) -> str:
    """
    This function opens all available chests in the Clash of Clans game.

    Args:
    - vm_index (int): The index of the virtual machine to use.
    - logger (Logger): The logger object to use for logging.
    - next_state (str): The next state to transition to after opening chests.

    Returns:
    - str: The next state to transition to after opening chests.
    """
    open_chests_start_time = time.time()

    logger.add_chest_unlock_attempt()
    logger.change_status(status="Opening chests state")

    # if not on clash_main, print the pixels that the box sees, then restart
    clash_main_check = check_if_on_clash_main_menu(vm_index)
    if clash_main_check is not True:
        logger.log("Not on clashmain for the start of open_chests_state()")
        logger.log(f"Bot saw these pixels: {clash_main_check}")
        return "restart"

    logger.change_status(status="Handling obstructing notifications")
    if handle_clash_main_tab_notifications(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 07531083150 Failure with handle_clash_main_tab_notifications"
        )
        return "restart"

    # if not on clash main return
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(
            status="Error 827358235 Not on clash main menu, returning to start state"
        )
        return "restart"

    logger.change_status(status="Opening chests...")
    # check which chests are available
    statuses = get_chest_statuses(vm_index)  # available/unavailable

    chest_index = 0
    for status in statuses:
        start_time = time.time()
        if status == "available":
            logger.log(f"Chest #{chest_index} is available")
            if open_chest(vm_index, logger, chest_index) == "restart":
                logger.change_status("Error 9988572 Failure with open_chest")
                return "restart"
        logger.log(
            f"Took {str(time.time() - start_time)[:5]}s to investigate chest #{chest_index}"
        )

        chest_index += 1

    logger.log(
        f"Took {str(time.time() - open_chests_start_time)[:5]}s to run open_chests_state"
    )

    return next_state


def get_chest_statuses(vm_index):
    """
    Returns a list of strings representing the status of each chest on the Clash Royale main screen.

    Args:
        vm_index (int): The index of the VM to use for the screenshot.

    Returns:
        List[str]: A list of strings representing the status of each
        chest. Possible values are "available" and "unavailable".
    """
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


def open_chest(vm_index, logger: Logger, chest_index) -> Literal["restart", "good"]:
    """
    Opens a chest at the specified index and performs necessary actions based on its status.

    Args:
        vm_index (int): The index of the VM to perform the action on.
        logger (Logger): The logger object to use for logging.
        chest_index (int): The index of the chest to open.

    Returns:
        Literal["restart", "good"]: A string indicating whether the action was successful or not.
    """
    logger.log("Opening this chest")

    prev_chests_opened = logger.get_chests_opened()

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
        time.sleep(1)

    if check_if_can_queue_chest(vm_index):
        logger.add_chest_unlocked()
        click(vm_index, QUEUE_CHEST_BUTTON_COORD[0], QUEUE_CHEST_BUTTON_COORD[1])
        time.sleep(1)

    # click deadspace until clash main reappears
    deadspace_clicking_start_time = time.time()
    while check_if_on_clash_main_menu(vm_index) is not True:
        click(vm_index, CLASH_MAIN_DEADSPACE_COORD[0], CLASH_MAIN_DEADSPACE_COORD[1])
        time.sleep(1)

        # if clicked deadspace too much, restart
        if time.time() - deadspace_clicking_start_time > 35:
            logger.change_status(
                "Error 58732589 Waited too long for clash main while opening a chest"
            )
            return "restart"

    chests_opened = logger.get_chests_opened()
    logger.log(f"Opened {chests_opened - prev_chests_opened} chests")
    return "good"


def check_if_can_queue_chest(vm_index):
    """
    Checks if a chest can be queued for opening.

    Args:
        vm_index (int): The index of the VM to perform the check on.

    Returns:
        bool: True if a chest can be queued, False otherwise.
    """
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
    """
    Checks if a chest is unlockable.

    Args:
        vm_index (int): The index of the VM to perform the check on.

    Returns:
        bool: True if the chest is unlockable, False otherwise.
    """
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
    pass
