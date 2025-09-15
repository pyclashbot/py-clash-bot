"""
Deck cycling and selection methods for py-clash-bot.
This module handles finding and selecting a user-specified deck.
It includes a fallback to randomize any partial deck that is found.
"""

import time

import numpy

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
)
from pyclashbot.detection.image_rec import find_image, pixel_is_equal
from pyclashbot.utils.logger import Logger

DECK_TABS_REGION = (0, 80, 416, 146)


def is_deck_full(emulator):
    """
    Checks if all eight card slots are filled using pixel analysis.
    """
    iar = numpy.asarray(emulator.screenshot())

    pixels = [
        iar[172][43],
        iar[172][130],
        iar[172][216],
        iar[172][302],
        iar[310][43],
        iar[311][130],
        iar[309][216],
        iar[309][302],
    ]

    valid_colors = [
        [175, 5, 179],
        [178, 5, 182],
        [178, 5, 183],
        [188, 2, 194],
        [185, 4, 191],
        [197, 2, 209],
        [193, 2, 203],
    ]

    for p in pixels:
        match_found = any(pixel_is_equal(valid_color, p, tol=40) for valid_color in valid_colors)

        if not match_found:
            return False

    return True


def is_single_deck_layout_by_pixel(emulator) -> bool:
    """
    Checks for the single-deck layout by verifying three specific pixel colors.
    """
    iar = numpy.asarray(emulator.screenshot())

    pixel_coords = [(99, 165), (117, 166), (99, 313), (117, 313)]
    expected_colors = [
        [141, 29, 0],
        [147, 34, 0],
        [145, 31, 4],
        [149, 34, 3],
    ]

    actual_pixels = [iar[y][x] for y, x in pixel_coords]

    for actual, expected in zip(actual_pixels, expected_colors):
        if not pixel_is_equal(expected, actual, tol=45):
            return False

    return True


def randomize_and_check_deck(emulator, logger, deck_to_randomize):
    """
    Performs the clicks to randomize a deck and checks if it is full afterward.
    """
    logger.change_status(f"Randomizing deck {deck_to_randomize}")
    emulator.click(53, 106)
    time.sleep(0.1)
    emulator.click(125, 188)
    time.sleep(0.1)
    logger.add_card_randomization()
    if not is_deck_full(emulator):
        logger.change_status(f"Deck {deck_to_randomize} still not full after randomizing.")


def select_deck_state(emulator, logger: Logger, deck_number, deck_count) -> tuple[bool, int | None]:
    """High-level state to select a given deck."""
    if not check_if_on_clash_main_menu(emulator):
        logger.change_status("Not on clash main for select_deck_state().")
        return False, None
    logger.change_status(f"Selecting deck #{deck_number}")
    success, selected_deck_number = select_deck(emulator, logger, deck_number, deck_count)
    if not success:
        logger.change_status("Failed somewhere in select_deck().")
        return False, None
    return True, selected_deck_number


def switch_deck_page(emulator, logger: Logger) -> bool:
    """Switches the deck page in the card menu."""
    logger.change_status("Switching deck page...")
    switch_button_coord = find_image(
        emulator.screenshot(), "deck_tabs/switch_deck", subcrop=DECK_TABS_REGION, tolerance=0.98
    )
    if switch_button_coord is not None:
        emulator.click(switch_button_coord[0], switch_button_coord[1])
        time.sleep(1)
        return True
    logger.change_status("Could not find switch deck page button.")
    return False


def find_and_click_deck(emulator, logger: Logger, deck_number: int, deck_count: int) -> tuple[bool, int | None]:
    """
    Finds and clicks a complete deck. If a partial deck is found, it
    randomizes it and selects it.
    """
    if is_single_deck_layout_by_pixel(emulator):
        logger.change_status("Pixel check confirmed single-deck layout.")
        if is_deck_full(emulator):
            logger.change_status("Single deck is complete. Using it.")
            return True, 1
        else:
            logger.change_status("Single deck is not complete. Randomizing it.")
            randomize_and_check_deck(emulator, logger, 1)
            return True, 1

    logger.change_status("Pixel check failed. Assuming multi-deck layout.")
    ss = emulator.screenshot()
    has_deck_page_2 = find_image(ss, "deck_tabs/switch_deck", subcrop=DECK_TABS_REGION, tolerance=0.98) is not None
    on_page_1 = find_image(ss, "deck_tabs/deck_1", subcrop=DECK_TABS_REGION, tolerance=0.98) is not None
    current_page = 1 if on_page_1 else 2

    deck_order_to_check = list(range(deck_number, deck_count + 1)) + list(range(1, deck_number))

    for deck_to_check in deck_order_to_check:
        if deck_to_check > 5 and not has_deck_page_2:
            logger.change_status(f"Deck #{deck_to_check} is on page 2, but no page 2 exists. Skipping.")
            continue

        page_to_be_on = 1 if 1 <= deck_to_check <= 5 else 2

        if current_page != page_to_be_on:
            if not has_deck_page_2:
                break
            if not switch_deck_page(emulator, logger):
                return False, None
            current_page = page_to_be_on

        deck_image_folder = f"deck_tabs/deck_{deck_to_check}"
        deck_coords = find_image(emulator.screenshot(), deck_image_folder, subcrop=DECK_TABS_REGION, tolerance=0.98)

        if deck_coords is None:
            logger.change_status(f"Deck #{deck_to_check} not found, skipping.")
            continue

        emulator.click(deck_coords[0] + 15, deck_coords[1] + 15)
        time.sleep(1)

        if is_deck_full(emulator):
            logger.change_status(f"Found complete deck: #{deck_to_check}.")

            return True, deck_to_check

        else:
            logger.change_status(f"Found partial deck #{deck_to_check}. Randomizing it now.")
            randomize_and_check_deck(emulator, logger, deck_to_check)
            return True, deck_to_check

    logger.error("Could not find any usable decks after checking all available pages.")
    return False, None


def select_deck(emulator, logger: Logger, deck_number: int, deck_count: int) -> tuple[bool, int | None]:
    """Navigates to the card page and selects a deck."""
    start_time = time.time()
    if not get_to_card_page_from_clash_main(emulator, logger):
        logger.change_status("Failed to get to card page from main.")
        return False, None
    emulator.click(125, 60)
    time.sleep(0.1)

    success, selected_deck_number = find_and_click_deck(emulator, logger, deck_number, deck_count)
    if not success:
        logger.change_status("find_and_click_deck() failed.")
        emulator.click(248, 603)
        time.sleep(1)
        return False, None

    logger.change_status("Returning to clash main")
    emulator.click(248, 603)
    time.sleep(1)
    if not check_if_on_clash_main_menu(emulator):
        logger.change_status("Failed to return to clash main after selecting deck.")
        return False, None

    logger.change_status(f"Selected deck {selected_deck_number} in {str(time.time() - start_time)[:4]}s")
    return True, selected_deck_number
