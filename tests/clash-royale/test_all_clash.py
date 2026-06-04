"""End-to-end clash test runner: one emulator, nav -> all jobs, linear.

Usage:
    py tests/clash-royale/test_all_clash.py --emulator <type>

`<type>` is one of the emulator backends supported on the current platform.
Use `--help` to see the live list (varies by Windows/macOS).

The runner refuses to do anything destructive on its own. It:
  1. Attaches to an already-running emulator of the type you specify.
  2. Verifies the emulator is reachable and currently on the Clash Royale
     main menu.
  3. If any precondition fails, prints what's wrong and exits — does NOT
     boot, configure, restart, or sign in to anything.
  4. Otherwise, runs the navigation test, then every job test in sequence.
     Stops at the first failure (later tests assume a clean main-menu state).
  5. Prints a pass/fail table and exits 0 on full pass, 1 otherwise.

Precondition (set up by hand before running):
  - The chosen emulator is launched.
  - Clash Royale is signed in to account slot 1.
  - At least 2 accounts are available on the emulator.
  - You are parked on the Clash Royale main menu.
  - You are in a clan (some job tests rely on the clan-chat screen).

See tests/clash-royale/readme.md for the full setup checklist.
"""

from __future__ import annotations

import argparse
import importlib.util
import inspect
import sys
from pathlib import Path
from types import ModuleType
from typing import Callable

TestFn = Callable[[object, object], tuple[bool, str]]

THIS_DIR = Path(__file__).resolve().parent
NAV_DIR = THIS_DIR / "navigation"
JOBS_DIR = THIS_DIR / "jobs"

# CLI alias -> EmulatorType key. Lowercase, dash-separated for friendly CLI.
CLI_ALIASES = {
    "memu": "MEmu",
    "bluestacks": "BlueStacks 5",
    "google-play": "Google Play Games",
    "adb": "ADB Device",
}


def _load(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _suite() -> list[tuple[str, TestFn]]:
    nav = _load(NAV_DIR / "test_navigate_main_pages.py")
    # jobs — order matters: cheap/safe ones first, fight chain last.
    # switch_account is a round-trip so we still end on account 1.
    job_files = [
        ("switch_account", "test_switch_account.py"),
        ("upgrade", "test_upgrade.py"),
        ("card_mastery", "test_card_mastery.py"),
        ("clan_chat_claim", "test_clan_chat_claim.py"),
        ("clan_chat_donate", "test_clan_chat_donate.py"),
        ("clan_chat_request", "test_clan_chat_request.py"),
        ("select_battle_mode", "test_select_battle_mode.py"),
        ("randomize_deck", "test_randomize_deck.py"),
        ("cycle_deck", "test_cycle_deck.py"),
        ("1v1_fight", "test_1v1_fight.py"),
        ("2v2_fight", "test_2v2_fight.py"),
    ]
    suite: list[tuple[str, TestFn]] = [("nav: all main-page permutations", nav.run_test)]
    for label, filename in job_files:
        mod = _load(JOBS_DIR / filename)
        suite.append((f"job: {label}", mod.run_test))
    return suite


def _available_cli_choices() -> list[str]:
    """Return the CLI aliases for emulators supported on this platform."""
    from pyclashbot.emulators import EmulatorType, get_available_emulators

    available = set(get_available_emulators())
    return [cli for cli, display in CLI_ALIASES.items() if EmulatorType(display) in available]


def _attach_emulator(cli_alias: str, logger):
    """Attach to an already-running emulator of the given type.

    Returns the controller or None on failure (and prints the reason).

    The constructor is called with `debug_mode=True` if the controller's
    __init__ accepts it (MEmu uses this to skip configure+restart). For
    controllers that don't expose `debug_mode`, we just pass the logger.
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
        print(f"       available here: {', '.join(_available_cli_choices())}", file=sys.stderr)
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


def _check_preconditions(emulator, cli_alias: str) -> tuple[bool, str]:
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


def _print_table(results: list[tuple[str, bool, str]]) -> None:
    name_w = max(len(name) for name, _, _ in results)
    print()
    print("=" * (name_w + 30))
    print(f"{'TEST':<{name_w}}  RESULT  MESSAGE")
    print("-" * (name_w + 30))
    for name, ok, msg in results:
        status = "PASS" if ok else "FAIL"
        print(f"{name:<{name_w}}  {status:<6}  {msg}")
    print("=" * (name_w + 30))


def main() -> int:
    # Build choices dynamically so --help reflects what works on this platform.
    try:
        choices = _available_cli_choices()
    except Exception:
        # If the registry can't be loaded, fall back to all four. The attach
        # step will fail with a more specific error.
        choices = list(CLI_ALIASES.keys())

    parser = argparse.ArgumentParser(description="Run the full Clash Royale test suite.")
    parser.add_argument(
        "--emulator",
        required=True,
        choices=choices,
        help="Which emulator backend to attach to. Must already be running on the CR main menu.",
    )
    args = parser.parse_args()

    from pyclashbot.utils.logger import Logger

    logger = Logger()

    emulator = _attach_emulator(args.emulator, logger)
    if emulator is None:
        return 1

    ok, msg = _check_preconditions(emulator, args.emulator)
    if not ok:
        print(f"\nABORTING: {msg}", file=sys.stderr)
        return 1

    print(f"[+] preconditions OK ({args.emulator}): emulator exists, is open, on Clash main menu.\n")

    suite = _suite()
    results: list[tuple[str, bool, str]] = []
    failed = False

    for i, (name, fn) in enumerate(suite):
        print(f"\n>>> RUNNING: {name}")
        try:
            ok, msg = fn(emulator, logger)
        except Exception as e:
            ok, msg = False, f"uncaught exception: {type(e).__name__}: {e}"

        results.append((name, ok, msg))

        if ok:
            print(f"<<< PASS: {name}")
            continue

        print(f"<<< FAIL: {name} -- {msg}", file=sys.stderr)
        failed = True
        for skip_name, _ in suite[i + 1 :]:
            results.append((skip_name, False, "skipped (earlier failure)"))
        break

    _print_table(results)

    if failed:
        print("\nOVERALL: FAIL")
        return 1
    print("\nOVERALL: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
