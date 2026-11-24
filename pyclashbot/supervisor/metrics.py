"""Per-guest counters and a deterministic snapshot for status/JSON output."""

from __future__ import annotations

import threading
import time
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass(slots=True)
class GuestMetrics:
    serial: str
    index: int | None = None
    wins: int = 0
    losses: int = 0
    fights: int = 0
    restarts: int = 0
    ready: bool = False
    last_heartbeat: float = 0.0

    def record_fight(self, *, won: bool) -> None:
        self.fights += 1
        if won:
            self.wins += 1
        else:
            self.losses += 1

    def mark_ready(self) -> None:
        self.ready = True

    def mark_unready(self) -> None:
        self.ready = False

    def record_restart(self) -> None:
        self.restarts += 1

    def heartbeat(self, now: float) -> None:
        self.last_heartbeat = now

    @property
    def win_rate(self) -> float:
        return 0.0 if self.fights == 0 else self.wins / self.fights

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["win_rate"] = round(self.win_rate, 4)
        return payload


class MetricsRegistry:
    """Thread-safe metrics keyed by explicit serial."""

    def __init__(self, *, clock: Callable[[], float] = time.time) -> None:
        self._clock = clock
        self._lock = threading.Lock()
        self._metrics: dict[str, GuestMetrics] = {}

    def for_guest(self, serial: str, *, index: int | None = None) -> GuestMetrics:
        with self._lock:
            metrics = self._metrics.get(serial)
            if metrics is None:
                metrics = GuestMetrics(serial=serial, index=index)
                self._metrics[serial] = metrics
            elif index is not None:
                metrics.index = index
            return metrics

    def update(self, serial: str, /, **changes: Any) -> GuestMetrics:
        with self._lock:
            metrics = self._metrics.get(serial)
            if metrics is None:
                metrics = GuestMetrics(serial=serial)
                self._metrics[serial] = metrics
            for name, value in changes.items():
                if not hasattr(metrics, name) or name == "serial":
                    raise AttributeError(f"unknown metric {name!r} for {serial!r}")
                setattr(metrics, name, value)
            return metrics

    def record_fight(self, serial: str, *, won: bool) -> GuestMetrics:
        with self._lock:
            metrics = self._metrics.get(serial)
            if metrics is None:
                metrics = GuestMetrics(serial=serial)
                self._metrics[serial] = metrics
            metrics.record_fight(won=won)
            metrics.heartbeat(self._clock())
            return metrics

    def record_restart(self, serial: str) -> GuestMetrics:
        with self._lock:
            metrics = self._metrics.get(serial)
            if metrics is None:
                metrics = GuestMetrics(serial=serial)
                self._metrics[serial] = metrics
            metrics.record_restart()
            metrics.heartbeat(self._clock())
            return metrics

    def heartbeat(self, serial: str) -> GuestMetrics:
        with self._lock:
            metrics = self._metrics.get(serial)
            if metrics is None:
                metrics = GuestMetrics(serial=serial)
                self._metrics[serial] = metrics
            metrics.heartbeat(self._clock())
            return metrics

    def snapshot(self) -> list[dict[str, Any]]:
        """Stable ordering (by serial) so JSON stays diffable."""
        with self._lock:
            ordered = sorted(self._metrics.values(), key=lambda item: item.serial)
            return [metrics.to_dict() for metrics in ordered]

    def totals(self) -> dict[str, int]:
        with self._lock:
            return {
                "guests": len(self._metrics),
                "fights": sum(item.fights for item in self._metrics.values()),
                "wins": sum(item.wins for item in self._metrics.values()),
                "losses": sum(item.losses for item in self._metrics.values()),
                "restarts": sum(item.restarts for item in self._metrics.values()),
            }

    def to_dict(self) -> dict[str, Any]:
        return {"totals": self.totals(), "guests": self.snapshot()}
