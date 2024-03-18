"""random import for deck randomization"""
import time
from typing import Literal

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
)
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.memu.client import click
from pyclashbot.utils.logger import Logger

DECK_2_COORD: tuple[Literal[158], Literal[127]] = (158, 127)

CLASH_MAIN_ICON_FROM_CARD_PAGE: tuple[Literal[245], Literal[600]] = (245, 600)
CARD_PAGE_ICON_FROM_CLASH_MAIN: tuple[Literal[115], Literal[600]] = (115, 600)
RANDOM_CARD_SEARCH_TIMEOUT = 120  # seconds
CARDS_TO_REPLACE_COORDS = [
    (72, 240),
    (156, 240),
    (257, 240),
    (339, 240),
    (72, 399),
    (156, 399),
    (257, 399),
    (339, 399),
]
FIND_REPLACEMENT_CARD_TIMEOUT = 10


def randomize_deck_state(vm_index: int, logger: Logger, next_state: str):
    #increment job count
    logger.add_randomize_deck_attempt()

    # if not on clash main, return 'restart'
    if check_if_on_clash_main_menu(vm_index) is False:
        logger.change_status(
            "Not on clash main for randomize_deck_state(). Returning restart!"
        )
        return "restart"

    logger.change_status("Randomizing deck #2")
    if randomize_deck(vm_index, logger) is False:
        logger.change_status("Failed somewhere in randomize_deck(). Returning restart!")
        return "restart"

    return next_state


def randomize_deck(vm_index: int, logger: Logger) -> bool:
    # get to card page
    if get_to_card_page_from_clash_main(vm_index, logger) is False:
        logger.change_status("Failed to get to card page from main. Returning False")
        return False

    # click on deck 2
    logger.change_status("Deleting deck 2...")
    click(vm_index, 109, 123)

    # click on deck options
    click(vm_index, 354, 480)
    time.sleep(0.33)

    # click delete deck
    print("Clicking delete")
    click(vm_index, 291, 305)
    time.sleep(0.33)

    # click OK
    print("Clicking OK")
    click(vm_index, 283, 387)
    time.sleep(0.33)

    # click empty card 1 slot
    logger.change_status("Randomizing deck 2...")
    print("Clicking empty card 1 slot")
    click(vm_index, 81, 218)
    time.sleep(4)

    # click randomize button
    print("Clicking randomize button")
    click(vm_index, 262, 396)
    wait_for_filled_deck(vm_index)

    # click OK
    print("Clicking OK to randomize")
    click(vm_index, 211, 591)
    time.sleep(2)

    # increment logger's deck randomization sta
    logger.add_card_randomization()

    # get to clash main
    logger.change_status("Returning to clash main")
    click(vm_index, 248, 603)
    time.sleep(2)

    # if not on clash main, return false
    if check_if_on_clash_main_menu(vm_index) is False:
        logger.change_status(
            "Failed to get to clash main after randomizing deck. Returning False"
        )
        return False
    time.sleep(1)

    return True


import numpy
from pyclashbot.memu.client import screenshot


def wait_for_filled_deck(vm_index):
    timeout = 20  # s
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_for_filled_deck(vm_index):
            return True
    return False


def check_for_filled_deck(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[144][168],
        iar[308][247],
        iar[279][344],
    ]

    colors = [
        [127, 47, 6],
        [163, 87, 9],
        [149, 70, 6],
    ]

    for i, p in enumerate(pixels):
        # print(p)
        if not pixel_is_equal(colors[i], p, tol=10):
            return False
    return True


def check_for_selected_deck_2(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[119][102],
        iar[111][111],
        iar[120][123],
        iar[13][401],
    ]

    colors = [
        [93, 211, 249],
        [94, 209, 250],
        [96, 208, 252],
        [21, 169, 45],
    ]

    for i, p in enumerate(pixels):
        # print(p)
        if not pixel_is_equal(colors[i], p, tol=10):
            return False
    return True


if __name__ == "__main__":
    start_time = time.time()
    randomize_deck(12, Logger(None))
    print(time.time() - start_time)

    # print(check_for_selected_deck_2(12))
