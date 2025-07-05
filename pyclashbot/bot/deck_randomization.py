"""random import for deck randomization"""

import time
from typing import Literal

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
)
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.google_play_emulator.gpe import click
from pyclashbot.utils.logger import Logger
import numpy
from pyclashbot.google_play_emulator.gpe import screenshot


CARD_PAGE_ICON_FROM_CLASH_MAIN: tuple[Literal[115], Literal[600]] = (115, 600)


def randomize_deck_state(logger: Logger, next_state: str, deck_number: int = 2):
    # increment job count

    # if not on clash main, return 'restart'
    if check_if_on_clash_main_menu() is False:
        logger.change_status(
            "Not on clash main for randomize_deck_state(). Returning restart!",
        )
        return "restart"

    logger.change_status(f"Randomizing deck #{deck_number}")
    if randomize_deck(logger, deck_number) is False:
        logger.change_status("Failed somewhere in randomize_deck(). Returning restart!")
        return "restart"

    return next_state


def check_for_underleveled_deck_options_location():
    iar = numpy.asarray(screenshot())
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


def click_delete_deck_button():
    if check_for_underleveled_delete_deck_button_location():
        print("Detected underleveled delete deck button location. Clicking...")
        click( 297, 276)

    else:
        click( 291, 305)


def check_for_underleveled_delete_deck_button_location():
    iar = numpy.asarray(screenshot())
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


def check_for_randomize_deck_icon():
    iar = numpy.asarray(screenshot())
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


def randomize_deck(logger: Logger, deckNo: int = 2) -> bool:
    start_time = time.time()

    differenceBetweenEachDeckX = 50

    # get to card page
    if get_to_card_page_from_clash_main( logger) is False:
        logger.change_status("Failed to get to card page from main. Returning False")
        return False

    # click on DECKS FIRST

    click( 125, 60)
    time.sleep(0.1)

    # click on the specified deck number
    logger.change_status(f"Randomizing deck {deckNo}...")

    # Calculate deck position based on deck number (1-5)
    # Base position for deck 1, then add offset for each deck

    deck_x = 95 + differenceBetweenEachDeckX * (deckNo - 1)

    # Click on the selected deck
    click( deck_x, 107)
    time.sleep(0.1)

    click( 53, 106)
    time.sleep(0.1)

    click( 125, 188)
    time.sleep(0.1)

    # # click random deck button
    # click(130, 187)
    # time.sleep(0.1)

    # click OK
    click( 280, 390)
    time.sleep(0.1)

    # increment logger's deck randomization stats
    logger.add_card_randomization()

    # get to clash main
    logger.change_status("Returning to clash main")
    click( 248, 603)
    time.sleep(1)

    # if not on clash main, return false
    if check_if_on_clash_main_menu() is False:
        logger.change_status(
            "Failed to get to clash main after randomizing deck. Returning False",
        )
        return False

    logger.change_status(
        f"Randomized deck {deckNo} in " + str(time.time() - start_time)[:5] + "s",
    )
    return True



def wait_for_filled_deck():
    timeout = 20  # s
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_for_filled_deck():
            return True
    return False


def check_for_filled_deck():
    iar = numpy.asarray(screenshot())
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

        if not pixel_is_equal(colors[i], p, tol=10):
            return False
    return True


if __name__ == "__main__":
    randomize_deck(0, Logger())
