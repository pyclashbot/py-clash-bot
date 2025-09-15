"""
Deck randomization methods for py-clash-bot.
This module handles finding and randomizing a user-specified deck with robust page handling and fallbacks.
"""

import time

from pyclashbot.bot.deck_cycle import (
    is_single_deck_layout_by_pixel,
    switch_deck_page,
)
from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
)
from pyclashbot.detection.image_rec import find_image
from pyclashbot.utils.logger import Logger

DECK_TABS_REGION = (0, 80, 416, 146)


def randomize_deck_state(emulator, logger: Logger, deck_number: int = 2):
    """High-level state for randomizing a given deck."""
    if not check_if_on_clash_main_menu(emulator):
        logger.change_status("Not on clash main for randomize_deck_state().")
        return False

    logger.change_status(f"Starting deck randomization state for deck #{deck_number}")
    if not randomize_deck(emulator, logger, deck_number):
        logger.change_status("Randomize_deck() failed.")
        return False

    return True


def find_and_select_deck_for_randomization(emulator, logger: Logger, deck_number: int) -> tuple[bool, int | None]:
    """
    Finds and selects a specific deck for randomization, returning the deck number that was actually selected.
    Includes robust fallback to Deck 1 if the target deck is not found.
    """
    if is_single_deck_layout_by_pixel(emulator):
        logger.change_status("Single deck layout detected. Selecting it for randomization.")
        return True, 1

    logger.change_status(f"Searching for deck #{deck_number} to randomize.")

    page_to_be_on = 1 if 1 <= deck_number <= 5 else 2

    ss = emulator.screenshot()
    on_page_1 = find_image(ss, "deck_tabs/deck_1", subcrop=DECK_TABS_REGION, tolerance=0.95) is not None
    current_page = 1 if on_page_1 else 2

    if current_page != page_to_be_on:
        logger.change_status(f"Target is on page {page_to_be_on}, but bot is on page {current_page}. Switching.")
        if not switch_deck_page(emulator, logger):
            logger.error("Failed to switch to the correct deck page.")
            return False, None
        time.sleep(1)

    deck_image_folder = f"deck_tabs/deck_{deck_number}"
    deck_coords = find_image(emulator.screenshot(), deck_image_folder, subcrop=DECK_TABS_REGION, tolerance=0.95)

    if deck_coords is not None:
        logger.change_status(f"Found and selected deck #{deck_number}.")
        emulator.click(deck_coords[0] + 15, deck_coords[1] + 15)
        time.sleep(1)
        return True, deck_number

    logger.change_status(f"Could not find deck #{deck_number}. Defaulting to deck #1.")

    on_page_1_after_fail = (
        find_image(emulator.screenshot(), "deck_tabs/deck_1", subcrop=DECK_TABS_REGION, tolerance=0.95) is not None
    )

    if not on_page_1_after_fail:
        logger.change_status("Currently on page 2. Switching back to page 1 for fallback deck.")
        if not switch_deck_page(emulator, logger):
            logger.error("Failed to switch back to page 1 for fallback.")
            return False, None
        time.sleep(1)

    deck1_coords = find_image(emulator.screenshot(), "deck_tabs/deck_1", subcrop=DECK_TABS_REGION, tolerance=0.95)
    if deck1_coords is None:
        logger.error("Critical error: Could not find deck #1 even after attempting to switch to page 1.")
        return False, None

    logger.change_status("Found and selected fallback deck #1.")
    emulator.click(deck1_coords[0] + 15, deck1_coords[1] + 15)
    time.sleep(1)
    return True, 1


