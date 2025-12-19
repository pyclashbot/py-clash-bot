"""
Deck cycling and selection methods for py-clash-bot.
"""

import time

from pyclashbot.bot.deck_utils import (
    DECK_TABS_REGION,
    is_deck_full,
    is_single_deck_layout_by_pixel,
    randomize_and_check_deck,
    return_to_clash_main_from_card_page,
    switch_deck_page,
)
from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
)
from pyclashbot.detection.image_rec import find_image
from pyclashbot.utils.logger import Logger

DECKS_PAGE_BUTTON_COORDS = (125, 60)


def select_deck_state(emulator, logger: Logger, deck_number, deck_count) -> tuple[bool, int | None]:
    if not check_if_on_clash_main_menu(emulator):
        logger.change_status("Not on clash main for select_deck_state().")
        return False, None
    logger.change_status(f"Selecting deck #{deck_number}")
    success, selected_deck_number = select_deck(emulator, logger, deck_number, deck_count)
    if not success:
        logger.change_status("Failed somewhere in select_deck().")
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


def _navigate_to_deck_selection(emulator, logger: Logger) -> bool:
    logger.change_status("Navigating to the deck selection page...")
    if not get_to_card_page_from_clash_main(emulator, logger):
        logger.change_status("Failed to get to card page from main.")
        return False
    emulator.click(*DECKS_PAGE_BUTTON_COORDS)
    time.sleep(0.1)
    return True


def select_deck(emulator, logger: Logger, deck_number: int, deck_count: int) -> tuple[bool, int | None]:
    start_time = time.time()
    if not _navigate_to_deck_selection(emulator, logger):
        return False, None

    success, selected_deck_number = find_and_click_deck(emulator, logger, deck_number, deck_count)
    if not success:
        logger.change_status("find_and_click_deck() failed.")
        return_to_clash_main_from_card_page(emulator, logger)
        return False, None

    if not return_to_clash_main_from_card_page(emulator, logger):
        return False, None

    logger.add_deck_cycled()
    logger.change_status(f"Selected deck {selected_deck_number} in {str(time.time() - start_time)[:4]}s")
    return True, selected_deck_number
