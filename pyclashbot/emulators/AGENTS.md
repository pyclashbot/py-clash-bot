# emulators/ — emulator abstraction

`base.py` defines `BaseEmulatorController` (lifecycle: create → configure → start/restart/stop, plus click/swipe/screenshot/install_apk/start_app). `adb_base.py`'s `AdbBasedController` implements the interaction primitives over ADB shell and is shared by MEmu, BlueStacks, and Google Play; `adb.py` is the plain-device controller. `EmulatorType` in `__init__.py` gates support via each class's `supported_platforms`.

## Adding an emulator

- **Adapters are ports — keep bot policy out.** Retry counts, human prompts, give-up and mid-run-recovery decisions live in the caller (`bot/worker.py`, the test fixture), never in an adapter — so the contract stays drivable by integration tests with no GUI or env-var scaffolding.
- Subclass `AdbBasedController` if ADB-based — then you only implement `adb(command, binary_output)` and `_check_app_installed(package)`; everything else is inherited (including `is_app_installed`, `start_app`, and the default `is_reachable()`). `start_app` raises `EmulatorNotReadyError` if the app isn't installed — there is no install-wait prompt; the bot fails fast. Otherwise subclass `BaseEmulatorController` and implement all abstract methods, including `is_app_installed(package) -> bool`.
- `is_reachable() -> (ok, reason)` defaults to "a screenshot decodes to a non-empty array"; override it only if the backend exposes a truer liveness signal (MEmu checks VM running-state).
- Take `logger` as the first `__init__` arg; set `supported_platforms`. `__init__` does only cheap, side-effect-light discovery/config (paths, serials, config reads, VM/instance discovery+creation) — it does **not** boot. `restart()` is the boot primitive (stop → configure-while-stopped → start → launch Clash → reach main menu); it's called explicitly after construction, must leave Clash Royale on a main menu detectable by `check_if_on_clash_main_menu(self)`, and must `raise EmulatorNotReadyError` (never return `False`) on any not-ready failure.

## Gotchas

- The Clash Royale package id lives in `base.py` as `CLASH_ROYALE_PACKAGE` — never re-inline the `"com.supercell.clashroyale"` string.
- A not-ready emulator (app missing, signed out, no main menu, no clean instance) must `raise EmulatorNotReadyError` (from `base.py`) — never block on a GUI "Retry" prompt; there is no human-in-the-loop prompt path. `restart()` makes one boot attempt and raises on failure; the caller decides what to do (stop the bot on first boot, or fold it into the bounded mid-run restart net). Internal **timeout-bounded** waits are fine — unbounded retry loops are not.
- Screenshots are `screencap -p` → `cv2.imdecode` → **BGR** numpy, expected ~**419×633**; a size mismatch triggers retry/recovery. **Card fingerprints** use this BGR order as-is in `card_detection.py`. Some `state_detect` helpers flip to RGB via `[..., ::-1]` for pixel constants.
- Platform-locked: MEmu & Google Play are **Windows-only**; BlueStacks is Win+macOS. Gate paths with `is_windows()`/`is_macos()` from `utils.platform`.
- Render modes differ per emulator and are written to that emulator's config file then require stop→edit→restart (MEmu int 0/1; BlueStacks `dx`/`gl`/`vlcn`, macOS defaults `vlcn`; Google Play XML).
- BlueStacks uses a private ADB server (port 5041) and a dynamic per-instance device serial read from `bluestacks.conf`; instance reuse/creation goes through the Multi-Instance Manager — close it after renaming metadata.
