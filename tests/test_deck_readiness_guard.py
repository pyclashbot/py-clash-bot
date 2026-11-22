"""Deck-readiness guard: an incomplete Battle Deck stops cleanly, not via restarts."""

from __future__ import annotations

from multiprocessing import Event, Queue
from typing import TYPE_CHECKING

import numpy as np
import pytest

from pyclashbot.bot import fight, nav, state_detect, states
from pyclashbot.bot.battle_errors import BattleDeckIncompleteError
from pyclashbot.bot.coords import START_FIGHT_BUTTON_COORD
from pyclashbot.bot.fight import start_fight
from pyclashbot.bot.state_detect import check_for_incomplete_deck_popup
from pyclashbot.utils.logger import Logger, ProcessLogger

if TYPE_CHECKING:
    from pathlib import Path


class _FakeEmulator:
    def __init__(self) -> None:
        self.image = np.zeros((633, 419, 3), dtype=np.uint8)
        self.clicks: list[tuple[int, int]] = []

    def screenshot(self) -> np.ndarray:
        return self.image

    def click(self, x_coord: int, y_coord: int) -> None:
        self.clicks.append((x_coord, y_coord))


def test_popup_matcher_uses_reference_image(monkeypatch: pytest.MonkeyPatch) -> None:
    emulator = _FakeEmulator()
    monkeypatch.setattr(state_detect, "find_image", lambda *args, **kwargs: (10, 20))
    assert check_for_incomplete_deck_popup(emulator) is True

    monkeypatch.setattr(state_detect, "find_image", lambda *args, **kwargs: None)
    assert check_for_incomplete_deck_popup(emulator) is False


def test_popup_matcher_tolerates_missing_reference(monkeypatch: pytest.MonkeyPatch) -> None:
    """The reference frame is pending; a missing folder must be a no-op, not a crash."""

    def _missing(*args: object, **kwargs: object) -> object:
        raise FileNotFoundError("battle_deck_incomplete")

    monkeypatch.setattr(state_detect, "find_image", _missing)
    assert check_for_incomplete_deck_popup(_FakeEmulator()) is False


def test_popup_matcher_tolerates_empty_reference(monkeypatch: pytest.MonkeyPatch) -> None:
    """An empty folder trips find_image's zero-worker pool; treat it as no-op."""

    def _empty(*args: object, **kwargs: object) -> object:
        raise ValueError("max_workers must be greater than 0")

    monkeypatch.setattr(state_detect, "find_image", _empty)
    assert check_for_incomplete_deck_popup(_FakeEmulator()) is False


def test_wait_for_battle_start_raises_on_delayed_refusal(monkeypatch: pytest.MonkeyPatch) -> None:
    """A server refusal that lands during the wait must not fall through to timeout."""
    monkeypatch.setattr(nav, "check_for_incomplete_deck_popup", lambda _emulator: True)

    with pytest.raises(BattleDeckIncompleteError):
        nav.wait_for_battle_start(_FakeEmulator(), Logger(stats=None, timed=False), timeout=1)


def test_wait_for_battle_start_throttles_popup_checks(monkeypatch: pytest.MonkeyPatch) -> None:
    """The popup matcher is capped at ~1 Hz; the battle check still polls normally."""
    checks: list[int] = []

    def _no_popup(_emulator: object) -> bool:
        checks.append(1)
        return False

    monkeypatch.setattr(nav, "check_for_incomplete_deck_popup", _no_popup)
    monkeypatch.setattr(nav, "check_if_in_battle", lambda _emulator: False)

    assert nav.wait_for_battle_start(_FakeEmulator(), Logger(stats=None, timed=False), timeout=0.2) is False
    assert len(checks) == 1  # immediate check only; interval is 1 s


def test_start_fight_raises_on_deck_refusal(monkeypatch: pytest.MonkeyPatch) -> None:
    emulator = _FakeEmulator()
    monkeypatch.setattr(fight, "check_if_on_clash_main_menu", lambda _emulator: True)
    monkeypatch.setattr(fight, "check_for_incomplete_deck_popup", lambda _emulator: True)
    monkeypatch.setattr(fight.time, "sleep", lambda _seconds: None)

    with pytest.raises(BattleDeckIncompleteError):
        start_fight(emulator, Logger(stats=None, timed=False), "Classic 1v1")

    assert emulator.clicks == [START_FIGHT_BUTTON_COORD]


def test_start_fight_continues_when_deck_is_ready(monkeypatch: pytest.MonkeyPatch) -> None:
    emulator = _FakeEmulator()
    monkeypatch.setattr(fight, "check_if_on_clash_main_menu", lambda _emulator: True)
    monkeypatch.setattr(fight, "check_for_incomplete_deck_popup", lambda _emulator: False)
    monkeypatch.setattr(fight.time, "sleep", lambda _seconds: None)

    assert start_fight(emulator, Logger(stats=None, timed=False), "Classic 1v1") is True


def test_start_fight_state_stops_cleanly(monkeypatch: pytest.MonkeyPatch) -> None:
    def _refuse(*args: object) -> object:
        raise BattleDeckIncompleteError("Battle Deck incomplete — fill 8/8")

    logger = Logger(stats=None, timed=False)
    monkeypatch.setattr(states, "start_fight", _refuse)
    monkeypatch.setattr(states, "mode_used_in_1v1", "Classic 1v1")
    monkeypatch.setattr(states.time, "sleep", lambda _seconds: None)

    result = states.state_tree(object(), logger, "start_fight", {}, states.StateHistory(logger), states.StateOrder())

    assert result == "stop"


def test_1v1_state_stops_on_delayed_refusal(monkeypatch: pytest.MonkeyPatch) -> None:
    def _refuse(*args: object, **kwargs: object) -> object:
        raise BattleDeckIncompleteError("Battle Deck incomplete — fill 8/8")

    logger = Logger(stats=None, timed=False)
    monkeypatch.setattr(states, "do_fight_state", _refuse)
    monkeypatch.setattr(states, "mode_used_in_1v1", "Classic 1v1")
    monkeypatch.setattr(states.time, "sleep", lambda _seconds: None)

    result = states.state_tree(object(), logger, "1v1_fight", {}, states.StateHistory(logger), states.StateOrder())

    assert result == "stop"


def test_worker_stop_state_exits_nonzero(monkeypatch: pytest.MonkeyPatch) -> None:
    from pyclashbot.bot import worker as worker_module

    worker = worker_module.WorkerProcess({}, Queue(), Event(), "unused.log")
    calls: list[int] = []

    def _stop_once(*args: object) -> str:
        calls.append(1)
        return "stop"

    monkeypatch.setattr(worker_module, "state_tree", _stop_once)

    assert worker._run_bot_loop(object(), {}, ProcessLogger(None)) is False
    assert len(calls) == 1  # stopped instead of looping/restarting


def test_worker_run_exits_nonzero_on_config_stop(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from pyclashbot.bot import worker as worker_module

    worker = worker_module.WorkerProcess({}, Queue(), Event(), str(tmp_path / "worker.log"))
    monkeypatch.setattr(worker, "_setup_emulator", lambda *args: object())
    monkeypatch.setattr(worker, "_run_bot_loop", lambda *args: False)

    with pytest.raises(SystemExit) as excinfo:
        worker.run()

    assert excinfo.value.code == 1
