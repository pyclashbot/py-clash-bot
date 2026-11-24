"""Per-guest counters and deterministic snapshots."""

from __future__ import annotations

import pytest

from pyclashbot.supervisor.metrics import GuestMetrics, MetricsRegistry


def test_guest_metrics_track_fights_and_win_rate() -> None:
    metrics = GuestMetrics(serial="127.0.0.1:5570", index=0)
    metrics.record_fight(won=True)
    metrics.record_fight(won=False)
    metrics.record_fight(won=True)

    assert (metrics.wins, metrics.losses, metrics.fights) == (2, 1, 3)
    assert metrics.win_rate == pytest.approx(2 / 3)


def test_zero_fights_has_zero_win_rate() -> None:
    assert GuestMetrics(serial="s").win_rate == 0.0


def test_registry_clock_heartbeat_and_snapshot_order() -> None:
    now = [100.0]
    registry = MetricsRegistry(clock=lambda: now[0])
    registry.for_guest("b", index=1)
    registry.for_guest("a", index=0)

    registry.record_fight("b", won=True)
    registry.record_restart("a")
    now[0] = 200.0
    registry.heartbeat("a")

    snapshot = registry.snapshot()
    assert [row["serial"] for row in snapshot] == ["a", "b"]
    assert snapshot[0]["restarts"] == 1
    assert snapshot[0]["last_heartbeat"] == 200.0
    assert snapshot[1]["wins"] == 1
    assert registry.totals() == {"guests": 2, "fights": 1, "wins": 1, "losses": 0, "restarts": 1}


def test_update_rejects_unknown_fields() -> None:
    registry = MetricsRegistry()
    registry.for_guest("a")
    with pytest.raises(AttributeError):
        registry.update("a", bogus=1)
    with pytest.raises(AttributeError):
        registry.update("a", serial="b")


def test_to_dict_wraps_totals_and_guests() -> None:
    registry = MetricsRegistry()
    registry.for_guest("a", index=0)
    payload = registry.to_dict()
    assert payload["totals"]["guests"] == 1
    assert payload["guests"][0]["serial"] == "a"
