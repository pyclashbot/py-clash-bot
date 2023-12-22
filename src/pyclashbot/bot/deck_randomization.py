"""random import for deck randomization"""
import random
import time
from typing import Literal

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
    get_to_clash_main_from_card_page,
)
from pyclashbot.detection.image_rec import (
    check_line_for_color,
    crop_image,
    find_references,
    get_file_count,
    get_first_location,
    pixel_is_equal,
    make_reference_image_list,
)
import numpy
from pyclashbot.memu.client import click, screenshot, scroll_down, scroll_up_fast
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


def randomize_deck(vm_index, logger) -> bool:
    # get to card page
    if get_to_card_page_from_clash_main(vm_index, logger) is False:
        logger.change_status("Failed to get to card page from main. Returning False")
        return False

    # click on deck 2
    logger.change_status("Deleting deck 2")
    click(vm_index, 109, 123)
    time.sleep(2)

    # click on deck options
    click(vm_index, 354, 480)
    time.sleep(2)

    # click delete deck
    print("Clicking delete")
    click(vm_index, 291, 305)
    time.sleep(2)

    # click OK
    print("Clicking OK")
    click(vm_index, 283, 387)
    time.sleep(2)

    # click empty card 1 slot
    print("Clicking empty card 1 slot")
    click(vm_index, 81, 218)
    time.sleep(4)

    # click randomize button
    print("Clicking randomize button")
    click(vm_index, 262, 396)
    time.sleep(4)

    # click OK
    print("Clicking OK to randomize")
    click(vm_index, 211, 591)
    time.sleep(2)

    # get to clash main
    logger.change_status("Returning to clash main")
    click(vm_index, 248, 603)
    time.sleep(3)

    # if not on clash main, return false
    if check_if_on_clash_main_menu(vm_index) is False:
        logger.change_status(
            "Failed to get to clash main after randomizing deck. Returning False"
        )
        return False
    time.sleep(1)

    return True


if __name__ == "__main__":
    vm_index = 12
    logger = Logger(None)

    while 1:
        randomize_deck_state(vm_index, logger, "next_state")
