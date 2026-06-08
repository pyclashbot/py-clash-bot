# Clash Royale integration tests

End-to-end pytest tests that drive the bot against a live emulator on **any**
supported backend (`memu`, `bluestacks`, `google-play`, `adb`). They are skipped
by a default `pytest` run; `--integration` turns them on.

Order, the shared emulator, and backend resolution live in `test_jobs.py` and
`../conftest.py`; add a job by appending its `run_test` to `SUITE`.

## Setup is automatic

No manual boot. During fixture construction the controller gets Clash to the main
menu — MEmu/BlueStacks/Google Play boot the VM, while `adb` attaches to an
already-running device and (re)launches Clash. If that can't be done (app missing,
signed out, no main menu) the run aborts fast with a clear message instead of
hanging. The first two `SUITE` entries then sanity-check the result:

1. `app_installed` — Clash Royale is installed (fails fast, never waits on install).
2. `screenshot_contract` — the capture pipeline returns a valid, non-black frame.

The remaining job tests assume the previous one left the emulator on the main
menu. Some still expect a populated account (≥2 accounts for `switch_account`, a
clan for the `clan_chat_*` tests); those fail with a clear message if unmet.

## Running

```
make test-emulator                      # resolve backend (cache / menu), boot, run
make test-emulator EMULATOR=bluestacks ADB_SERIAL=127.0.0.1:5555
uv run pytest -x --integration --emulator memu
```

`--integration` flips the default marker and selects a backend; precedence is
`--emulator` > cached pick (pytest's `config.cache`, under `.pytest_cache/`) >
`emulator_default` ini > interactive menu, all gated to backends available on this
OS. `--emulator`
is a one-off (not persisted); a menu pick and `--adb-serial` are sticky. `-x`
stops at the first failure. Run one entry by its `SUITE` id with `-k` (e.g.
`-k boot_and_reach_main_menu`, `-k 1v1_fight`).
