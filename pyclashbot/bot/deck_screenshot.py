"""Deck screenshot capture functionality during battle."""

import os
import time
from os.path import expandvars, join

import cv2

from pyclashbot.bot.nav import check_if_in_battle
from pyclashbot.utils.logger import Logger
from pyclashbot.utils.webhook import DECK_SCREENSHOT_WEBHOOK_URL, send_deck_screenshot_webhook

# Deck screenshot folder
DECK_SCREENSHOT_DIR = join(expandvars("%localappdata%"), "programs", "py-clash-bot", "deck_screenshots")

# Region for deck/hand during battle (x1, y1, x2, y2)
# Captures the bottom area where cards are shown during battle
# Hand cards are at y ~561-563, so we capture from y=520 to bottom (633)
BATTLE_DECK_REGION = (80, 520, 400, 633)


def ensure_deck_folder_exists() -> None:
    """Ensure the deck screenshots folder exists."""
    os.makedirs(DECK_SCREENSHOT_DIR, exist_ok=True)


def capture_deck_screenshot(emulator, logger: Logger) -> bool:
    """Capture a screenshot of the deck/hand during battle.

    Args:
        emulator: The emulator controller
        logger: Logger instance

    Returns:
        True if screenshot was captured, False otherwise
    """
    try:
        # Ensure folder exists before attempting to save
        ensure_deck_folder_exists()

        # Check if we're in battle
        if not check_if_in_battle(emulator):
            # Don't log every time we're not in battle to avoid spam
            return False

        # Take screenshot (returns BGR format from emulator)
        screenshot = emulator.screenshot()
        if screenshot is None:
            logger.log("Failed to capture screenshot: emulator.screenshot() returned None")
            return False

        # Validate screenshot dimensions
        if screenshot.size == 0:
            logger.log("Failed to capture screenshot: screenshot is empty")
            return False

        height, width = screenshot.shape[:2]

        # Crop to deck/hand region during battle (x1, y1, x2, y2)
        x1, y1, x2, y2 = BATTLE_DECK_REGION

        # Validate crop region is within screenshot bounds
        if x1 < 0 or y1 < 0 or x2 > width or y2 > height:
            logger.log(
                f"Crop region ({x1}, {y1}, {x2}, {y2}) exceeds screenshot bounds ({width}x{height})"
            )
            return False

        if x1 >= x2 or y1 >= y2:
            logger.log(f"Invalid crop region: ({x1}, {y1}, {x2}, {y2})")
            return False

        deck_crop = screenshot[y1:y2, x1:x2]

        # Validate crop is not empty
        if deck_crop.size == 0:
            logger.log("Failed to crop deck region: resulting crop is empty")
            return False

        # Generate filename with timestamp
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        filename = f"deck_{timestamp}.png"
        filepath = join(DECK_SCREENSHOT_DIR, filename)

        # Save the cropped deck image (screenshot is already in BGR format)
        success = cv2.imwrite(filepath, deck_crop)
        if not success:
            logger.log(f"Failed to save deck screenshot to {filepath}")
            return False

        # Verify file was actually created
        if not os.path.exists(filepath):
            logger.log(f"File was not created at {filepath}")
            return False

        # Optionally send to webhook if configured
        if DECK_SCREENSHOT_WEBHOOK_URL:
            try:
                # Read image bytes for webhook
                with open(filepath, "rb") as f:
                    image_bytes = f.read()
                send_deck_screenshot_webhook(image_bytes, DECK_SCREENSHOT_WEBHOOK_URL, timestamp=timestamp)
            except Exception as e:
                # Silently fail - don't interrupt screenshot saving
                pass

        logger.log(f"Captured deck screenshot during battle: {filename}")
        return True

    except Exception as e:
        logger.log(f"Error capturing deck screenshot: {e}")
        import traceback
        logger.log(f"Traceback: {traceback.format_exc()}")
        return False
