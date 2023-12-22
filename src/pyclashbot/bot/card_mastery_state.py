import time
from typing import Literal

from pyclashbot.bot.nav import (
    check_if_on_card_page,
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
    get_to_clash_main_from_card_page,
)
from pyclashbot.detection.image_rec import check_line_for_color, pixel_is_equal
from pyclashbot.memu.client import click
from pyclashbot.utils.logger import Logger
import numpy
from pyclashbot.memu.client import screenshot


CARD_MASTERY_ICON = (275, 476)
FIRST_CARD_MASTERY_REWARD_CARD = (99, 170)
CARD_MASTERY_REWARD_COORD_LIST = [
    (202, 290),
    (202, 300),
    (202, 320),
    (202, 340),
    (202, 360),
    (202, 380),
    (202, 400),
    (202, 430),
    (202, 460),
]
CARD_PAGE_DEADSPACE: tuple[Literal[21], Literal[355]] = (5, 355)


def card_mastery_state(vm_index, logger, next_state):
    logger.change_status("Going to collect card mastery rewards")

    if not check_if_on_clash_main_menu(vm_index):
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
    logger.change_status("Getting to card page...")
    if get_to_card_page_from_clash_main(vm_index, logger) == "restart":
        logger.change_status(
            "Failed to get to card page to collect mastery rewards! Returning false"
        )
        return False
    time.sleep(3)

    # while card mastery icon exists:
    while card_mastery_rewards_exist(vm_index):
        logger.change_status("Detected card mastery rewards")
        #   click card mastery icon
        collect_first_mastery_reward(vm_index, logger)
        logger.change_status("Collected a card mastery reward!")
        logger.add_card_mastery_reward_collection()
        time.sleep(3)

    # get to clash main
    click(vm_index, 243, 600)
    time.sleep(3)

    # if not on clash main, return False
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            "Failed to get back to clash main menu from card page! Returning false"
        )
        return False

    return True


def collect_first_mastery_reward(vm_index, logger):
    # click the card mastery reward icon
    click(vm_index, 270, 480)
    time.sleep(3)

    # click first card
    click(vm_index, 105, 170)
    time.sleep(3)

    # click rewards
    for y in range(280, 520, 35):
        click(vm_index, 200, y)

    # click deadspace a bunch
    click(vm_index, 5, 355, clicks=10, interval=0.5)
    time.sleep(3)


def card_mastery_rewards_exist(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[460][280],
        iar[467][282],
        iar[464][279],
    ]
    colors = [
        [60, 8, 224],
        [57, 9, 232],
        [47, 10, 233],
    ]

    for i, p in enumerate(pixels):
        if p[2] < p[0] + p[1]:
            return False
    return True


if __name__ == "__main__":
    vm_index = 12
    logger = Logger(None)

    print(card_mastery_state(vm_index, logger, "next_state"))

    # print(card_mastery_rewards_exist(vm_index))
