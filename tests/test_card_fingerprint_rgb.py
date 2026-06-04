"""Regression: card fingerprints use RGB; emulator.screenshot() is BGR.

Run: uv run python tests/test_card_fingerprint_rgb.py
Included in: make test (all tests under tests/).
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from pyclashbot.bot import card_detection as cd

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "tests" / "fixtures" / "card_hand_bgr_regression.png"

# Slots 0-3 on the fixture: fisherman, spirit_empress (air), phoenix, mega_minion.
EXPECTED = {
    0: "fisherman",
    1: "spirit_empress",
    2: "phoenix",
    3: "mega_minion",
}


class _BgrEmulator:
    def __init__(self, bgr: np.ndarray) -> None:
        self._bgr = bgr

    def screenshot(self) -> np.ndarray:
        return self._bgr


def _load_rgb() -> np.ndarray:
    if not FIXTURE.is_file():
        raise AssertionError(f"missing fixture: {FIXTURE}")
    return np.array(Image.open(FIXTURE).convert("RGB"))


def test_screenshot_rgb_converts_bgr_channels() -> None:
    bgr = np.zeros((4, 4, 3), dtype=np.uint8)
    bgr[0, 0] = [10, 20, 30]  # B, G, R
    out = cd._screenshot_rgb(_BgrEmulator(bgr))
    assert out[0, 0].tolist() == [30, 20, 10]


def test_bgr_screenshot_without_conversion_yields_unknown() -> None:
    rgb = _load_rgb()
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    cd.battle_iar = bgr
    for slot, expected in EXPECTED.items():
        corners = cd.get_all_pixel_data(None, slot)
        got = cd.find_closest_card(corners)
        assert got == "UNKNOWN", f"slot {slot}: BGR must not match {expected}, got {got}"


def test_bgr_emulator_path_identifies_hand_after_rgb_conversion() -> None:
    rgb = _load_rgb()
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    cd.check_which_cards_are_available(_BgrEmulator(bgr), False, False)
    for slot, expected in EXPECTED.items():
        corners = cd.get_all_pixel_data(None, slot)
        raw = cd.find_closest_card(corners)
        got = cd.CARD_DETECTION_ALIASES.get(raw, raw)
        assert got == expected, f"slot {slot}: expected {expected}, got {got} (raw {raw})"


def main() -> int:
    tests = [
        test_screenshot_rgb_converts_bgr_channels,
        test_bgr_screenshot_without_conversion_yields_unknown,
        test_bgr_emulator_path_identifies_hand_after_rgb_conversion,
    ]
    for test in tests:
        print(f"running {test.__name__}...")
        test()
        print("  PASS")
    print(f"\n{len(tests)} passed")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as err:
        print(f"FAIL: {err}", file=sys.stderr)
        raise SystemExit(1) from err
