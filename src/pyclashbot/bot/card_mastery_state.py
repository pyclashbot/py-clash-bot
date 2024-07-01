import time
import numpy

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
    wait_for_clash_main_menu,
)
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.memu.client import click
from pyclashbot.utils.logger import Logger
from pyclashbot.memu.client import screenshot


def card_mastery_state(vm_index, logger, next_state):
    logger.change_status(vm_index, "Going to collect card mastery rewards")

    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(
            vm_index,
            'Not on clash main menu for card_mastery_state() returning "restart"',
        )
        return "restart"

    if collect_card_mastery_rewards(vm_index, logger) is False:
        logger.change_status(
            vm_index,
            'Failed somewhere in collect_card_mastery_rewards(), returning "restart"',
        )
        return "restart"

    return next_state


def collect_card_mastery_rewards(vm_index, logger: Logger) -> bool:
    # get to card page
    logger.change_status(vm_index, "Collecting card mastery rewards...")
    if get_to_card_page_from_clash_main(vm_index, logger) == "restart":
        logger.change_status(
            vm_index,
            "Failed to get to card page to collect mastery rewards! Returning false",
        )
        return False
    time.sleep(3)

    if not card_mastery_rewards_exist_with_delay(vm_index):
        logger.change_status(vm_index, "No card mastery rewards to collect.")
        time.sleep(1)

    else:
        # while card mastery icon exists:
        while card_mastery_rewards_exist_with_delay(vm_index):
            logger.change_status(vm_index, "Detected card mastery rewards")
            #   click card mastery icon
            collect_first_mastery_reward(vm_index)
            logger.change_status(vm_index, "Collected a card mastery reward!")
            logger.add_card_mastery_reward_collection()
            time.sleep(2)

    # get to clash main
    logger.change_status(vm_index, "Returning to clash main menu")
    click(vm_index, 243, 600)

    # wait for main to appear
    if wait_for_clash_main_menu(vm_index, logger) is False:
        logger.change_status(
            vm_index,
            "Failed to get back to clash main menu from card page! Returning false",
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

    click(vm_index, 243, 600)


def card_mastery_rewards_exist_with_delay(vm_index):
    timeout = 2  # s
    start_time = time.time()
    while time.time() - start_time < timeout:
        if card_mastery_rewards_exist(vm_index):
            return True

    return False


def card_mastery_rewards_exist(vm_index):
    # Convert the screenshot to a NumPy array for easier access
    iar = numpy.asarray(screenshot(vm_index))

    pixels = [
        iar[437][342],
        iar[422][369],
        iar[453][368],
    ]

    colors = [
        [95, 214, 251],
        [58, 10, 236],
        [43, 190, 255],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=15):
            return False

    return True


if __name__ == "__main__":
    while 1:
        start_time = time.time()
        print(card_mastery_rewards_exist_with_delay(0),time.time() - start_time)
