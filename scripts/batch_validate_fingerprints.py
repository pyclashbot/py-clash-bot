#!/usr/bin/env python3
"""Batch-validate card fingerprints on labeled battle PNGs (BGR path).

Usage:
  uv run python scripts/batch_validate_fingerprints.py
  uv run python scripts/batch_validate_fingerprints.py path/to/battle.png

Optional CARD_FINGERPRINT_ASSETS directory for manifest PNGs when no paths are passed.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from fingerprint_bgr import validate_bgr_png

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


def assets_dir() -> Path | None:
    override = os.environ.get("CARD_FINGERPRINT_ASSETS")
    if override:
        return Path(override)
    local = REPO / "tests" / "fixtures" / "card_fingerprint_captures"
    return local if local.is_dir() else None


def find_manifest_key(path: Path) -> str | None:
    for key in MANIFEST:
        if key in path.name:
            return key
    return None


def main(argv: list[str]) -> int:
    if argv:
        paths = [Path(p) for p in argv]
    else:
        assets = assets_dir()
        paths = sorted(assets.glob("battle-screenshot-20260604-*.png")) if assets else []

    if not paths:
        print("No PNGs found.", file=sys.stderr)
        return 2

    fails = 0
    for path in paths:
        key = find_manifest_key(path)
        if not key:
            continue
        print(f"\n=== {path.name} ({key}) ===")
        for line in validate_bgr_png(path, MANIFEST[key]):
            print(line)
            if "FAIL" in line:
                fails += 1

    print(f"\n=== done: {fails} failing slot line(s) ===")
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
