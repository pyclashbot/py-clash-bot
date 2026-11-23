"""Arena normalization and clickable-region clamps."""

from __future__ import annotations

from pyclashbot.bot.coords import (
    ARENA_PLAY_REGION_LTRB,
    PLAYABLE_PLAY_REGION_LTRB,
    clamp_to_playable,
    norm_to_px,
)


def test_norm_to_px_corners() -> None:
    assert norm_to_px((0.0, 0.0)) == (50, 57)
    assert norm_to_px((1.0, 1.0)) == (367, 477)


def test_norm_to_px_center() -> None:
    assert norm_to_px((0.5, 0.5)) == (208, 267)


def test_norm_to_px_does_not_clamp_out_of_range() -> None:
    assert norm_to_px((1.1, -0.1)) == (399, 15)


def test_clamp_to_playable_corners() -> None:
    assert clamp_to_playable((0, 0)) == (59, 67)
    assert clamp_to_playable((999, 999)) == (355, 467)


def test_clamp_to_playable_keeps_inside_points() -> None:
    assert clamp_to_playable((200, 300)) == (200, 300)


def test_norm_to_px_uses_state_arena_override() -> None:
    state = {"arena": {"rect_px": [52, 57, 367, 476]}}
    rect = state["arena"]["rect_px"]
    assert norm_to_px((0.0, 0.0), rect) == (52, 57)
    assert norm_to_px((1.0, 1.0), rect) == (367, 476)


def test_arena_and_playable_rects_are_distinct() -> None:
    assert ARENA_PLAY_REGION_LTRB == (50, 57, 367, 477)
    assert PLAYABLE_PLAY_REGION_LTRB == (59, 67, 355, 467)
