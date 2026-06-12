"""Backend selection and attachment behind the `emulator` fixture (conftest.py).

Not a test module. Resolves which emulator backend to drive (CLI arg > cached
choice > committed default > interactive menu, all gated to the platform's
available backends), persists interactive picks, and attaches to it.
"""

from __future__ import annotations

import inspect
import sys
from typing import TYPE_CHECKING

import pytest

from pyclashbot.emulators.adb_base import validate_device_serial
from pyclashbot.emulators.base import EmulatorNotReadyError

if TYPE_CHECKING:
    from collections.abc import Callable

    from pyclashbot.utils.logger import Logger

# CLI alias -> EmulatorType key. Lowercase, dash-separated for friendly CLI.
CLI_ALIASES = {
    "memu": "MEmu",
    "bluestacks": "BlueStacks 5",
    "google-play": "Google Play Games",
    "adb": "ADB Device",
}


def available_cli_choices() -> list[str]:
    from pyclashbot.emulators import EmulatorType, get_available_emulators

    available = set(get_available_emulators())
    return [cli for cli, display in CLI_ALIASES.items() if EmulatorType(display) in available]


def prompt_backend_menu(choices: list[str]) -> str | None:
    """Numbered stdin menu over the platform-available backends. None on abort."""
    if not choices:
        return None
    print("\nSelect emulator backend:")
    for i, choice in enumerate(choices, 1):
        print(f"  {i}) {choice}")
    try:
        raw = input(f"Enter choice [1-{len(choices)}]: ").strip()
    except (EOFError, KeyboardInterrupt):
        return None
    if raw.isdigit() and 1 <= int(raw) <= len(choices):
        return choices[int(raw) - 1]
    return None


def resolve_backend(
    cli_opt: str | None,
    cache: dict,
    ini_default: str,
    choices: list[str],
    interactive_cb: Callable[[list[str]], str | None],
) -> tuple[str, bool]:
    """Resolve the backend alias against the platform-available `choices`.

    Precedence: cli_opt > cache > ini_default > interactive menu. Returns
    (backend, persist); persist is True only for an interactive pick. An explicit
    cli_opt unsupported on this platform is a hard error, whereas a stale cache or
    committed default is silently skipped so resolution falls through. `interactive_cb`
    is invoked only when nothing else resolves, and returns None when it can't prompt
    (non-tty) or the user aborts — so the cache/arg path never touches capture/stdin.
    """
    if cli_opt is not None:
        if cli_opt in choices:
            return (cli_opt, False)
        raise pytest.UsageError(f"--emulator {cli_opt!r} is not available on this platform; choose from {choices}")

    for candidate in (cache.get("emulator"), ini_default):
        if candidate in choices:
            return (candidate, False)

    pick = interactive_cb(choices)
    if pick is not None:
        return (pick, True)

    raise pytest.UsageError(f"could not resolve an emulator backend; pass --emulator (available: {choices})")


def resolve_serial(cli_opt: str | None, cache: dict) -> tuple[str | None, bool]:
    """Resolve the ADB serial. Precedence: --adb-serial arg > cache. Returns
    (serial, persist); an explicit arg is sticky (persists)."""
    if cli_opt is not None:
        if not validate_device_serial(cli_opt):
            raise pytest.UsageError(f"--adb-serial {cli_opt!r} is not a valid device serial")
        return (cli_opt, True)
    return (cache.get("adb_serial"), False)


def attach_emulator(cli_alias: str, logger: Logger, device_serial: str | None = None):
    """Construct the controller for `cli_alias`, boot it via restart(), and return it
    (or None, printing why).

    Construction is cheap discovery/config; restart() does the booting (VM start +
    Clash launch + main-menu wait). A not-ready emulator raises EmulatorNotReadyError
    from either step — that re-raises so the fixture can report it. Passes
    device_serial only when the controller's __init__ accepts it.
    """
    from pyclashbot.emulators import EmulatorType, get_emulator_registry

    registry = get_emulator_registry()
    display = CLI_ALIASES.get(cli_alias)
    if display is None:
        print(f"ERROR: unknown --emulator {cli_alias!r}", file=sys.stderr)
        return None

    try:
        emu_type = EmulatorType(display)
    except ValueError:
        print(f"ERROR: emulator {cli_alias!r} is not a valid EmulatorType", file=sys.stderr)
        return None

    cls = registry.get(emu_type)
    if cls is None:
        print(
            f"ERROR: emulator {cli_alias!r} is not supported on the current platform.",
            file=sys.stderr,
        )
        print(f"       available here: {', '.join(available_cli_choices())}", file=sys.stderr)
        return None

    kwargs: dict = {}
    sig = inspect.signature(cls.__init__)
    if device_serial is not None and "device_serial" in sig.parameters:
        kwargs["device_serial"] = device_serial

    try:
        emu = cls(logger, **kwargs)
        emu.restart()
        return emu
    except EmulatorNotReadyError:
        raise  # a real "not set up" signal — let the fixture report it, don't mask as None
    except Exception as e:
        print(f"ERROR: failed to attach to {cli_alias}: {type(e).__name__}: {e}", file=sys.stderr)
        return None
