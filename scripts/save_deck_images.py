"""Capture and save deck screenshots for dataset generation.

This helper script connects to the configured emulator, grabs repeated
screenshots of the Clash Royale deck area, and saves cropped images to disk.

Usage examples
--------------

Run with defaults (MEmu, 10 captures, 1 second apart)::

    uv run python scripts/save_deck_images.py

Capture 25 images at half-second intervals to a custom directory::

    uv run python scripts/save_deck_images.py --count 25 --interval 0.5 \
        --output-dir "C:/datasets/decks"

The emulator should already be running and focused on the deck screen when you
launch this script. Each run creates a timestamped sub-folder to keep captures
organised for labelling or ML pipelines (e.g. YOLO datasets).
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

from pyclashbot.bot.upgrade_state import CARD_COORDS
from pyclashbot.emulators.memu import MemuEmulatorController, verify_memu_installation
from pyclashbot.utils.logger import Logger

DeckRegion = tuple[int, int, int, int]


def default_output_dir() -> Path:
    if sys.platform.startswith("win"):
        base = Path(os.path.expandvars(r"%appdata%")) / "py-clash-bot"
    else:
        base = Path.home() / ".py-clash-bot"
    return base / "deck_snapshots"


def compute_deck_region(frame_shape: Iterable[int]) -> DeckRegion:
    height, width = frame_shape[:2]
    xs = [coord[0] for coord in CARD_COORDS]
    ys = [coord[1] for coord in CARD_COORDS]
    left = max(min(xs) - 60, 0)
    right = min(max(xs) + 60, width)
    top = max(min(ys) - 110, 0)
    bottom = min(max(ys) + 110, height)
    if right <= left or bottom <= top:
        return (0, 0, width, height)
    return (left, top, right, bottom)


def capture_deck_frame(emulator) -> np.ndarray:
    frame = emulator.screenshot()
    if frame is None or not isinstance(frame, np.ndarray):
        raise RuntimeError("Failed to capture screenshot from emulator")
    return frame


def crop_deck(frame: np.ndarray) -> np.ndarray:
    left, top, right, bottom = compute_deck_region(frame.shape)
    cropped = frame[top:bottom, left:right]
    if cropped.size == 0:
        return frame
    return cropped


def save_image(image: np.ndarray, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(path), image):
        raise RuntimeError(f"Failed to write image to {path}")


def create_emulator(logger: Logger, render_mode: str) -> MemuEmulatorController:
    if not verify_memu_installation():
        raise RuntimeError("MEmu installation was not detected. Please install MEmu first.")
    emulator = MemuEmulatorController(logger, render_mode=render_mode)
    # Do not shut down the emulator when garbage collected; user controls lifecycle.
    setattr(emulator, "_auto_stop_on_del", False)
    return emulator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture Clash Royale deck screenshots")
    parser.add_argument(
        "--render-mode",
        choices=["opengl", "directx"],
        default="directx",
        help="Render mode to use when launching MEmu (default: directx)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of deck images to capture (default: 10)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Seconds to wait between captures (default: 1.0)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory to store captured images (default: %%APPDATA%%/py-clash-bot/deck_snapshots)",
    )
    parser.add_argument(
        "--full-frame",
        action="store_true",
        help="Also save the full emulator screenshot alongside the cropped deck",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_root = args.output_dir if args.output_dir else default_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = output_root / timestamp

    logger = Logger(timed=False)
    print(f"[deck-capture] Saving images to {session_dir}")
    print("[deck-capture] Initialising emulator controller (this may take a moment)...")
    emulator = create_emulator(logger, args.render_mode)

    try:
        print("[deck-capture] Ensure the deck screen is visible in the emulator window.")
        time.sleep(1.0)
        deck_region = None

        for index in range(1, args.count + 1):
            frame = capture_deck_frame(emulator)
            if deck_region is None:
                deck_region = compute_deck_region(frame.shape)

            cropped = crop_deck(frame)
            deck_path = session_dir / f"deck_{index:03d}.png"
            save_image(cropped, deck_path)
            print(f"[deck-capture] Saved deck image #{index} -> {deck_path}")

            if args.full_frame:
                full_path = session_dir / f"deck_{index:03d}_full.png"
                save_image(frame, full_path)

            if index < args.count:
                time.sleep(max(args.interval, 0))

        if deck_region:
            left, top, right, bottom = deck_region
            print(
                "[deck-capture] Deck region used:",
                f"left={left}, top={top}, right={right}, bottom={bottom}",
            )
    finally:
        # Release reference without attempting to shut down the emulator implicitly.
        del emulator

    print("[deck-capture] Capture complete.")


if __name__ == "__main__":
    main()
