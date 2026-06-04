# Reference screenshots (419×633)

Used by `scripts/generate_placement_map.py` to visualize card placement tap points.

See [../placement-zones.md](../placement-zones.md) for the committed overlay map and group summary.

## Battle overlay map

1. Start a battle in the emulator (resolution **419×633**, density 160 — same as the bot).
2. Pause or play until the arena is visible (troops optional; empty lane is fine).
3. Save a full-frame PNG as:

   `docs/reference/battle-screenshot.png`

4. Generate the overlay:

   ```bash
   uv run python scripts/generate_placement_map.py
   ```

   Output: `docs/placement-zones-overlay.png`

### Capture options

| Platform | How |
|----------|-----|
| **Windows + MEmu** | Run bot or `tests/memu/test_screenshot.py`, save `emulator.screenshot()` to the path above, or use MEmu’s screenshot tool. |
| **ADB** | `adb exec-out screencap -p > docs/reference/battle-screenshot.png` then verify size is 419×633. |
| **Manual** | Screenshot the emulator window; crop to the game field only if the image is exactly 419×633. |

If the file is missing, the script still writes a green **schematic** at `docs/placement-zones-map.png` and prints instructions.

### Tips

- Use a **1v1 ladder** frame (not clan chat or menus) so the arena matches play coordinates.
- Coordinates in code assume **your side is the bottom** of the image (hand/elixir at bottom).
- Regenerate after any `PLAY_COORDS` edit.
