"""Fresh-account regression: the main menu is not a battle.

The gold Pass Royale button can satisfy the bright/gold pixels used by
``check_if_in_battle``. These fixtures pin the main-menu guard so the state
machine does not start a fight chain from the home screen.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from pyclashbot.bot.state_detect import check_if_in_battle, check_if_on_clash_main_menu

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = REPO_ROOT / "tests" / "fixtures"


class _BgrEmulator:
    """Minimal screenshot source; mirrors the bot's BGR contract."""

    def __init__(self, bgr: np.ndarray) -> None:
        self._bgr = bgr

    def screenshot(self) -> np.ndarray:
        return self._bgr


def _load_bgr(name: str) -> np.ndarray:
    path = FIXTURES / name
    if not path.is_file():
        raise AssertionError(f"missing fixture: {path}")
    rgb = np.array(Image.open(path).convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def test_fresh_main_menu_is_not_a_battle() -> None:
    emulator = _BgrEmulator(_load_bgr("fresh_main_menu.png"))

    # Precondition: this is the screen that used to false-positive.
    assert check_if_on_clash_main_menu(emulator) is True
    assert check_if_in_battle(emulator) is False


def test_real_battle_is_still_detected() -> None:
    emulator = _BgrEmulator(_load_bgr("real_battle.png"))

    assert check_if_on_clash_main_menu(emulator) is False
    assert check_if_in_battle(emulator) is True
