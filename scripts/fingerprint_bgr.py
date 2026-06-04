"""BGR fingerprint helpers — matches live bot (emulator.screenshot, no channel flip)."""

from __future__ import annotations

import re
from pathlib import Path  # noqa: TC003

import cv2
import numpy as np
from PIL import Image

from pyclashbot.bot import card_detection as cd

COLOR_KEYS = list(cd.COLORS.keys())


def png_to_bgr_iar(path: Path) -> np.ndarray:
    rgb = np.array(Image.open(path).convert("RGB"))
    if rgb.shape[:2] != (633, 419):
        msg = f"expected 419x633, got {rgb.shape[1]}x{rgb.shape[0]}: {path}"
        raise ValueError(msg)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def extract_corners_from_bgr_iar(iar: np.ndarray, slot: int) -> list[dict[str, int]]:
    cd.battle_iar = iar
    raw = cd.get_all_pixel_data(None, slot)
    return [{k: int(v) for k, v in corner.items()} for corner in raw]


def extract_corners_from_png(path: Path, slot: int) -> list[dict[str, int]]:
    return extract_corners_from_bgr_iar(png_to_bgr_iar(path), slot)


def corners_to_numpy(corners: list[dict[str, int]]) -> list[np.ndarray]:
    return [np.array([corner[k] for k in COLOR_KEYS], dtype=np.int64) for corner in corners]


def self_offset(card_id: str, corners: list[dict[str, int]]) -> int:
    arr = corners_to_numpy(corners)
    data = corners_to_numpy(corners)
    _, off = cd.calculate_offset(card_id, data, arr)
    return int(off)


def matches_expected(raw: str, got: str, expected: str) -> bool:
    if expected in (got, raw):
        return True
    for variant, canonical in cd.CARD_DETECTION_ALIASES.items():
        if canonical == expected and raw in (variant, canonical):
            return True
    return False


def validate_bgr_png(path: Path, expect: dict[int, str]) -> list[str]:
    iar = png_to_bgr_iar(path)
    cd.battle_iar = iar
    lines: list[str] = []
    for slot, card_id in sorted(expect.items()):
        corners = extract_corners_from_bgr_iar(iar, slot)
        raw = cd.find_closest_card(corners)
        got = cd.CARD_DETECTION_ALIASES.get(raw, raw)
        off = self_offset(card_id, corners)
        ok = matches_expected(raw, got, card_id) and off <= cd.CARD_MATCH_THRESHOLD
        lines.append(
            f"  slot {slot} {card_id}: {'PASS' if ok else 'FAIL'} detect={got} raw={raw} offset={off}",
        )
    return lines


def format_corner_dict(corner: dict[str, int]) -> str:
    lines = ["        {"]
    for key in COLOR_KEYS:
        lines.append(f'            "{key}": {corner[key]},')
    lines.append("        },")
    return "\n".join(lines)


def format_card_block(card_id: str, corners: list[dict[str, int]]) -> str:
    parts = [f'    "{card_id}": [']
    for corner in corners:
        parts.append(format_corner_dict(corner))
    parts.append("    ],")
    return "\n".join(parts)


def replace_card_block(content: str, card_id: str, corners: list[dict[str, int]]) -> str:
    pattern = rf'    "{re.escape(card_id)}": \[\n.*?\n    \],'
    block = format_card_block(card_id, corners)
    new_content, n = re.subn(pattern, block, content, count=1, flags=re.DOTALL)
    if n != 1:
        raise ValueError(f"could not replace fingerprint block for {card_id!r} (matches={n})")
    return new_content
