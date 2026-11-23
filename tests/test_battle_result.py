"""Battle-result recording from the post-battle banner, with a per-fight latch."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image

from pyclashbot.bot import fight
from pyclashbot.bot.state_detect import read_post_battle_crown_score
from pyclashbot.utils.logger import Logger

FIXTURES = Path(__file__).resolve().parents[1] / "tests" / "fixtures"


def _load_bgr(name: str) -> np.ndarray:
    rgb = np.array(Image.open(FIXTURES / name).convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


class _FrameEmulator:
    def __init__(self, image: np.ndarray | None = None) -> None:
        self.image = np.zeros((633, 419, 3), dtype=np.uint8) if image is None else image
        self.clicks: list[tuple[int, int]] = []

    def screenshot(self) -> np.ndarray:
        return self.image

    def click(self, x: int, y: int) -> None:
        self.clicks.append((x, y))


@pytest.fixture(autouse=True)
def _reset_result_latch():
    fight.reset_battle_result_latch()
    yield
    fight.reset_battle_result_latch()


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(fight.time, "sleep", lambda _seconds: None)


def _logger() -> Logger:
    return Logger(stats=None, timed=False)


def test_crown_score_win_fixture() -> None:
    assert read_post_battle_crown_score(_FrameEmulator(_load_bgr("post_battle_win.png"))) == (3, 1)


def test_crown_score_loss_fixture() -> None:
    assert read_post_battle_crown_score(_FrameEmulator(_load_bgr("post_battle_loss.png"))) == (0, 3)


def test_record_battle_result_is_idempotent() -> None:
    logger = _logger()
    assert fight.record_battle_result(logger, True) is True
    assert fight.record_battle_result(logger, False) is False
    assert (logger.wins, logger.losses) == (1, 0)


def test_end_fight_survives_nav_failure_after_early_result(monkeypatch: pytest.MonkeyPatch) -> None:
    logger = _logger()
    emulator = _FrameEmulator(_load_bgr("post_battle_loss.png"))

    def _exit(*args: object, **kwargs: object) -> None:
        raise SystemExit(1)

    monkeypatch.setattr(fight, "get_to_main_after_fight", _exit)

    with pytest.raises(SystemExit):
        fight.end_fight_state(emulator, logger, False, False)

    assert (logger.wins, logger.losses) == (0, 1)


def test_end_fight_double_call_counts_once(monkeypatch: pytest.MonkeyPatch) -> None:
    logger = _logger()
    emulator = _FrameEmulator(_load_bgr("post_battle_win.png"))
    monkeypatch.setattr(fight, "get_to_main_after_fight", lambda *args: True)
    monkeypatch.setattr(fight, "check_if_previous_game_was_win", lambda *args, **kwargs: True)

    assert fight.end_fight_state(emulator, logger, False, False) is True
    assert fight.end_fight_state(emulator, logger, False, False) is True
    assert (logger.wins, logger.losses) == (1, 0)


def test_restart_adds_neither(monkeypatch: pytest.MonkeyPatch) -> None:
    logger = _logger()
    emulator = _FrameEmulator()
    monkeypatch.setattr(fight, "read_post_battle_crown_score", lambda _emulator: None)
    monkeypatch.setattr(fight, "get_to_main_after_fight", lambda *args: True)
    monkeypatch.setattr(fight, "check_if_previous_game_was_win", lambda *args, **kwargs: "restart")

    assert fight.end_fight_state(emulator, logger, False, False) is False
    assert (logger.wins, logger.losses) == (0, 0)


def test_battle_log_fallback_records_when_no_early_result(monkeypatch: pytest.MonkeyPatch) -> None:
    logger = _logger()
    emulator = _FrameEmulator()
    monkeypatch.setattr(fight, "wait_for_clash_main_menu", lambda *args, **kwargs: True)
    monkeypatch.setattr(fight, "get_to_activity_log", lambda *args, **kwargs: None)
    monkeypatch.setattr(fight, "check_pixels_for_win_in_battle_log", lambda _emulator: True)

    assert fight.check_if_previous_game_was_win(emulator, logger) is True
    assert (logger.wins, logger.losses) == (1, 0)
