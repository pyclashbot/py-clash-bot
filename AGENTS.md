# py-clash-bot

A Clash Royale automation bot: drives an Android emulator via ADB and acts on the screen using OpenCV image recognition and hardcoded pixel checks. Treat it as a screen-scraping state machine — there is no game API.

## Commands

Targets live in the `Makefile` (`make setup`/`dev`/`lint`/`test`, `build-msi`/`build-dmg`, all via `uv`); `CONTRIBUTING.md` has dev setup. Non-obvious bits those don't tell you:
- Tests are **pytest**, offline by default (`addopts = -m "not emulator"`). Hardware tests carry `@pytest.mark.emulator`: `make test` runs only offline tests; `make test-emulator` runs the live-emulator suite. `--integration` flips the marker and resolves a backend (`--emulator`/cache/menu, platform-gated); the `emulator` fixture boots the emulator via `restart()`. See `tests/AGENTS.md`.
- The clash suite is one parametrized test (`tests/clash_royale/test_jobs.py`) over an ordered `SUITE` list — add a job by appending its `run_test` to `SUITE`. Shared emulator + backend resolution live in `tests/conftest.py` + `tests/_emulator_support.py`. Select with `-k`, stop at first failure with `-x`.
- `tests/clash_royale/` needs a live emulator and **does not run in CI** (CI only builds artifacts + runs pre-commit).
- MSI build = cx-freeze, DMG = pyinstaller; both inject the real version (see Cross-cutting rules).

## Architecture

`pyclashbot/__main__.py` wires the `interface/` GUI to a `bot/worker.py` `WorkerProcess` running in a separate process; they communicate over `multiprocessing` `Queue` (stats) + `Event` (shutdown). The worker runs a state-machine loop (`bot/states.py`) that calls `emulators/` for screen I/O and `detection/` for image recognition. Subdirectories under `pyclashbot/` have their own `AGENTS.md` — read it before editing that layer.

## Cross-cutting rules

- **Never call `time.sleep()`** — it is lint-banned. Use `interruptible_sleep()` from `pyclashbot.utils.cancellation` so shutdown is responsive. The active `CancellationToken` is thread-local; worker threads must `CancellationToken.set_current(token)`.
- **All screen coordinates are absolute to a fixed emulator resolution (~419×633).** There is no scaling — every click/pixel-check constant breaks if the resolution changes.
- **All screen coordinates live in `pyclashbot/bot/coords.py`** as named constants. Never inline a raw `emulator.click(150, 320)` — promote to a `NAMED_COORD = (150, 320)` and click via `emulator.click(*NAMED_COORD)`. The only documented exception is `PLAY_COORDS` in `card_detection.py` (large card-name → coords dict, kept with card detection).
- **Pure detection helpers live in `pyclashbot/bot/find.py`.** Anything shaped like `(emulator) → coords | None` belongs there. `find.py` is a **leaf module** — it imports only from `pyclashbot.detection.*`, `pyclashbot.utils.*`, `pyclashbot.bot.coords`, and `pyclashbot.bot.state_detect`. Never from other `pyclashbot.bot.*` modules.
- **Pixel/state predicates live in `pyclashbot/bot/state_detect.py`.** `check_if_on_*(emulator) → bool` and small `pixel_indicates_*(bgr) → bool` helpers all live here.
- **Main-page navigation goes through `nav.py`'s `navigate_main_page(emulator, logger, start, end)`** + the `NAV_CLICKS` table. Don't re-implement bottom-nav clicks in feature modules; extend `NAV_CLICKS` instead.
- Detection keeps multiple color palettes (with tolerance) to absorb emulator/app-version drift; add fallbacks, don't tighten thresholds.
- **`emulator.screenshot()` is BGR; card fingerprints must match that channel order.** Regression: `tests/test_card_fingerprint_bgr.py`.
- Always verify screen state (a `check_if_on_*` / detection call) **before** clicking. Never hardcode a raw click — use named coordinate constants or nav helpers.
- Persistent user settings go through `USER_SETTINGS_CACHE` (`pyclashbot.utils.caching`), keyed by `UIField.value` strings. Logging/stats go through `pyclashbot.utils.logger`; OS checks through `pyclashbot.utils.platform` (`is_windows()`/`is_macos()`).
- Version is a `v0.0.0` placeholder in `pyproject.toml`; the real version is injected from the git tag at build time and read at runtime from `pyclashbot/__version__` via `utils/versioning.py`.
- Python 3.12 only. Conventional-commit messages.

## Where new code goes

| You're adding… | Put it in… |
|---|---|
| A new screen coordinate / button position | `pyclashbot/bot/coords.py` |
| A pure "find this thing on screen" helper | `pyclashbot/bot/find.py` |
| A "is this screen visible" predicate | `pyclashbot/bot/state_detect.py` |
| A new main-page transition | extend `NAV_CLICKS` in `pyclashbot/bot/nav.py` |
| A new feature state (e.g. clan war, shop daily) | new `pyclashbot/bot/<feature>_state.py`, modeled on `clan_chat_state.py` or `account_switch.py` |
| A new image template | `pyclashbot/detection/reference_images/<folder>/*.png`, then call `find_image(..., "<folder>")` |
