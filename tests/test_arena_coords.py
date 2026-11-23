"""Arena normalization and clickable-region clamps."""

from __future__ import annotations

import pytest

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


def test_norm_to_px_scales_with_frame_size() -> None:
    assert norm_to_px((0.0, 0.0), frame_size=(838, 1266)) == (100, 114)
    assert norm_to_px((0.5, 0.5), frame_size=(838, 1266)) == (417, 534)
    assert norm_to_px((1.0, 1.0), frame_size=(838, 1266)) == (734, 954)


@pytest.mark.parametrize(
    ("frame_size", "xy_norm", "expected"),
    [
        # Values pinned from Matt's play_denorm reference (not re-derived here).
        ((419, 633), (0.0, 0.0), (50, 57)),
        ((419, 633), (0.25, 0.75), (129, 372)),
        ((419, 633), (0.5, 0.5), (208, 267)),
        ((419, 633), (1.0, 1.0), (367, 477)),
        ((419, 633), (1.1, -0.1), (399, 15)),
        ((838, 1266), (0.0, 0.0), (100, 114)),
        ((838, 1266), (0.25, 0.75), (258, 744)),
        ((838, 1266), (0.5, 0.5), (417, 534)),
        ((838, 1266), (1.0, 1.0), (734, 954)),
        ((838, 1266), (1.1, -0.1), (797, 30)),
        ((600, 1000), (0.0, 0.0), (72, 90)),
        ((600, 1000), (0.25, 0.75), (185, 588)),
        ((600, 1000), (0.5, 0.5), (299, 422)),
        ((600, 1000), (1.0, 1.0), (526, 754)),
        ((600, 1000), (1.1, -0.1), (571, 24)),
    ],
)
def test_norm_to_px_matches_play_denorm(
    frame_size: tuple[int, int], xy_norm: tuple[float, float], expected: tuple[int, int]
) -> None:
    assert norm_to_px(xy_norm, frame_size=frame_size) == expected


def test_norm_to_px_uses_explicit_rect() -> None:
    rect = (52, 57, 367, 476)
    assert norm_to_px((0.0, 0.0), rect=rect) == (52, 57)
    assert norm_to_px((1.0, 1.0), rect=rect) == (367, 476)


def test_clamp_to_playable_corners() -> None:
    assert clamp_to_playable((0, 0)) == (59, 67)
    assert clamp_to_playable((999, 999)) == (355, 467)


def test_clamp_to_playable_keeps_inside_points() -> None:
    assert clamp_to_playable((200, 300)) == (200, 300)


def test_clamp_to_playable_scales_with_frame_size() -> None:
    assert clamp_to_playable(norm_to_px((0.0, 0.0), frame_size=(838, 1266)), frame_size=(838, 1266)) == (118, 134)
    assert clamp_to_playable(norm_to_px((1.0, 1.0), frame_size=(838, 1266)), frame_size=(838, 1266)) == (710, 934)


def test_clamped_effective_model_range_is_smaller_than_unit_square() -> None:
    assert norm_to_px((0.0, 0.0)) == (50, 57)
    assert clamp_to_playable(norm_to_px((0.0, 0.0))) == (59, 67)
    assert norm_to_px((1.0, 1.0)) == (367, 477)
    assert clamp_to_playable(norm_to_px((1.0, 1.0))) == (355, 467)


def test_arena_and_playable_rects_are_distinct() -> None:
    assert ARENA_PLAY_REGION_LTRB == (50, 57, 367, 477)
    assert PLAYABLE_PLAY_REGION_LTRB == (59, 67, 355, 467)
