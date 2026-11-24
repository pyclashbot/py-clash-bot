"""Deck selection, cycling, and randomization for py-clash-bot.

Consolidates the former deck_utils.py, deck_cycle.py, and deck_randomization.py.
"""

import time

from pyclashbot.bot.coords import (
    CONFIRM_RANDOMIZE_DECK_BUTTON_COORD,
    DECK_PAGE_OPTIONS_BUTTON_COORDS,
    DECK_TABS_REGION,
    RANDOMIZE_DECK_BUTTON_COORD,
)
from pyclashbot.bot.nav import (
    _navigate_to_deck_selection,
    get_to_card_page_from_clash_main,
    return_to_clash_main_from_card_page,
    switch_deck_page,
)
from pyclashbot.bot.state_detect import (
    check_if_on_clash_main_menu,
    check_if_on_classic_1v1_deck_page,
    check_if_on_classic_2v2_deck_page,
    check_if_on_confirm_randomize_deck_page,
    check_if_on_trophy_road_deck_page,
    deck_card_signature,
    is_deck_full,
    is_single_deck_layout_by_pixel,
)
from pyclashbot.detection.image_rec import find_image
from pyclashbot.utils.logger import Logger

CONFIRM_PAGE_TIMEOUT_S = 5.0
DECK_PAGE_TIMEOUT_S = 5.0
POLL_INTERVAL_S = 0.25
OPTIONS_SETTLE_S = 0.5
TAB_SETTLE_S = 1.0
DECK_SETTLE_S = 0.5

# One successful randomization per (account, deck) avoids shuffling again on every
# state-machine loop. Tests call reset_randomize_latch().
_RANDOMIZED_DECKS: set[tuple[int, int]] = set()


def reset_randomize_latch() -> None:
    _RANDOMIZED_DECKS.clear()


def _on_known_deck_page(emulator) -> bool:
    return (
        check_if_on_trophy_road_deck_page(emulator)
        or check_if_on_classic_2v2_deck_page(emulator)
        or check_if_on_classic_1v1_deck_page(emulator)
    )


def _wait_until(predicate, *, timeout: float) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(POLL_INTERVAL_S)
    return predicate()


def _select_deck_tab(emulator, logger: Logger, deck_number: int) -> bool:
    """Click the target deck tab; single-deck layouts use the only deck."""
    if is_single_deck_layout_by_pixel(emulator):
        return True
    if not 1 <= deck_number <= 10:
        logger.change_status(f"Invalid deck number #{deck_number}; cannot randomize")
        return False
    folder = f"deck_tabs/deck_{deck_number}"
    coords = find_image(emulator.screenshot(), folder, subcrop=DECK_TABS_REGION, tolerance=0.98)
    if coords is None and deck_number > 5:
        if not switch_deck_page(emulator, logger):
            return False
        coords = find_image(emulator.screenshot(), folder, subcrop=DECK_TABS_REGION, tolerance=0.98)
    if coords is None:
        logger.change_status(f"Deck #{deck_number} tab not found; cannot randomize")
        return False
    emulator.click(coords[0] + 15, coords[1] + 15)
    time.sleep(TAB_SETTLE_S)
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
    """Select an already-full deck; never randomize a partial/fresh deck here."""
    if is_single_deck_layout_by_pixel(emulator):
        logger.change_status("Pixel check confirmed single-deck layout.")
        if is_deck_full(emulator):
            logger.change_status("Single deck is complete. Using it.")
            return True, 1
        logger.change_status("No full deck found — single deck is partial/fresh; not randomizing.")
        logger.error("No full deck found.")
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

        logger.change_status(f"Deck #{deck_to_check} is not full (partial/fresh); skipping.")
        logger.error(f"Deck #{deck_to_check} is not full — not randomizing.")

    logger.change_status("No full deck found — not randomizing.")
    logger.error("No full deck found.")
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

    account = int(getattr(logger, "current_account", 0) or 0)
    key = (account, deck_number)
    if key in _RANDOMIZED_DECKS:
        logger.change_status(f"Deck #{deck_number} already randomized for this account; skipping")
        return True

    logger.change_status(f"Starting deck randomization state for deck #{deck_number}")
    if not randomize_deck(emulator, logger, deck_number):
        logger.change_status("Deck randomization failed")
        return False

    _RANDOMIZED_DECKS.add(key)
    return True


def randomize_deck(emulator, logger: Logger, deck_number: int = 2) -> bool:
    """Randomize one full deck exactly once, with a bounded confirm-page wait.

    Trophy Road, Classic 1v1, and Classic 2v2 share the same deck page and
    options/randomize/confirm sequence. We deliberately refuse a partial/fresh
    deck: the confirm dialog exists only for a full deck, and shuffling a
    partial deck is the bug this path replaces.
    """
    if get_to_card_page_from_clash_main(emulator, logger) != "good":
        logger.change_status("Failed to reach the card page; not randomizing")
        return False

    if not _on_known_deck_page(emulator):
        logger.change_status("Undetected screen type. Not classic 1v1, nor 2v2, nor trophy road deck page!")
        return False

    if not _select_deck_tab(emulator, logger, deck_number):
        return_to_clash_main_from_card_page(emulator, logger)
        return False

    if not is_deck_full(emulator):
        logger.change_status(f"Deck #{deck_number} is not full (partial/fresh); not randomizing")
        return_to_clash_main_from_card_page(emulator, logger)
        return False

    before = deck_card_signature(emulator)
    logger.change_status(f"Randomizing deck #{deck_number}...")
    emulator.click(*DECK_PAGE_OPTIONS_BUTTON_COORDS)
    time.sleep(OPTIONS_SETTLE_S)
    emulator.click(*RANDOMIZE_DECK_BUTTON_COORD)

    confirm_seen = _wait_until(
        lambda: check_if_on_confirm_randomize_deck_page(emulator),
        timeout=CONFIRM_PAGE_TIMEOUT_S,
    )
    if confirm_seen:
        emulator.click(*CONFIRM_RANDOMIZE_DECK_BUTTON_COORD)

    if not _wait_until(lambda: _on_known_deck_page(emulator), timeout=DECK_PAGE_TIMEOUT_S):
        logger.change_status("Did not return to the deck page after randomizing")
        return_to_clash_main_from_card_page(emulator, logger)
        return False

    if not is_deck_full(emulator):
        logger.change_status(f"Deck #{deck_number} is not full after randomizing")
        return_to_clash_main_from_card_page(emulator, logger)
        return False

    time.sleep(DECK_SETTLE_S)
    if deck_card_signature(emulator) == before:
        logger.change_status(f"Deck #{deck_number} card order did not change; not counting randomization")
        return_to_clash_main_from_card_page(emulator, logger)
        return False

    logger.add_card_randomization()
    suffix = " after confirm" if confirm_seen else " (no confirm dialog detected)"
    logger.change_status(f"Deck #{deck_number} randomized{suffix}")
    return return_to_clash_main_from_card_page(emulator, logger)
