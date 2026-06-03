# bot/ — automation state machine

`worker.py` runs the process lifecycle and an infinite loop calling `state_tree()` in `states.py`, which sequences jobs (upgrade → card_mastery → select_battle_mode → randomize/cycle deck → fight → end). Each state returns the next state name; a failed state returns `"restart"`, which restarts the emulator. The worker aborts after **5 consecutive restarts**.

## Adding or editing a state / navigation step

- Call a `check_if_on_*` detection before acting; loop on `interruptible_sleep()` with an explicit timeout (e.g. `wait_for_clash_main_menu()` waits up to 240s and clears reward popups mid-wait). Handle async popups before proceeding.
- Navigation is consolidated in `nav.py` (post nav-refactor): use `navigate_main_page(emulator, logger, start, end)` and the `NAV_CLICKS` table rather than ad-hoc click sequences. Deck pages use image matching on `DECK_TABS_REGION`.
- New coordinates go in `coords.py` as named constants — see the resolution warning in the root `AGENTS.md`.

## Gotchas

- `states.py` carries **module-level globals** (`mode_used_in_1v1`, `fight_mode_cycle_index`) set in one state and read in later ones; if `mode_used_in_1v1` is `None`, fight/cycle states silently skip.
- `StateHistory` throttles expensive states (upgrade, card_mastery) by randomized time increments — a manually-triggered state won't re-run until its increment elapses.
- Card availability and deck tabs use **image recognition** (`card_detection.py`, `find_image`); elixir/battle/upgrade checks use **single-pixel** sampling — an off-by-one Y breaks them.
