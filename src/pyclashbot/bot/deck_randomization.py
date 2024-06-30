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


CARD_PAGE_ICON_FROM_CLASH_MAIN: tuple[Literal[115], Literal[600]] = (115, 600)


def randomize_deck_state(vm_index: int, logger: Logger, next_state: str):
    # increment job count
    logger.add_randomize_deck_attempt()

    # if not on clash main, return 'restart'
    if check_if_on_clash_main_menu(vm_index) is False:
        logger.change_status(vm_index,
            "Not on clash main for randomize_deck_state(). Returning restart!"
        )
        return "restart"

    logger.change_status(vm_index,"Randomizing deck #2")
    if randomize_deck(vm_index, logger) is False:
        logger.change_status(vm_index,"Failed somewhere in randomize_deck(). Returning restart!")
        return "restart"

    return next_state


def check_for_underleveled_deck_options_location(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[431][346],
        iar[437][360],
        iar[441][349],
        iar[445][355],
        iar[432][350],
        iar[458][373],
    ]
    colors = [
        [245, 175, 85],
        [255, 255, 255],
        [244, 182, 98],
        [255, 255, 255],
        [249, 186, 100],
        [244, 174, 85],
    ]

    # for p in pixels:
    #     print(p)

    for i, p in enumerate(pixels):
        if not pixel_is_equal(colors[i], p, tol=25):
            return False

    return True


def click_deck_options(vm_index):
    click(vm_index, 53, 110)


def click_delete_deck_button(vm_index):
    if check_for_underleveled_delete_deck_button_location(vm_index):
        print("Detected underleveled delete deck button location. Clicking...")
        click(vm_index, 297, 276)

    else:
        click(vm_index, 291, 305)


def check_for_underleveled_delete_deck_button_location(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[266][257],
        iar[270][287],
        iar[273][279],
        iar[276][298],
        iar[288][267],
        iar[281][289],
        iar[291][328],
    ]
    colors = [
        [93, 92, 252],
        [255, 255, 255],
        [93, 92, 252],
        [228, 228, 228],
        [69, 67, 252],
        [221, 221, 221],
        [69, 67, 252],
    ]

    # for p in pixels:
    #     print(p)

    for i, p in enumerate(pixels):
        if not pixel_is_equal(colors[i], p, tol=25):
            return False

    return True


def check_for_randomize_deck_icon(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[219][260],
        iar[237][251],
        iar[229][252],
        iar[299][253],
        iar[289][254],
        iar[300][250],
        iar[328][244],
    ]
    colors = [
        [119, 235, 107],
        [255, 255, 255],
        [36, 36, 36],
        [255, 255, 255],
        [30, 36, 253],
        [255, 255, 255],
        [255, 255, 255],
    ]

    # for p in pixels:
    #     print(p)

    for i, p in enumerate(pixels):
        if not pixel_is_equal(colors[i], p, tol=25):
            return False

    return True


def randomize_deck(vm_index: int, logger: Logger) -> bool:
    start_time = time.time()

    # get to card page
    if get_to_card_page_from_clash_main(vm_index, logger) is False:
        logger.change_status(vm_index,"Failed to get to card page from main. Returning False")
        return False

    # click on deck 2
    logger.change_status(vm_index,"Randomizing deck 2...")
    click(vm_index, 145, 107)

    # click on deck options
    print("Click deck options")
    click_deck_options(vm_index)
    time.sleep(0.1)

    # click random deck button
    click(vm_index, 130, 187)
    time.sleep(0.1)

    # click OK
    click(vm_index, 280, 390)
    time.sleep(0.1)

    # increment logger's deck randomization sta
    logger.add_card_randomization()

    # get to clash main
    logger.change_status(vm_index,"Returning to clash main")
    click(vm_index, 248, 603)
    time.sleep(1)

    # if not on clash main, return false
    if check_if_on_clash_main_menu(vm_index) is False:
        logger.change_status(vm_index,
            "Failed to get to clash main after randomizing deck. Returning False"
        )
        return False

    logger.change_status(vm_index,"Randomized deck 2 in " + str(time.time() - start_time)[:5] + "s")
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


if __name__ == "__main__":
    randomize_deck(12, Logger())
