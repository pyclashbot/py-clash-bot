# Clash Royale integration test suite

End-to-end pytest tests that exercise the bot against a real, running emulator.
The suite does **not** boot, restart, configure, or sign in to anything —
you set everything up by hand, then point pytest at your emulator.

These tests are marked `@pytest.mark.emulator`, so a bare `pytest` run (which
defaults to `-m "not emulator"`) **skips** them. You opt in explicitly with
`-m emulator --emulator <backend>`.

## Layout

```
tests/clash_royale/
├── test_jobs.py             # the entry point: one parametrized test over SUITE
├── readme.md                # you are here
├── navigation/
│   ├── test_navigate_main_pages.py   # eulerian circuit over all main-page edges
│   └── test_wait_for_main_menu.py    # launch-helper sanity check (not in SUITE)
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

Each job/nav module exposes a single function:

```python
def run_test(emulator, logger) -> tuple[bool, str]: ...
```

- `(True, "")` → pass
- `(False, "Didn't begin on clash main")` → precondition broken before the test ran
- `(False, "Failed during <step>")` → the test exercised the bot and the bot failed
- `(False, "Didn't end on clash main")` → the bot ran but didn't return to a clean state

`test_jobs.py` imports these into an ordered `SUITE` list and drives them through
one parametrized test, `test_clash_job`. The `SUITE` order is the single source
of truth; on failure the parametrized id and the returned message become the
pytest assertion message. The shared emulator is attached once (session-scoped
`emulator` fixture in `tests/conftest.py`), which also runs the precondition
check and aborts the whole run if it fails.

## Setup checklist (do this before running)

The `emulator` fixture refuses to test until **all** of these are true. If any
fail, pytest aborts the session with `ABORTING: can't test until …`.

1. **Pick an emulator backend** and install it. The suite supports any
   emulator the bot itself supports on your platform:
   - `memu` — MEmu (Windows only)
   - `bluestacks` — BlueStacks 5 (Windows + macOS)
   - `google-play` — Google Play Games (Windows only)
   - `adb` — any plain ADB-reachable device (always available)

   Run `uv run pytest --help | grep -A2 emulator` to see the live list of
   supported `--emulator` choices on your machine.
2. **Launch the emulator** and let it finish booting. The suite does NOT
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
`pyclashbot`) live in the `uv`-managed venv.

Run the whole clash suite (ordered, stop at first failure) against your
emulator. `-x` matters: later tests assume the previous one left the emulator
on the main menu, so stop-on-fail avoids chaining false negatives.

```
uv run pytest tests/clash_royale -m emulator -x --emulator memu
uv run pytest tests/clash_royale -m emulator -x --emulator bluestacks
uv run pytest tests/clash_royale -m emulator -x --emulator google-play
uv run pytest tests/clash_royale -m emulator -x --emulator adb
```

`make test-emulator EMULATOR=memu` runs every emulator-marked test (this clash
suite **plus** the `tests/memu/` infra tests) the same way.

Run a subset with `-k` (matches the parametrize ids) instead of the old
`--only` flag, or target one case by node id:

```
uv run pytest tests/clash_royale -m emulator --emulator memu -k clan_chat
uv run pytest tests/clash_royale -m emulator --emulator memu -k "1v1 or 2v2"
uv run pytest "tests/clash_royale/test_jobs.py::test_clash_job[select_battle_mode]" -m emulator --emulator memu
```

Expected output on a healthy setup (use `-v` for the per-id PASS/FAIL list):

```
tests/clash_royale/test_jobs.py::test_clash_job[nav_main_pages] PASSED
tests/clash_royale/test_jobs.py::test_clash_job[switch_account] PASSED
...
tests/clash_royale/test_jobs.py::test_clash_job[2v2_fight] PASSED

============================= 12 passed in ... =============================
```

Exit code `0` = all green; non-zero = a failure (or the precondition abort).

## Stop-on-fail and re-running

`-x` stops at the first failure; pytest's summary shows which parametrized id
failed and the message returned by its `run_test`. There's no "resume from id
N" — earlier tests double as setup for later ones (e.g. `select_battle_mode`
leaves a mode selected that `1v1_fight` relies on), so fix the cause and re-run
the suite.

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
2. Import its `run_test` in `test_jobs.py` and add an entry to the `SUITE`
   list at the position you want it to run (order is the source of truth).
3. Update this readme's layout section if needed.

To add a new navigation test, drop it in `navigation/` and wire it into `SUITE`
the same way.

Do **not** add an `if __name__ == "__main__":` block or a `test_*` function to
these job/nav modules — they expose only `run_test`. The marker, the shared
emulator fixture, and ordering all live in `test_jobs.py` / `conftest.py`.
