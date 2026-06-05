# Clash Royale integration tests

End-to-end pytest tests that drive the bot against a **live, already-running**
emulator. They never boot, configure, or sign in to anything — you set the
emulator up by hand. All are marked `@pytest.mark.emulator`, so a default
`pytest` run skips them.

Order, the shared emulator, and the precondition gate live in `test_jobs.py`
and `../conftest.py`; add a job by appending its `run_test` to `SUITE`.

## Before running

The `emulator` fixture aborts (`ABORTING: can't test until …`) unless your
emulator is:

- parked on the Clash Royale **main menu**, signed in to slot 1, popups dismissed;
- holding **≥2 accounts** (`switch_account` round-trips slot 1 → 2 → 1);
- **in a clan** (the clan-chat tests need the clan-chat screen).

## Running

```
uv run pytest tests/clash_royale -m emulator -x --emulator memu
```

`--emulator` picks the backend (`memu`, `bluestacks`, `google-play`, `adb`).
`-x` stops at the first failure — later tests assume the previous one left the
emulator on the main menu. Narrow with `-k` (e.g. `-k clan_chat`).
`make test-emulator EMULATOR=memu` runs this plus the `tests/memu/` tests.
