# py-clash-bot

A Clash Royale automation bot: drives an Android emulator via ADB and acts on the screen using OpenCV image recognition and hardcoded pixel checks. Treat it as a screen-scraping state machine — there is no game API.

## Commands

Targets live in the `Makefile` (`make setup`/`dev`/`lint`/`test`, `build-msi`/`build-dmg`, all via `uv`); `CONTRIBUTING.md` has dev setup. Non-obvious bits those don't tell you:
- Tests are **not** pytest — each `tests/**/test_*.py` runs as a standalone script (exit 0 = pass); `EMULATOR=memu make test` filters to `tests/<name>/`.
- `tests/clash-royale/` are integration tests needing a live MEmu VM and **do not run in CI**. CI only builds artifacts + runs pre-commit.
- MSI build = cx-freeze, DMG = pyinstaller; both inject the real version (see Cross-cutting rules).

## Architecture

`pyclashbot/__main__.py` wires the `interface/` GUI to a `bot/worker.py` `WorkerProcess` running in a separate process; they communicate over `multiprocessing` `Queue` (stats) + `Event` (shutdown). The worker runs a state-machine loop (`bot/states.py`) that calls `emulators/` for screen I/O and `detection/` for image recognition. Subdirectories under `pyclashbot/` have their own `AGENTS.md` — read it before editing that layer.

## Cross-cutting rules

- **Never call `time.sleep()`** — it is lint-banned. Use `interruptible_sleep()` from `pyclashbot.utils.cancellation` so shutdown is responsive. The active `CancellationToken` is thread-local; worker threads must `CancellationToken.set_current(token)`.
- **All screen coordinates are absolute to a fixed emulator resolution (~419×633).** There is no scaling — every click/pixel-check constant breaks if the resolution changes.
- Detection keeps multiple color palettes (with tolerance) to absorb emulator/app-version drift; add fallbacks, don't tighten thresholds.
- Always verify screen state (a `check_if_on_*` / detection call) **before** clicking. Never hardcode a raw click — use named coordinate constants or nav helpers.
- Persistent user settings go through `USER_SETTINGS_CACHE` (`pyclashbot.utils.caching`), keyed by `UIField.value` strings. Logging/stats go through `pyclashbot.utils.logger`; OS checks through `pyclashbot.utils.platform` (`is_windows()`/`is_macos()`).
- Version is a `v0.0.0` placeholder in `pyproject.toml`; the real version is injected from the git tag at build time and read at runtime from `pyclashbot/__version__` via `utils/versioning.py`.
- Python 3.12 only. Conventional-commit messages.
