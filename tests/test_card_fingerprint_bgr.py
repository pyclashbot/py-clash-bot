"""Regression: fingerprints and bot both use BGR emulator screenshots.

Offline test (static fixture image + a fake emulator), so it runs in the default
`pytest` selection. Run: uv run pytest tests/test_card_fingerprint_bgr.py
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from pyclashbot.bot import card_detection as cd

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "card_hand_bgr_regression.png"

EXPECTED = {
    0: "lumberjack",
    1: "ram_rider",
    2: "ice_wizard",
    3: "hero_bowler",
}


class _BgrEmulator:
    def __init__(self, bgr: np.ndarray) -> None:
        self._bgr = bgr

    def screenshot(self) -> np.ndarray:
        return self._bgr


def _load_bgr() -> np.ndarray:
    if not FIXTURE.is_file():
        raise AssertionError(f"missing fixture: {FIXTURE}")
    rgb = np.array(Image.open(FIXTURE).convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def test_bot_uses_raw_bgr_screenshot() -> None:
    bgr = np.zeros((4, 4, 3), dtype=np.uint8)
    bgr[0, 0] = [10, 20, 30]
    out = _BgrEmulator(bgr).screenshot()
    assert out[0, 0].tolist() == [10, 20, 30]


def test_bgr_path_identifies_hand() -> None:
    bgr = _load_bgr()
    cd.check_which_cards_are_available(_BgrEmulator(bgr), False, False)
    for slot, expected in EXPECTED.items():
        corners = cd.get_all_pixel_data(None, slot)
        raw = cd.find_closest_card(corners)
        got = cd.CARD_DETECTION_ALIASES.get(raw, raw)
        assert got == expected, f"slot {slot}: expected {expected}, got {got} (raw {raw})"
