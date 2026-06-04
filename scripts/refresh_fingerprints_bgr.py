#!/usr/bin/env python3
"""Re-extract card_color_data fingerprints from battle PNGs on the BGR path.

Matches pre-684 bot behavior (raw emulator.screenshot channel order).

Usage:
  uv run python scripts/refresh_fingerprints_bgr.py
  uv run python scripts/refresh_fingerprints_bgr.py --dry-run

Set CARD_FINGERPRINT_ASSETS to a directory of labeled 419x633 battle PNGs
(default: tests/fixtures/card_fingerprint_captures if that directory exists).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from fingerprint_bgr import (
    extract_corners_from_png,
    replace_card_block,
    self_offset,
)


def assets_dir() -> Path | None:
    override = os.environ.get("CARD_FINGERPRINT_ASSETS")
    if override:
        return Path(override)
    local = REPO / "tests" / "fixtures" / "card_fingerprint_captures"
    return local if local.is_dir() else None


# Labeled trainer captures (timestamp key in filename)
MANIFEST: dict[str, dict[int, str]] = {
    "152301": {0: "mini_pekka", 1: "pekka", 2: "giant", 3: "royal_giant"},
    "152408": {0: "golem", 1: "lava_hound", 2: "vines", 3: "three_musketeers"},
    "153010": {0: "lumberjack", 1: "ram_rider", 2: "ice_wizard", 3: "hero_bowler"},
    "153102": {0: "mortar", 1: "ice_spirit", 2: "musketeer", 3: "evo_royal_giant"},
    "153651": {0: "electro_spirit", 1: "goblins", 2: "heal_spirit", 3: "minions"},
    "153735": {0: "spear_goblins", 1: "fire_spirit", 2: "skeletons", 3: "evo_mortar"},
    "154539": {0: "ice_spirit", 1: "hero_goblins", 2: "mother_witch", 3: "guards"},
    "154554": {0: "zap", 1: "hero_goblins", 2: "giant_skeleton", 3: "guards"},
    "154626": {0: "goblin_gang", 1: "bats", 2: "mother_witch", 3: "zap"},
    "154703": {0: "hero_goblins", 1: "giant_skeleton", 2: "evo_ice_spirit", 3: "guards"},
    "155328": {0: "evo_zap", 1: "minion_horde", 2: "inferno_dragon", 3: "electro_giant"},
    "155410": {0: "evo_bats", 1: "ice_golem", 2: "electro_wizard", 3: "royal_ghost"},
    "172417": {0: "hero_knight", 1: "fisherman", 2: "phoenix", 3: "sparky"},
    "172502": {0: "zappies", 1: "mirror", 2: "elixir_collector", 3: "rascals"},
    "173904": {0: "rune_giant", 1: "electro_dragon", 2: "goblin_demolisher", 3: "royal_recruits"},
    "173951": {0: "mega_minion", 1: "evo_knight", 2: "suspicious_bush", 3: "berserker"},
    "174707": {0: "goblin_giant", 1: "evo_goblin_cage", 2: "elixir_golem", 3: "spirit_empress_air"},
    "174902": {0: "evo_baby_dragon", 1: "hero_barb_barrel", 2: "elixir_golem", 3: "spirit_empress_ground"},
    "175916": {0: "electro_spirit", 1: "evo_tesla", 2: "hero_magic_archer", 3: "evo_archers"},
    "182427": {0: "fisherman", 1: "spirit_empress_air", 2: "phoenix", 3: "mega_minion"},
}

# PR #680 / #682 ids — refreshed when present in MANIFEST PNGs above
PR_680_682_TOUCHED = {
    "electro_spirit",
    "fisherman",
    "phoenix",
    "mega_minion",
    "spirit_empress_air",
    "spirit_empress_ground",
    "goblins",
    "heal_spirit",
    "minions",
    "spear_goblins",
    "zap",
    "mini_pekka",
    "pekka",
    "giant",
    "royal_giant",
    "golem",
    "lava_hound",
    "vines",
    "three_musketeers",
    "lumberjack",
    "ram_rider",
    "ice_wizard",
    "hero_bowler",
    "mortar",
    "ice_spirit",
    "musketeer",
    "evo_royal_giant",
    "fire_spirit",
    "skeletons",
    "evo_mortar",
    "hero_goblins",
    "mother_witch",
    "guards",
    "giant_skeleton",
    "goblin_gang",
    "bats",
    "evo_ice_spirit",
    "evo_zap",
    "minion_horde",
    "inferno_dragon",
    "electro_giant",
    "evo_bats",
    "ice_golem",
    "electro_wizard",
    "royal_ghost",
}


def find_pngs() -> dict[str, Path]:
    found: dict[str, Path] = {}
    assets = assets_dir()
    if assets is None:
        return found
    for path in sorted(assets.glob("battle-screenshot-20260604-*.png")):
        for key in MANIFEST:
            if key in path.name and key not in found:
                found[key] = path
    return found


def collect_updates() -> dict[str, list[dict[str, int]]]:
    pngs = find_pngs()
    updates: dict[str, list[dict[str, int]]] = {}
    best_off: dict[str, int] = {}

    for key, expect in MANIFEST.items():
        path = pngs.get(key)
        if path is None:
            print(f"[!] missing PNG for {key}", file=sys.stderr)
            continue
        for slot, card_id in expect.items():
            corners = extract_corners_from_png(path, slot)
            off = self_offset(card_id, corners)
            prev = best_off.get(card_id)
            if prev is None or off < prev:
                updates[card_id] = corners
                best_off[card_id] = off
                print(f"  {card_id} <- {path.name} slot {slot} (self_offset={off})")

    return updates


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="validate only, do not write file")
    args = parser.parse_args()

    print("Collecting BGR fingerprints from manifest PNGs...")
    updates = collect_updates()
    print(f"\n{len(updates)} card(s) to update")

    touched_682 = sorted(PR_680_682_TOUCHED & set(updates))
    print(f"Includes {len(touched_682)} #680/#682 ids with source PNGs")

    missing_682 = sorted(PR_680_682_TOUCHED - set(updates.keys()))
    if missing_682:
        print(f"\n[!] #680/#682 ids still need a labeled PNG (not in manifest): {len(missing_682)}")
        for card in missing_682[:20]:
            print(f"    - {card}")
        if len(missing_682) > 20:
            print(f"    ... and {len(missing_682) - 20} more")

    if args.dry_run:
        print("\n(dry-run: card_detection.py not modified)")
        return 0

    card_path = REPO / "pyclashbot" / "bot" / "card_detection.py"
    content = card_path.read_text(encoding="utf-8")
    for card_id in sorted(updates):
        content = replace_card_block(content, card_id, updates[card_id])
    card_path.write_text(content, encoding="utf-8")
    print(f"\nWrote {len(updates)} blocks to {card_path}")

    print("\nRe-validating with fresh import (BGR)...")
    import subprocess

    png_args = [str(p) for p in find_pngs().values()]
    proc = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "batch_validate_fingerprints.py"), *png_args],
        cwd=str(REPO),
        check=False,
    )
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
