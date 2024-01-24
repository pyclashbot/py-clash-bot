import time
from typing import Literal

import numpy

from pyclashbot.bot.nav import (
    check_for_trophy_reward_menu,
    check_if_on_clash_main_menu,
    handle_clash_main_tab_notifications,
    handle_trophy_reward_menu,
)
from pyclashbot.detection.image_rec import (
    check_line_for_color,
    pixel_is_equal,
    region_is_color,
)
from pyclashbot.memu.client import click,  screenshot
from pyclashbot.utils.logger import Logger

UNLOCK_CHEST_BUTTON_COORD = (207, 412)
QUEUE_CHEST_BUTTON_COORD = (314, 357)
CLASH_MAIN_DEADSPACE_COORD = (20, 350)
CHEST_OPENING_DEADSPACE_CLICK_TIMEOUT = 40  # s


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

    # handle being on trophy road meu
    if check_for_trophy_reward_menu(vm_index):
        handle_trophy_reward_menu(vm_index, logger)
        time.sleep(3)

    # if not on clash_main, print the pixels that the box sees, then restart
    clash_main_check = check_if_on_clash_main_menu(vm_index)
    if clash_main_check is not True:
        logger.log("Not on clashmain for the start of open_chests_state()")
        logger.log("These are the pixels the bot saw after failing to find clash main:")
        for pixel in clash_main_check:
            logger.log(f"    {pixel}")

        return "restart"

    logger.change_status(
        status="Handling obstructing notifications before opening chests"
    )
    if handle_clash_main_tab_notifications(vm_index, logger) is False:
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

    pixels = [
        iar[544][90],
        iar[538][161],
        iar[541][270],
        iar[543][335],
    ]

    colors = [
        [143, 96, 19],
        [160, 119, 33],
        [155, 115, 29],
        [142, 94, 18],
    ]

    statuses = []
    for index, pixel in enumerate(pixels):
        if not pixel_is_equal(pixel, colors[index], tol=25):
            statuses.append("available")
        else:
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
        logger.change_status("This chest is unlockable!")
        click(vm_index, UNLOCK_CHEST_BUTTON_COORD[0], UNLOCK_CHEST_BUTTON_COORD[1])
        time.sleep(1)

    if check_if_can_queue_chest(vm_index):
        logger.add_chest_unlocked()
        logger.change_status("This chest is queueable!")
        click(vm_index, QUEUE_CHEST_BUTTON_COORD[0], QUEUE_CHEST_BUTTON_COORD[1])
        time.sleep(1)

    # click deadspace until clash main reappears
    deadspace_clicking_start_time = time.time()
    while check_if_on_clash_main_menu(vm_index) is not True:
        print("Clicking deadspace to skip chest rewards bc not on clash main")
        click(vm_index, CLASH_MAIN_DEADSPACE_COORD[0], CLASH_MAIN_DEADSPACE_COORD[1])
        time.sleep(1)

        # if clicked deadspace too much, restart
        if (
            time.time() - deadspace_clicking_start_time
            > CHEST_OPENING_DEADSPACE_CLICK_TIMEOUT
        ):
            break

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
