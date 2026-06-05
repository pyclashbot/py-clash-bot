# Clash Royale integration test suite

End-to-end tests that exercise the bot against a real, running emulator.
The suite does **not** boot, restart, configure, or sign in to anything —
you set everything up by hand, then point the runner at your emulator.

## Layout

```
tests/clash-royale/
├── test_all_clash.py        # the only entry point (run this)
├── readme.md                # you are here
├── navigation/
│   ├── test_navigate_main_pages.py   # eulerian circuit over all main-page edges
│   └── test_wait_for_main_menu.py    # standalone launch-helper sanity check
└── jobs/
    ├── test_switch_account.py        # switch slot 1 -> 2 -> 1
    ├── test_upgrade.py
    ├── test_card_mastery.py
    ├── test_clan_chat_claim.py
    ├── test_clan_chat_donate.py
    ├── test_clan_chat_request.py
    ├── test_select_battle_mode.py    # Classic 1v1, Classic 2v2, Trophy Road
    ├── test_randomize_deck.py
    ├── test_cycle_deck.py
    ├── test_1v1_fight.py             # start_fight -> do_fight_state -> end_fight_state
    └── test_2v2_fight.py             # same, Classic 2v2
```

Every test file exposes the same function shape:

```python
def run_test(emulator, logger) -> tuple[bool, str]: ...
```

- `(True, "")` → pass
- `(False, "Didn't begin on clash main")` → precondition broken before the test ran
- `(False, "Failed during <step>")` → the test exercised the bot and the bot failed
- `(False, "Didn't end on clash main")` → the bot ran but didn't return to a clean state

## Setup checklist (do this before running)

The runner refuses to test until **all** of these are true. If any fail, it
prints `ABORTING: can't test until …` and exits.

1. **Pick an emulator backend** and install it. The runner supports any
   emulator the bot itself supports on your platform:
   - `memu` — MEmu (Windows only)
   - `bluestacks` — BlueStacks 5 (Windows + macOS)
   - `google-play` — Google Play Games (Windows only)
   - `adb` — any plain ADB-reachable device (always available)

   Run `py tests/clash-royale/test_all_clash.py --help` to see the live
   list of supported emulators on your machine.
2. **Launch the emulator** and let it finish booting. The runner does NOT
   boot, configure, or restart anything for you — that's intentional, so
   tests never destroy your setup.
3. **Install + sign in to Clash Royale** on the emulator.
4. **Add at least 2 accounts** to the Clash Royale account list. The
   `test_switch_account` test switches from slot 1 → 2 → 1, so you need
   both slots to exist.
5. **Be in a clan.** The three clan-chat tests assume you can reach the
   clan-chat screen. Joining any random clan is fine; they no-op if there's
   nothing to claim/donate/request.
6. **Park the app on the main menu**, signed in to **account slot 1**.
   Dismiss any popups (chests, season pass, news, etc.) so the main-menu
   pixel checks pass.

## Run the suite

**Always invoke via `uv run`** — the project's dependencies (including
`pyclashbot`) live in the `uv`-managed venv. Running with plain `py` or
`python` will fail with `ModuleNotFoundError: No module named 'pyclashbot'`.

Specify which emulator the runner should attach to via `--emulator`:

```
uv run py tests/clash-royale/test_all_clash.py --emulator memu
uv run py tests/clash-royale/test_all_clash.py --emulator bluestacks
uv run py tests/clash-royale/test_all_clash.py --emulator google-play
uv run py tests/clash-royale/test_all_clash.py --emulator adb
```

Expected output on a healthy setup:

```
[+] preconditions OK: emulator exists, is open, on Clash main menu.

>>> RUNNING: nav: all main-page permutations
<<< PASS: nav: all main-page permutations
>>> RUNNING: job: switch_account
<<< PASS: job: switch_account
...
>>> RUNNING: job: 2v2_fight
<<< PASS: job: 2v2_fight

=================================================
TEST                              RESULT  MESSAGE
-------------------------------------------------
nav: all main-page permutations   PASS
job: switch_account               PASS
job: upgrade                      PASS
job: card_mastery                 PASS
job: clan_chat_claim              PASS
job: clan_chat_donate             PASS
job: clan_chat_request            PASS
job: select_battle_mode           PASS
job: randomize_deck               PASS
job: cycle_deck                   PASS
job: 1v1_fight                    PASS
job: 2v2_fight                    PASS
=================================================

OVERALL: PASS
```

Exit code `0` = all green, `1` = something failed (or precondition aborted).

## Linear stop-on-fail

The suite is linear and stops at the first failure. Later tests assume the
previous test left the emulator on the main menu, so continuing past a
failure would just chain false negatives. The pass/fail table marks every
test after the failure as `skipped (earlier failure)`.

If you want to investigate one specific failure, fix the cause and re-run
the whole suite — there's no built-in "resume from test N" because earlier
tests double as setup for later ones (e.g. `select_battle_mode` leaves a
mode selected, which `1v1_fight` relies on).

## How long does it take?

- Nav permutations: ~1–2 minutes (20 page transitions).
- Cheap jobs (upgrade, card_mastery, deck states, clan chat): seconds each
  when there's nothing to do; minutes when there is.
- `1v1_fight` and `2v2_fight`: a full real match each — **multiple minutes
  per fight**, depending on matchmaking and game length. These dominate the
  total runtime.

Plan for ~10–20 minutes for a green full run.

## Extending the suite

To add a new job test:

1. Create `jobs/test_<feature>.py` with a `run_test(emulator, logger) -> tuple[bool, str]`.
   - Begin with `wait_for_clash_main_menu(...)`.
   - Call the state function(s) you want to exercise.
   - End with `wait_for_clash_main_menu(...)` again.
   - Return `(True, "")` or `(False, "Failed during <step>")`.
2. Add an entry to the `job_files` list in `test_all_clash.py`.
3. Update this readme's layout and expected-output sections if needed.

To add a new navigation test, drop it in `navigation/` and wire it up the
same way.

Do **not** add an `if __name__ == "__main__":` block that boots its own
emulator. Tests are library modules; the runner owns emulator attachment.
