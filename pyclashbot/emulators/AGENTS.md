# emulators/ — emulator abstraction

`base.py` defines `BaseEmulatorController` (lifecycle: create → configure → start/restart/stop, plus click/swipe/screenshot/install_apk/start_app). `adb_base.py`'s `AdbBasedController` implements the interaction primitives over ADB shell and is shared by MEmu, BlueStacks, and Google Play; `adb.py` is the plain-device controller. `EmulatorType` in `__init__.py` gates support via each class's `supported_platforms`.

## Adding an emulator

- Subclass `AdbBasedController` if ADB-based — then you only implement `adb(command, binary_output)` and `_check_app_installed(package)`; everything else is inherited (including the install-wait prompt loop). Otherwise subclass `BaseEmulatorController` and implement all abstract methods.
- Take `logger` as the first `__init__` arg; set `supported_platforms`. `restart()` must leave Clash Royale on a main menu detectable by `check_if_on_clash_main_menu(self)`, else return `False` to trigger the retry loop.

## Gotchas

- Screenshots are `screencap -p` → `cv2.imdecode` → **BGR** numpy, expected ~**419×633**; a size mismatch triggers retry/recovery. **Card fingerprints** use this BGR order as-is in `card_detection.py`. Some `state_detect` helpers flip to RGB via `[..., ::-1]` for pixel constants.
- Platform-locked: MEmu & Google Play are **Windows-only**; BlueStacks is Win+macOS. Gate paths with `is_windows()`/`is_macos()` from `utils.platform`.
- Render modes differ per emulator and are written to that emulator's config file then require stop→edit→restart (MEmu int 0/1; BlueStacks `dx`/`gl`/`vlcn`, macOS defaults `vlcn`; Google Play XML).
- BlueStacks uses a private ADB server (port 5041) and a dynamic per-instance device serial read from `bluestacks.conf`; instance reuse/creation goes through the Multi-Instance Manager — close it after renaming metadata.
