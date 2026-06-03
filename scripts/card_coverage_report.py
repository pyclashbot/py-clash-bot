#!/usr/bin/env python3
"""Print card fingerprint/group coverage gaps. Always exits 0 (informational only)."""

from __future__ import annotations

from pyclashbot.bot.card_detection import CARD_GROUPS, card_color_data

# Cards from the community wiki list (no + limited editions, no merge tactics-only labels).
SCOPE = """
bats berserker electro_dragon electro_giant electro_spirit evo_archers evo_baby_dragon
evo_barbarians evo_bats evo_bomber evo_cannon evo_dart_goblin evo_electro_dragon evo_executioner
evo_furnace evo_goblin_cage evo_goblin_drill evo_goblin_giant evo_hunter evo_ice_spirit
evo_inferno_dragon evo_knight evo_lumberjack evo_mega_knight evo_minion_horde evo_mortar
evo_musketeer evo_pekka evo_princess evo_royal_ghost evo_royal_giant evo_royal_hogs
evo_royal_recruits evo_skeleton_army evo_skeleton_barrel evo_skeletons evo_snowball evo_tesla
evo_valkyrie evo_wall_breakers evo_witch evo_wizard evo_zap executioner fire_spirit fisherman
goblin_demolisher guards heal hero_balloon hero_barb_barrel hero_bowler hero_dark_prince
hero_giant hero_goblins hero_ice_golem hero_knight hero_magic_archer hero_mega_minion
hero_mini_pekka hero_musketeer hero_tombstone hero_wizard ice_spirit lumberjack mega_minion
mother_witch musketeer rascals royal_recruits rune_giant spirit_empress suspicious_bush
three_musketeers vines zappies
""".split()

GROUPED = {card for cards in CARD_GROUPS.values() for card in cards}
FINGERPRINTED = set(card_color_data.keys())


def main() -> None:
    missing_group = sorted(set(SCOPE) - GROUPED)
    missing_fp_set = GROUPED - FINGERPRINTED
    missing_fp = sorted(missing_fp_set)
    missing_fp_scope = sorted(set(SCOPE) & missing_fp_set)

    print(f"Scope cards: {len(set(SCOPE))}")
    print(f"Grouped (all): {len(GROUPED)}")
    print(f"Fingerprinted: {len(FINGERPRINTED)}")
    print()
    if missing_group:
        print(f"Missing play group ({len(missing_group)}):")
        for card in missing_group:
            print(f"  - {card}")
    else:
        print("All scope cards have a play group.")
    print()
    print(f"In a play group but no fingerprint ({len(missing_fp)} total, {len(missing_fp_scope)} in scope):")
    for card in missing_fp_scope[:40]:
        print(f"  - {card}")
    if len(missing_fp_scope) > 40:
        print(f"  ... and {len(missing_fp_scope) - 40} more")


if __name__ == "__main__":
    main()
