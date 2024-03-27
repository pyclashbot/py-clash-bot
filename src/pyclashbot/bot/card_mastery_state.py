import time
import numpy

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
    wait_for_clash_main_menu,
)
from pyclashbot.memu.client import click
from pyclashbot.utils.logger import Logger
from pyclashbot.memu.client import screenshot


def card_mastery_state(vm_index, logger, next_state):
    logger.change_status("Going to collect card mastery rewards")

    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(
            'Not on clash main menu for card_mastery_state() returning "restart"'
        )
        return "restart"

    if collect_card_mastery_rewards(vm_index, logger) is False:
        logger.change_status(
            'Failed somewhere in collect_card_mastery_rewards(), returning "restart"'
        )
        return "restart"

    return next_state


def collect_card_mastery_rewards(vm_index, logger: Logger) -> bool:
    # get to card page
    logger.change_status("Collecting card mastery rewards...")
    if get_to_card_page_from_clash_main(vm_index, logger) == "restart":
        logger.change_status(
            "Failed to get to card page to collect mastery rewards! Returning false"
        )
        return False
    time.sleep(3)

    if not card_mastery_rewards_exist(vm_index):
        logger.change_status("No card mastery rewards to collect.")
        time.sleep(1)

    else:
        # while card mastery icon exists:
        while card_mastery_rewards_exist(vm_index):
            logger.change_status("Detected card mastery rewards")
            #   click card mastery icon
            collect_first_mastery_reward(vm_index)
            logger.change_status("Collected a card mastery reward!")
            logger.add_card_mastery_reward_collection()
            time.sleep(3)

    # get to clash main
    click(vm_index, 243, 600)
    time.sleep(1)
    logger.change_status("Returning to clash main menu")
    click(vm_index, 243, 600)

    # wait for main to appear
    if wait_for_clash_main_menu(vm_index, logger) is False:
        logger.change_status(
            "Failed to get back to clash main menu from card page! Returning false"
        )
        return False

    return True


def collect_first_mastery_reward(vm_index):
    # click the card mastery reward icon
    click(vm_index, 318, 444)
    time.sleep(3)

    # click first card
    click(vm_index, 99, 166)
    time.sleep(3)

    # click rewards at specific Y positions
    y_positions = [316, 403, 488]
    for y in y_positions:
        click(vm_index, 200, y)
        time.sleep(0.5)

    # click deadspace a bunch
    click(vm_index, 5, 355, clicks=15, interval=0.5)
    time.sleep(3)


def card_mastery_rewards_exist(vm_index):
    # Convert the screenshot to a NumPy array for easier access
    iar = numpy.asarray(screenshot(vm_index))

    # Define the target color, positions to check, and tolerance
    target_color = numpy.array([57, 9, 236])
    positions_to_check = [
        (435, 326),
        (435, 336),
    ]
    tolerance = 10  # Define how much color variation is acceptable

    # Function to check if a pixel is within tolerance
    def is_color_within_tolerance(pixel_color, target_color, tolerance):
        return numpy.all(numpy.abs(pixel_color - target_color) <= tolerance)

    # Check each specified position for the target color within tolerance
    for pos in positions_to_check:
        pixel_color = iar[pos[0], pos[1]]
        if not is_color_within_tolerance(pixel_color, target_color, tolerance):
            return False
    return True


if __name__ == "__main__":
    vm_index = 12
    logger = Logger()

    collect_card_mastery_rewards(vm_index, logger)
