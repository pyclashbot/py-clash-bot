import numpy

from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.utils.cancellation import interruptible_sleep
from pyclashbot.utils.logger import Logger

# --- Constants for UI element locations ---
DECK_OPTIONS_BUTTON_COORDS = (53, 106)
RANDOMIZE_DECK_BUTTON_COORDS = (125, 188)
RANDOMIZE_DECK_CONFIRM_BUTTON_COORDS = (280, 390)


def is_deck_full(emulator) -> bool:
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
    return all(any(pixel_is_equal(valid_color, p, tol=40) for valid_color in valid_colors) for p in pixels)


def is_single_deck_layout_by_pixel(emulator) -> bool:
    iar = numpy.asarray(emulator.screenshot())
    pixel_coords = [(99, 165), (117, 166), (99, 313), (117, 313)]
    expected_colors = [[141, 29, 0], [147, 34, 0], [145, 31, 4], [149, 34, 3]]
    return all(
        pixel_is_equal(expected, actual, tol=45)
        for (x, y), expected in zip(pixel_coords, expected_colors)
        for actual in [iar[y][x]]
    )


def randomize_and_check_deck(emulator, logger: Logger, deck_to_randomize: int) -> bool:
    """
    Randomizes the selected deck and verifies that it becomes full.

    This function intelligently handles whether the deck is full or partial
    before randomizing, applying the correct click sequence for each case.
    """
    logger.change_status(f"Randomizing deck #{deck_to_randomize}...")

    # Check if the deck is full to determine which click sequence to use
    deck_is_full_before_randomize = is_deck_full(emulator)

    # Click the options menu
    emulator.click(*DECK_OPTIONS_BUTTON_COORDS)
    interruptible_sleep(0.1)

    # Click the randomize button
    emulator.click(*RANDOMIZE_DECK_BUTTON_COORDS)
    interruptible_sleep(0.1)

    # If the deck was already full, a confirmation is required
    if deck_is_full_before_randomize:
        emulator.click(*RANDOMIZE_DECK_CONFIRM_BUTTON_COORDS)
        interruptible_sleep(0.1)

    # Wait for cards to populate, then check if the deck is now full
    interruptible_sleep(1.0)
    logger.add_card_randomization()

    if not is_deck_full(emulator):
        logger.change_status(f"Deck {deck_to_randomize} still not full after randomizing.")
        return False

    logger.change_status(f"Deck #{deck_to_randomize} successfully randomized.")
    return True
