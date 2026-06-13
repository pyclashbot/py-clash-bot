"""Deck selection, cycling, and randomization for py-clash-bot.

Consolidates the former deck_utils.py, deck_cycle.py, and deck_randomization.py.
"""

import time

from pyclashbot.bot.coords import (
    DECK_OPTIONS_BUTTON_COORDS,
    DECK_TABS_REGION,
    RANDOMIZE_DECK_BUTTON_COORDS,
    RANDOMIZE_DECK_CONFIRM_BUTTON_COORDS,
)
from pyclashbot.bot.nav import (
    _navigate_to_deck_selection,
    get_to_card_page_from_clash_main,
    return_to_clash_main_from_card_page,
    switch_deck_page,
)
from pyclashbot.bot.state_detect import (
    check_if_on_clash_main_menu,
    is_deck_full,
    is_single_deck_layout_by_pixel,
)
from pyclashbot.detection.image_rec import find_image
from pyclashbot.utils.logger import Logger


def randomize_and_check_deck(emulator, logger: Logger, deck_to_randomize: int) -> bool:
    """
    Randomizes the selected deck and verifies that it becomes full.

    This function intelligently handles whether the deck is full or partial
    before randomizing, applying the correct click sequence for each case.
    """
    logger.change_status(f"Randomizing deck #{deck_to_randomize}...")

    deck_is_full_before_randomize = is_deck_full(emulator)

    emulator.click(*DECK_OPTIONS_BUTTON_COORDS)
    time.sleep(0.1)

    emulator.click(*RANDOMIZE_DECK_BUTTON_COORDS)
    time.sleep(0.1)

    if deck_is_full_before_randomize:
        emulator.click(*RANDOMIZE_DECK_CONFIRM_BUTTON_COORDS)
        time.sleep(0.1)

    time.sleep(1.0)
    logger.add_card_randomization()

    if not is_deck_full(emulator):
        logger.change_status(f"Deck {deck_to_randomize} still not full after randomizing.")
        return False

    logger.change_status(f"Deck #{deck_to_randomize} successfully randomized.")
    return True


def select_deck_state(emulator, logger: Logger, deck_number, deck_count) -> tuple[bool, int | None]:
    if not check_if_on_clash_main_menu(emulator):
        logger.change_status("Not on main menu — cannot select deck")
        return False, None
    logger.change_status(f"Selecting deck #{deck_number}")
    success, selected_deck_number = select_deck(emulator, logger, deck_number, deck_count)
    if not success:
        logger.change_status("Deck selection failed")
        return False, None
    return True, selected_deck_number


def find_and_click_deck(emulator, logger: Logger, deck_number: int, deck_count: int) -> tuple[bool, int | None]:
    if is_single_deck_layout_by_pixel(emulator):
        logger.change_status("Pixel check confirmed single-deck layout.")
        if is_deck_full(emulator):
            logger.change_status("Single deck is complete. Using it.")
            return True, 1
        else:
            logger.change_status("Single deck is not complete. Randomizing it.")
            if randomize_and_check_deck(emulator, logger, 1):
                return True, 1
            else:
                logger.error("Failed to randomize the single deck.")
                return False, None

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
            if randomize_and_check_deck(emulator, logger, deck_to_check):
                return True, deck_to_check
            else:
                logger.change_status(f"Failed to randomize deck #{deck_to_check}. Continuing...")
                continue

    logger.error("Could not find any usable decks after checking all available pages.")
    return False, None


def select_deck(emulator, logger: Logger, deck_number: int, deck_count: int) -> tuple[bool, int | None]:
    start_time = time.time()
    if not _navigate_to_deck_selection(emulator, logger):
        return False, None

    success, selected_deck_number = find_and_click_deck(emulator, logger, deck_number, deck_count)
    if not success:
        logger.change_status("Failed to find and select deck")
        return_to_clash_main_from_card_page(emulator, logger)
        return False, None

    if not return_to_clash_main_from_card_page(emulator, logger):
        return False, None

    logger.add_deck_cycled()
    logger.change_status(f"Selected deck {selected_deck_number} in {str(time.time() - start_time)[:4]}s")
    return True, selected_deck_number


def randomize_deck_state(emulator, logger: Logger, deck_number: int = 2):
    if not check_if_on_clash_main_menu(emulator):
        logger.change_status("Not on main menu — cannot randomize deck")
        return False

    logger.change_status(f"Starting deck randomization state for deck #{deck_number}")
    if not randomize_deck(emulator, logger, deck_number):
        logger.change_status("Deck randomization failed")
        return False

    return True


def find_and_select_deck_for_randomization(emulator, logger: Logger, deck_number: int) -> tuple[bool, int | None]:
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
        find_image(
            emulator.screenshot(),
            "deck_tabs/deck_1",
            subcrop=DECK_TABS_REGION,
            tolerance=0.95,
        )
        is not None
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
    """Orchestrates the entire deck randomization process including navigation."""
    start_time = time.time()

    if not get_to_card_page_from_clash_main(emulator, logger):
        return False

    success, selected_deck = find_and_select_deck_for_randomization(emulator, logger, deck_number)
    if not success or selected_deck is None:
        return False

    if not randomize_and_check_deck(emulator, logger, selected_deck):
        logger.error(f"Failed to randomize and verify deck #{selected_deck}.")
        return_to_clash_main_from_card_page(emulator, logger)
        return False

    if not return_to_clash_main_from_card_page(emulator, logger):
        return False

    logger.change_status(f"Successfully randomized deck #{selected_deck} in {str(time.time() - start_time)[:4]}s")
    return True
