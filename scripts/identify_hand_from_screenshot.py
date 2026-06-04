#!/usr/bin/env python3
"""Score hand slots on a 419x633 battle PNG against card_color_data fingerprints.

Uses BGR channel order (same as live emulator.screenshot / pre-684 bot).

Usage:
  uv run python scripts/identify_hand_from_screenshot.py path/to/battle.png
  uv run python scripts/identify_hand_from_screenshot.py battle.png --top 8
  uv run python scripts/identify_hand_from_screenshot.py battle.png --expect 0:evo_knight,3:berserker

Threshold matches production CARD_MATCH_THRESHOLD (1000): lower offset = closer match.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import numpy as np
from fingerprint_bgr import matches_expected, png_to_bgr_iar

from pyclashbot.bot import card_detection as cd

CARD_MATCH_THRESHOLD = cd.CARD_MATCH_THRESHOLD


def slot_has_card(iar: np.ndarray, slot: int) -> bool:
    x_coords, y_coords = cd.card_coords[slot]
    pixels = iar[np.ix_(y_coords, x_coords)]
    purple = np.all(np.abs(pixels - cd.purple_color) <= 30, axis=-1)
    return int(np.sum(purple)) >= 26


def score_slot(corners: list[dict]) -> list[tuple[int, str]]:
    arr = np.array([list(c.values()) for c in corners])
    scores: list[tuple[int, str]] = []
    for name, data in cd.card_color_data.items():
        _, offset = cd.calculate_offset(name, data, arr)
        scores.append((int(offset), name))
    scores.sort()
    return scores


def resolve_id(raw_id: str) -> str:
    return cd.CARD_DETECTION_ALIASES.get(raw_id, raw_id)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="Full-screen battle PNG (419x633)")
    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="How many closest cards to list per slot (default 5)",
    )
    parser.add_argument(
        "--expect",
        type=str,
        default="",
        help="Optional expected ids: 0:card_a,1:card_b (for pass/fail hints)",
    )
    parser.add_argument(
        "--slots",
        type=str,
        default="",
        help="Only score these slots, e.g. 0,1,2,3 (default: auto-detect filled slots)",
    )
    args = parser.parse_args()

    if not args.image.is_file():
        print(f"[!] Not found: {args.image}", file=sys.stderr)
        return 1

    iar = png_to_bgr_iar(args.image)
    cd.battle_iar = iar

    expected: dict[int, str] = {}
    if args.expect:
        for part in args.expect.split(","):
            idx_s, card = part.split(":", 1)
            expected[int(idx_s.strip())] = card.strip()

    if args.slots:
        slots = [int(s) for s in args.slots.split(",")]
    else:
        slots = [i for i in range(4) if slot_has_card(iar, i)]
        if not slots:
            slots = list(range(4))
            print("[!] No purple card frames detected; scoring all 4 slots anyway.\n")

    print(f"Image: {args.image}")
    print(f"Threshold: {CARD_MATCH_THRESHOLD} (UNKNOWN if best offset > threshold)\n")

    failures = 0
    for slot in slots:
        corners = cd.get_all_pixel_data(None, slot)
        scores = score_slot(corners)
        best_off, best_raw = scores[0]
        best_id = resolve_id(best_raw)
        group = cd.get_card_group(best_id)
        status = "OK" if best_off <= CARD_MATCH_THRESHOLD else "UNKNOWN"

        print(f"=== slot {slot} ===")
        print(f"  detect: {best_id} (raw: {best_raw})  offset: {best_off}  [{status}]  group: {group}")
        if slot in expected:
            exp = expected[slot]
            match = matches_expected(best_raw, best_id, exp)
            print(f"  expect: {exp}  -> {'PASS' if match else 'FAIL'}")
            if not match:
                failures += 1
        print(f"  top {args.top}:")
        for off, name in scores[: args.top]:
            mark = " <--" if off == best_off else ""
            alias = resolve_id(name)
            extra = f" -> {alias}" if alias != name else ""
            print(f"    {off:5d}  {name}{extra}{mark}")
        print()

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
