# bot/ — automation state machine

`worker.py` runs the process lifecycle and an infinite loop calling `state_tree()` in `states.py`, which sequences jobs (upgrade → card_mastery → select_battle_mode → randomize/cycle deck → fight → end). Each state returns the next state name; a failed state returns `"restart"`, which restarts the emulator. The worker aborts after **5 consecutive restarts**.

## Adding or editing a state / navigation step

- Call a `check_if_on_*` detection (from `state_detect.py`) before acting; loop on `time.sleep()` with an explicit timeout (e.g. `wait_for_clash_main_menu()` waits up to 240s and clears reward popups mid-wait). Handle async popups before proceeding.
- Navigation is consolidated in `nav.py`: use `navigate_main_page(emulator, logger, start, end)` and the `NAV_CLICKS` table rather than ad-hoc click sequences. Deck pages use image matching on `DECK_TABS_REGION`.
- New coordinates go in `coords.py` as named constants — see the resolution warning in the root `AGENTS.md`. `NAV_CLICKS` itself references named constants from `coords.py`; don't inline raw tuples even inside the table.
- Pure detection helpers (`(emulator) → coords | None`) go in `find.py`. Pixel predicates (`check_if_on_*`, `pixel_indicates_*`) go in `state_detect.py`. `find.py` is leaf-only: it never imports from `pyclashbot.bot.*` except `coords` and `state_detect`.
- New feature jobs go in their own `<feature>_state.py` (see `clan_chat_state.py`, `account_switch.py`, `upgrade_state.py` for the shape). Wire into `states.py:state_tree()` last.

## Status messages

User-facing progress goes through `logger.change_status()` (updates the live status line and log). Use `logger.log()` for detail that should not replace the status line.

- **main menu** — home screen; not "clash main".
- **Clash Royale** — game/app name (especially emulator startup).
- **burger menu** — main-menu options overlay.
- Battle modes: **Classic 1v1**, **Classic 2v2**, **Trophy Road**, **Quick Match**.
- Use an em dash (`—`) for breaks: `Not on main menu — cannot start fight`.
- Sentence case; no function names or debug error codes in status text.
- Throttle repetitive wait-loop messages to ~once per second (see `wait_for_battle_start`, `wait_for_elixir`).

## Gotchas

- `states.py` carries **module-level globals** (`mode_used_in_1v1`, `fight_mode_cycle_index`) set in one state and read in later ones; if `mode_used_in_1v1` is `None`, fight/cycle states silently skip.
- `StateHistory` throttles expensive states (upgrade, card_mastery) by randomized time increments — a manually-triggered state won't re-run until its increment elapses.
- Card availability and deck tabs use **image recognition** (`card_detection.py`, `find_image`); elixir/battle/upgrade checks use **single-pixel** sampling — an off-by-one Y breaks them.
- **Card color fingerprints are BGR.** `battle_iar` is raw `emulator.screenshot()` (OpenCV BGR). Regression: `tests/test_card_fingerprint_bgr.py`.
