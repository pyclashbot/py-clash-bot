from pyclashbot.bot.state_detect import is_deck_full, is_single_deck_layout_by_pixel
from pyclashbot.utils.cancellation import interruptible_sleep
from pyclashbot.utils.logger import Logger

# Re-export for backwards compatibility; new callers should import from state_detect.
__all__ = ["is_deck_full", "is_single_deck_layout_by_pixel", "randomize_and_check_deck"]

# --- Constants for UI element locations ---
DECK_OPTIONS_BUTTON_COORDS = (53, 106)
RANDOMIZE_DECK_BUTTON_COORDS = (125, 188)
RANDOMIZE_DECK_CONFIRM_BUTTON_COORDS = (280, 390)


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
