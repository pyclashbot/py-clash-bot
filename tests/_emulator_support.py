"""Helpers behind the `emulator` fixture (conftest.py). Not a test module.

Non-destructive: attaches to an already-running emulator and verifies it's on
the Clash main menu; never boots, configures, or signs in.
"""

from __future__ import annotations

import inspect
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
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


def attach_emulator(cli_alias: str, logger: Logger):
    """Attach to an already-running emulator; return the controller or None (printing why).

    Passes debug_mode=True if the controller's __init__ accepts it (skips configure+restart).
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
    if "debug_mode" in sig.parameters:
        kwargs["debug_mode"] = True

    try:
        return cls(logger, **kwargs)
    except Exception as e:
        print(f"ERROR: failed to attach to {cli_alias}: {type(e).__name__}: {e}", file=sys.stderr)
        return None


def check_preconditions(emulator, cli_alias: str) -> tuple[bool, str]:
    """Verify: emulator exists, is open (reachable), on the Clash Royale main menu."""
    # 1. Reachability check — works across all emulator types.
    try:
        screenshot = emulator.screenshot()
    except Exception as e:
        return (
            False,
            f"can't test until the {cli_alias} emulator is open and reachable "
            f"(screenshot raised {type(e).__name__}: {e})",
        )
    if screenshot is None or getattr(screenshot, "size", 0) == 0:
        return (False, f"can't test until the {cli_alias} emulator is open (screenshot returned empty)")

    # 2. MEmu-only deeper check: VM must be in the "running" state. Other
    #    controllers don't have an equivalent introspection API; the
    #    screenshot above is the best generic gate we have.
    if cli_alias == "memu":
        try:
            vms = emulator.pmc.list_vm_info()
            vm = next((v for v in vms if v["index"] == emulator.vm_index), None)
            if vm is None:
                return (False, f"can't test until the MEmu VM idx={emulator.vm_index} exists")
            if not vm["running"]:
                return (
                    False,
                    f"can't test until the MEmu VM {vm.get('title', emulator.vm_index)!r} is open "
                    "(it's not currently running)",
                )
        except Exception:
            # If the introspection API itself is broken, fall through — the
            # screenshot check above already confirmed reachability.
            pass

    # 3. Screen-state check: must be on clash main menu, no popups, signed in.
    from pyclashbot.bot.state_detect import check_if_on_clash_main_menu

    if not check_if_on_clash_main_menu(emulator):
        return (
            False,
            f"can't test until you park the {cli_alias} emulator on the Clash Royale main menu "
            "(launch the app, dismiss any popups, sign in to account slot 1)",
        )

    return (True, "")
