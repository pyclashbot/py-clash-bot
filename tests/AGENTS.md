# tests/ — pytest, two tiers

Offline tests run in CI on a bare `pytest`. Emulator tests carry
`@pytest.mark.emulator` and need a live emulator — they are skipped by default
(`addopts = -m "not emulator"`) and **CI never runs them**. Turn them on with
`--integration` (or `make test-emulator`), which flips the marker to `-m emulator`
and resolves a backend.

## Layout

- `test_*.py` (top level) — offline unit/regression tests: pure functions +
  committed fixtures, no emulator (e.g. `test_card_fingerprint_bgr.py`,
  `test_emulator_resolution.py`).
- `clash_royale/` — live end-to-end suite: one parametrized test
  (`test_jobs.py`) over the ordered `SUITE`. The emulator is booted by `restart()`
  in the fixture (via `attach_emulator`); the first two entries are setup
  (app-installed check, screenshot smoke) and the rest are jobs. See `clash_royale/readme.md`.
- `_emulator_support.py` — not a test module: backend resolution and
  `attach_emulator()` behind the `emulator` fixture (cross-run persistence is
  pytest's `config.cache`, wired in `conftest.py`).
- `fixtures/` — committed regression inputs (e.g. captured BGR screenshots).

## Backend selection (`--integration`)

- Resolution precedence: `--emulator <alias>` > cached pick (pytest's own
  `config.cache`, under `.pytest_cache/`; inspect with `pytest --cache-show
  'pyclashbot/*'`, reset with `--cache-clear`) > `emulator_default` ini > interactive
  menu. Every candidate is gated to the platform's available backends
  (`available_cli_choices()`); an unsupported `--emulator` is a hard error, a stale
  cache/ini value is skipped. The menu lists only backends available on this OS.
- `--emulator` is a one-off override (not persisted); an interactive pick is. The
  optional `--adb-serial host:port` is sticky (persisted) and follows the same
  read precedence. Resolution runs in `conftest.py::pytest_configure` with capture
  suspended so the menu can read stdin; a non-TTY with nothing resolvable raises
  `pytest.UsageError` rather than hanging.

## Conventions

- The session-scoped `emulator` fixture attaches via `attach_emulator`, which
  constructs the controller (cheap discovery/config) then calls `restart()` to boot
  it; it `pytest.exit`s the whole run if either step fails. `restart()` launches
  Clash and reaches the main menu — MEmu/BlueStacks/Google Play boot the VM, while
  ADB attaches to an already-running device and (re)launches Clash. Either way a
  not-ready emulator (app missing, signed out, no main menu) fails fast there with
  a clear `EmulatorNotReadyError` rather than hanging on a GUI prompt.
- A clash entry is a `run_test(emulator, logger) -> (bool, str)`. Add one by
  appending its `run_test` to `SUITE` in `test_jobs.py`; entries run with `-x` and
  set up later ones, so order matters.
- Any test needing hardware must be marked `@pytest.mark.emulator` (or via SUITE
  membership), or CI will try to run it.
