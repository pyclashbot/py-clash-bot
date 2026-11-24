"""Deck randomization: one path, full decks only, bounded confirm, no loops."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pytest
from PIL import Image

from pyclashbot.bot import coords, deck, state_detect
from pyclashbot.bot.coords import (
    CONFIRM_RANDOMIZE_DECK_BUTTON_COORD,
    DECK_PAGE_OPTIONS_BUTTON_COORDS,
    RANDOMIZE_DECK_BUTTON_COORD,
)
from pyclashbot.utils.logger import Logger

FIXTURES = Path(__file__).resolve().parent / "fixtures"
OLD_CLICKS = {(53, 106), (125, 188), (280, 390)}


class _RecordingLogger(Logger):
    def __init__(self) -> None:
        super().__init__(stats=None, timed=False)
        self.statuses: list[str] = []
        self.randomizations = 0
        self.current_account = 0

    def change_status(self, status: str) -> None:
        self.statuses.append(status)
        super().change_status(status)

    def add_card_randomization(self) -> None:
        self.randomizations += 1


class _FakeEmulator:
    def __init__(self) -> None:
        self.clicks: list[tuple[int, int]] = []
        self.image = np.zeros((633, 419, 3), dtype=np.uint8)

    def screenshot(self) -> np.ndarray:
        return self.image

    def click(self, x: int, y: int) -> None:
        self.clicks.append((x, y))


class _FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0

    def time(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


class _Sequence:
    def __init__(self, *values):
        self.values = list(values)
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        if len(self.values) > 1:
            return self.values.pop(0)
        return self.values[0]


def _frame(name: str) -> np.ndarray:
    rgb = np.array(Image.open(FIXTURES / name).convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


@pytest.fixture(autouse=True)
def _reset_latch(monkeypatch: pytest.MonkeyPatch) -> None:
    deck.reset_randomize_latch()
    clock = _FakeClock()
    monkeypatch.setattr(deck.time, "time", clock.time)
    monkeypatch.setattr(deck.time, "sleep", clock.sleep)


def _patch_common(
    monkeypatch: pytest.MonkeyPatch,
    *,
    is_full,
    signature,
    confirm,
    known_page=True,
    single_layout=False,
):
    monkeypatch.setattr(deck, "get_to_card_page_from_clash_main", lambda *args: "good")
    monkeypatch.setattr(deck, "return_to_clash_main_from_card_page", lambda *args: True)
    monkeypatch.setattr(deck, "is_single_deck_layout_by_pixel", lambda *args: single_layout)
    monkeypatch.setattr(deck, "_on_known_deck_page", known_page if callable(known_page) else lambda *args: known_page)
    monkeypatch.setattr(deck, "is_deck_full", is_full if callable(is_full) else lambda *args: is_full)
    monkeypatch.setattr(deck, "deck_card_signature", signature if callable(signature) else lambda *args: signature)
    monkeypatch.setattr(
        deck,
        "check_if_on_confirm_randomize_deck_page",
        confirm if callable(confirm) else lambda *args: confirm,
    )
    monkeypatch.setattr(
        deck,
        "find_image",
        lambda _image, folder, **kwargs: (130, 100) if folder == "deck_tabs/deck_2" else None,
    )


def test_full_deck_randomizes_once_with_one_confirm(monkeypatch: pytest.MonkeyPatch) -> None:
    emulator = _FakeEmulator()
    logger = _RecordingLogger()
    _patch_common(
        monkeypatch,
        is_full=_Sequence(True, True),
        signature=_Sequence(((1, 2, 3),) * 8, ((4, 5, 6),) * 8),
        confirm=True,
    )

    assert deck.randomize_deck(emulator, logger, 2) is True
    assert emulator.clicks == [
        (145, 115),  # deck 2 tab
        DECK_PAGE_OPTIONS_BUTTON_COORDS,
        RANDOMIZE_DECK_BUTTON_COORD,
        CONFIRM_RANDOMIZE_DECK_BUTTON_COORD,
    ]
    assert logger.randomizations == 1
    assert not any(click in OLD_CLICKS for click in emulator.clicks)


def test_generic_full_deck_page_uses_the_active_deck(monkeypatch: pytest.MonkeyPatch) -> None:
    emulator = _FakeEmulator()
    logger = _RecordingLogger()
    _patch_common(
        monkeypatch,
        is_full=_Sequence(True, True),
        signature=_Sequence(((1, 2, 3),) * 8, ((4, 5, 6),) * 8),
        confirm=True,
        known_page=False,
    )
    monkeypatch.setattr(deck, "check_if_on_card_page", lambda *args: True)
    monkeypatch.setattr(deck, "find_image", lambda *args, **kwargs: None)

    assert deck.randomize_deck(emulator, logger, 2) is True
    assert DECK_PAGE_OPTIONS_BUTTON_COORDS in emulator.clicks
    assert RANDOMIZE_DECK_BUTTON_COORD in emulator.clicks
    assert any("active full deck" in status for status in logger.statuses)


def test_partial_deck_is_never_randomized(monkeypatch: pytest.MonkeyPatch) -> None:
    emulator = _FakeEmulator()
    logger = _RecordingLogger()
    _patch_common(
        monkeypatch,
        is_full=False,
        signature=lambda *args: ((1, 2, 3),) * 8,
        confirm=True,
    )

    assert deck.randomize_deck(emulator, logger, 2) is False
    assert emulator.clicks == [(145, 115)]  # only the tab selection
    assert logger.randomizations == 0
    assert any("not full" in status.lower() for status in logger.statuses)


def test_undetected_screen_does_not_randomize(monkeypatch: pytest.MonkeyPatch) -> None:
    emulator = _FakeEmulator()
    logger = _RecordingLogger()
    _patch_common(
        monkeypatch,
        is_full=True,
        signature=lambda *args: ((1, 2, 3),) * 8,
        confirm=True,
        known_page=False,
    )

    assert deck.randomize_deck(emulator, logger, 2) is False
    assert emulator.clicks == []
    assert logger.randomizations == 0
    assert any("undetected" in status.lower() for status in logger.statuses)


def test_no_confirm_page_times_out_without_confirm_click(monkeypatch: pytest.MonkeyPatch) -> None:
    emulator = _FakeEmulator()
    logger = _RecordingLogger()
    confirm = _Sequence(False)
    _patch_common(
        monkeypatch,
        is_full=_Sequence(True),
        signature=lambda *args: ((1, 2, 3),) * 8,
        confirm=confirm,
        known_page=_Sequence(True, False),
    )

    assert deck.randomize_deck(emulator, logger, 2) is False
    assert DECK_PAGE_OPTIONS_BUTTON_COORDS in emulator.clicks
    assert RANDOMIZE_DECK_BUTTON_COORD in emulator.clicks
    assert CONFIRM_RANDOMIZE_DECK_BUTTON_COORD not in emulator.clicks
    assert confirm.calls <= 25  # bounded wait, not an unbounded retry loop
    assert logger.randomizations == 0


def test_unchanged_card_order_is_not_counted(monkeypatch: pytest.MonkeyPatch) -> None:
    emulator = _FakeEmulator()
    logger = _RecordingLogger()
    _patch_common(
        monkeypatch,
        is_full=_Sequence(True, True),
        signature=_Sequence(((1, 2, 3),) * 8, ((1, 2, 3),) * 8),
        confirm=True,
    )

    assert deck.randomize_deck(emulator, logger, 2) is False
    assert CONFIRM_RANDOMIZE_DECK_BUTTON_COORD in emulator.clicks
    assert logger.randomizations == 0
    assert any("did not change" in status for status in logger.statuses)


def test_randomize_state_runs_once_per_account_and_deck(monkeypatch: pytest.MonkeyPatch) -> None:
    logger = _RecordingLogger()
    calls: list[int] = []
    monkeypatch.setattr(deck, "check_if_on_clash_main_menu", lambda *args: True)
    monkeypatch.setattr(
        deck,
        "randomize_deck",
        lambda _emulator, _logger, number: calls.append(number) or True,
    )

    assert deck.randomize_deck_state(object(), logger, 2) is True
    assert deck.randomize_deck_state(object(), logger, 2) is True
    assert calls == [2]
    assert logger.current_account == 0

    logger.current_account = 1
    assert deck.randomize_deck_state(object(), logger, 2) is True
    assert calls == [2, 2]


def test_randomize_state_returns_false_on_undetected_screen(monkeypatch: pytest.MonkeyPatch) -> None:
    logger = _RecordingLogger()
    monkeypatch.setattr(deck, "check_if_on_clash_main_menu", lambda *args: True)
    monkeypatch.setattr(deck, "randomize_deck", lambda *args: False)

    assert deck.randomize_deck_state(object(), logger, 2) is False
    assert any("failed" in status.lower() for status in logger.statuses)


def test_find_and_click_deck_refuses_partial_single_deck(monkeypatch: pytest.MonkeyPatch) -> None:
    emulator = _FakeEmulator()
    logger = _RecordingLogger()
    monkeypatch.setattr(deck, "is_single_deck_layout_by_pixel", lambda *args: True)
    monkeypatch.setattr(deck, "is_deck_full", lambda *args: False)

    assert deck.find_and_click_deck(emulator, logger, 1, 1) == (False, None)
    assert emulator.clicks == []
    assert any("no full deck" in status.lower() for status in logger.statuses)


def test_find_and_click_deck_selects_the_next_full_deck_without_shuffling(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    emulator = _FakeEmulator()
    logger = _RecordingLogger()
    monkeypatch.setattr(deck, "is_single_deck_layout_by_pixel", lambda *args: False)
    monkeypatch.setattr(deck, "is_deck_full", _Sequence(False, True))

    def _find(_image, folder, **kwargs):
        return {"deck_tabs/deck_1": (10, 10), "deck_tabs/deck_2": (130, 10)}.get(folder)

    monkeypatch.setattr(deck, "find_image", _find)

    assert deck.find_and_click_deck(emulator, logger, 1, 2) == (True, 2)
    assert emulator.clicks == [(25, 25), (145, 25)]
    assert not any(click in OLD_CLICKS for click in emulator.clicks)
    assert not any(click in {DECK_PAGE_OPTIONS_BUTTON_COORDS, RANDOMIZE_DECK_BUTTON_COORD} for click in emulator.clicks)


def test_no_stale_duplicate_coordinates_remain() -> None:
    assert not hasattr(coords, "DECK_OPTIONS_BUTTON_COORDS")
    assert not hasattr(coords, "RANDOMIZE_DECK_BUTTON_COORDS")
    assert not hasattr(coords, "RANDOMIZE_DECK_CONFIRM_BUTTON_COORDS")


def test_live_deck_page_fixture_is_full_and_order_sensitive() -> None:
    emulator = _FakeEmulator()
    emulator.image = _frame("deck_full_8of8.png")

    assert state_detect.is_deck_full(emulator) is True
    signature = state_detect.deck_card_signature(emulator)
    assert len(signature) == 8
    assert signature == state_detect.deck_card_signature(emulator)


def test_confirm_page_fixture_matches_the_detector() -> None:
    emulator = _FakeEmulator()
    emulator.image = _frame("deck_randomize_confirm.png")
    assert state_detect.check_if_on_confirm_randomize_deck_page(emulator) is True
