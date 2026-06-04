# Card placement zones

The bot picks a **play group** for each detected card, then taps a random point from that group’s left or right lane (`PLAY_COORDS` in `pyclashbot/bot/card_detection.py`).

## Reference map

![Placement zones overlay](placement-zones-overlay.png)

- **Your side** is the **bottom** of the image; **enemy** is the top.
- **Shape + color** = play group (see legend at the bottom of the image).
- Example: yellow **stars** = `center_spell`; red **circles** = `bridge_line`; pink **squares** = `spirit` (uses building coords on your side).

A green **schematic** (no battle screenshot required) is at [placement-zones-map.png](placement-zones-map.png).

## Play groups (summary)

| Group | Arena area |
|-------|------------|
| `king_lane` | Deep lane / behind king |
| `princess` | Princess lane |
| `bridge_line` | Bridge line (tanks, heavies) |
| `bridge_rush` | In front of bridge |
| `back_support` | Behind bridge |
| `defense_building` | Back-field buildings |
| `siege_building` | Mortar / X-Bow |
| `center_spell` | Center behind river |
| `lane_spell` | Standard spell lane |
| `reactive_spell` | Reactive spells (Zap, Heal, Vines, …) |
| `spirit` | Spirits (your side; coords match `defense_building` for now) |
| `rocket`, `tornado`, `goblin_barrel`, `graveyard`, `miner`, `goblin_drill` | Card-specific |

Full card → group list lives in `CARD_GROUPS` in `card_detection.py` (177 ids including pre-fingerprint evo/hero variants).

## Regenerate the map

After changing `PLAY_COORDS` or `CARD_GROUPS`:

1. Optional: save a mid-battle **419×633** screenshot as `docs/reference/battle-screenshot.png` (gitignored; see [reference/README.md](reference/README.md)).
2. Run:

   ```bash
   uv run python scripts/generate_placement_map.py
   ```

   Writes `docs/placement-zones-overlay.png` (and updates the schematic).

**BlueStacks (macOS):**

```bash
BS="/Applications/BlueStacks.app/Contents/MacOS/hd-adb"
export ADB_SERVER_PORT=5041
"$BS" devices   # note serial, e.g. emulator-5574
"$BS" -s emulator-5574 exec-out screencap -p > docs/reference/battle-screenshot.png
uv run python scripts/generate_placement_map.py
```