def randomize_deck(emulator, logger: Logger, deck_number: int) -> bool:
    """
    Main function to navigate, find, and randomize the specified deck.
    """
    start_time = time.time()

    if not get_to_card_page_from_clash_main(emulator, logger):
        return False

    success, selected_deck = find_and_select_deck_for_randomization(emulator, logger, deck_number)
    if not success or selected_deck is None:
        return False

    logger.change_status(f"Performing randomization clicks for deck #{selected_deck}.")
    emulator.click(53, 106)
    time.sleep(0.1)
    emulator.click(125, 188)
    time.sleep(0.1)
    emulator.click(280, 390)
    time.sleep(0.1)
    logger.add_card_randomization()

    logger.change_status("Returning to clash main")
    emulator.click(248, 603)
    time.sleep(1)

    if not check_if_on_clash_main_menu(emulator):
        logger.change_status("Failed to return to clash main after randomizing deck.")
        return False

    logger.change_status(f"Successfully randomized deck #{selected_deck} in {str(time.time() - start_time)[:4]}s")
    return True


# --- Old Pixel Check Functions (Commented Out for Future Reference) ---

# def check_for_underleveled_deck_options_location(emulator):
#     iar = numpy.asarray(emulator.screenshot())
#     pixels = [
#         iar[431][346],
#         iar[437][360],
#         iar[441][349],
#         iar[445][355],
#         iar[432][350],
#         iar[458][373],
#     ]
#     colors = [
#         [245, 175, 85],
#         [255, 255, 255],
#         [244, 182, 98],
#         [255, 255, 255],
#         [249, 186, 100],
#         [244, 174, 85],
#     ]
#
#     for i, p in enumerate(pixels):
#         if not pixel_is_equal(colors[i], p, tol=25):
#             return False
#
#     return True
#
# def click_delete_deck_button(emulator):
#    if check_for_underleveled_delete_deck_button_location(emulator):
#        print("Detected underleveled delete deck button location. Using that instead...")
#        emulator.click(297, 276)
#    else:
#        emulator.click(291, 305)
#
# def check_for_underleveled_delete_deck_button_location(emulator):
#     iar = numpy.asarray(emulator.screenshot())
#     pixels = [
#         iar[266][257],
#         iar[270][287],
#         iar[273][279],
#         iar[276][298],
#         iar[288][267],
#         iar[281][289],
#         iar[291][328],
#     ]
#     colors = [
#         [93, 92, 252],
#         [255, 255, 255],
#         [93, 92, 252],
#         [228, 228, 228],
#         [69, 67, 252],
#         [221, 221, 221],
#         [69, 67, 252],
#     ]
#
#     for i, p in enumerate(pixels):
#         if not pixel_is_equal(colors[i], p, tol=25):
#             return False
#
#     return True
#
# def check_for_randomize_deck_icon(emulator):
#     iar = numpy.asarray(emulator.screenshot())
#     pixels = [
#         iar[219][260],
#         iar[237][251],
#         iar[229][252],
#         iar[299][253],
#         iar[289][254],
#         iar[300][250],
#         iar[328][244],
#     ]
#     colors = [
#         [119, 235, 107],
#         [255, 255, 255],
#         [36, 36, 36],
#         [255, 255, 255],
#         [30, 36, 253],
#         [255, 255, 255],
#         [255, 255, 255],
#     ]
#
#     for i, p in enumerate(pixels):
#         if not pixel_is_equal(colors[i], p, tol=25):
#             return False
#
#     return True
#
# def wait_for_filled_deck(emulator):
#     timeout = 20  # s
#     start_time = time.time()
#     while time.time() - start_time < timeout:
#         if check_for_filled_deck(emulator):
#             return True
#     return False
#
# def check_for_filled_deck(emulator):
#     iar = numpy.asarray(emulator.screenshot())
#     pixels = [
#         iar[144][168],
#         iar[308][247],
#         iar[279][344],
#     ]
#
#     colors = [
#         [127, 47, 6],
#         [163, 87, 9],
#         [149, 70, 6],
#     ]
#
#     for i, p in enumerate(pixels):
#         if not pixel_is_equal(colors[i], p, tol=10):
#             return False
#     return True
