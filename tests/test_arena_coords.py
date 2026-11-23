"""Arena normalization and clickable-region clamps."""

from __future__ import annotations

from pyclashbot.bot.coords import (
    ARENA_PLAY_REGION_LTRB,
    PLAYABLE_PLAY_REGION_LTRB,
    clamp_to_playable,
    norm_to_px,
)

FRAME = (419, 633)


def _play_denorm(xy_norm, rect, frame_size):
    """Independent reference for Matt's play_denorm scaling."""
    left, top, right, bottom = rect
    sx = frame_size[0] / FRAME[0]
    sy = frame_size[1] / FRAME[1]
    return (
        round(left * sx + xy_norm[0] * (right - left) * sx),
        round(top * sy + xy_norm[1] * (bottom - top) * sy),
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


def test_norm_to_px_matches_play_denorm() -> None:
    for frame_size in ((419, 633), (838, 1266), (600, 1000)):
        for xy_norm in ((0.0, 0.0), (0.25, 0.75), (0.5, 0.5), (1.0, 1.0), (1.1, -0.1)):
            assert norm_to_px(xy_norm, frame_size=frame_size) == _play_denorm(
                xy_norm, ARENA_PLAY_REGION_LTRB, frame_size
            )


def test_norm_to_px_uses_explicit_rect() -> None:
    rect = (52, 57, 367, 476)
    assert norm_to_px((0.0, 0.0), rect=rect) == (52, 57)
    assert norm_to_px((1.0, 1.0), rect=rect) == (367, 476)


def test_clamp_to_playable_corners() -> None:
    assert clamp_to_playable((0, 0)) == (59, 67)
    assert clamp_to_playable((999, 999)) == (355, 467)


def test_clamp_to_playable_keeps_inside_points() -> None:
    assert clamp_to_playable((200, 300)) == (200, 300)


def test_clamped_effective_model_range_is_smaller_than_unit_square() -> None:
    assert norm_to_px((0.0, 0.0)) == (50, 57)
    assert clamp_to_playable(norm_to_px((0.0, 0.0))) == (59, 67)
    assert norm_to_px((1.0, 1.0)) == (367, 477)
    assert clamp_to_playable(norm_to_px((1.0, 1.0))) == (355, 467)


def test_arena_and_playable_rects_are_distinct() -> None:
    assert ARENA_PLAY_REGION_LTRB == (50, 57, 367, 477)
    assert PLAYABLE_PLAY_REGION_LTRB == (59, 67, 355, 467)
