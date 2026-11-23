"""Stats queue flushing at shutdown."""

from __future__ import annotations

import queue as queue_module
from multiprocessing import Event, Queue
from typing import TYPE_CHECKING

import pytest

from pyclashbot.bot.worker import WorkerProcess
from pyclashbot.utils.logger import ProcessLogger, drain_stats_queue

if TYPE_CHECKING:
    from pathlib import Path


class _Queue:
    def __init__(self, *items: dict) -> None:
        self.items = list(items)

    def put_nowait(self, item: dict) -> None:
        self.items.append(item)

    def get_nowait(self) -> dict:
        if not self.items:
            raise queue_module.Empty
        return self.items.pop(0)


def test_process_logger_flush_publishes_once() -> None:
    stats_queue = _Queue()
    logger = ProcessLogger(stats_queue)
    logger.wins = 2
    logger.flush()
    logger.flush()

    assert len(stats_queue.items) == 1
    assert stats_queue.items[0]["wins"] == 2


def test_drain_stats_queue_returns_latest_and_consumes_once() -> None:
    stats_queue = _Queue({"wins": 1}, {"wins": 2})
    latest = drain_stats_queue(stats_queue, {"wins": 0})

    assert latest == {"wins": 2}
    assert stats_queue.items == []
    assert drain_stats_queue(stats_queue, latest) is latest


def test_worker_flushes_once_on_shutdown(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    stats_queue: Queue = Queue(maxsize=10)
    worker = WorkerProcess({}, stats_queue, Event(), str(tmp_path / "worker.log"))
    monkeypatch.setattr(worker, "_setup_emulator", lambda *args: object())
    monkeypatch.setattr(worker, "_run_bot_loop", lambda *args: False)

    with pytest.raises(SystemExit):
        worker.run()

    snapshot = stats_queue.get(timeout=1)
    assert snapshot["current_status"] == "Bot stopped"
    with pytest.raises(queue_module.Empty):
        stats_queue.get_nowait()
