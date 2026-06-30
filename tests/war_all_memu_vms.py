"""Run the war state on every running MEmu VM, sequentially, and report pass/fail.

Assumes Clash Royale is already open and on the main menu in each target VM.
For each VM it runs `war_state`, which navigates main -> war, plays/exits, and
returns to main; that round trip succeeding (war_state returns True) is a pass.

Not a pytest test (it drives many live VMs by index and takes CLI args), so the
filename is not `test_*` and pytest won't collect it.

    uv run python tests/war_all_memu_vms.py            # all running MEmu VMs
    uv run python tests/war_all_memu_vms.py --vms 0 2   # only VM indices 0 and 2

ponytail: reassigns vm_index on one bare controller instead of one controller
per VM; the MEmu click/swipe/screenshot primitives key off self.vm_index only.
"""

from __future__ import annotations

import argparse
import sys

from pymemuc import PyMemuc

from pyclashbot.bot.state_detect import check_if_on_clash_main_menu
from pyclashbot.bot.war import war_state
from pyclashbot.emulators.memu import MemuEmulatorController, MemuScreenCapture
from pyclashbot.utils.logger import Logger


def _running_vm_indices(pmc: PyMemuc) -> list[int]:
    return [vm["index"] for vm in pmc.list_vm_info() if vm["running"]]


def _make_driver(pmc: PyMemuc, logger: Logger, vm_index: int) -> MemuEmulatorController:
    """A MEmu controller pointed at vm_index, WITHOUT the find-or-create __init__
    side effect (which would spawn a pyclashbot VM). Only the click/swipe/screenshot
    plumbing is wired — that's all war_state touches."""
    emu = object.__new__(MemuEmulatorController)
    emu.logger = logger
    emu.pmc = pmc
    emu.screenshotter = MemuScreenCapture(pmc)
    emu.vm_index = vm_index
    return emu


def run_one(pmc: PyMemuc, logger: Logger, vm_index: int) -> tuple[bool, str]:
    """main -> war -> main on a single VM. (passed, reason)."""
    # Tag every war_state status line with this VM and echo it to the console.
    logger.set_current_state(f"VM {vm_index}", console=True)
    emu = _make_driver(pmc, logger, vm_index)

    if not check_if_on_clash_main_menu(emu):
        return (False, "not on main menu at start (need CR open on main page)")

    if not war_state(emu, logger):
        return (False, "war_state failed (did not complete main -> war -> main)")

    if not check_if_on_clash_main_menu(emu):
        return (False, "war_state returned True but not back on main menu")

    return (True, "main -> war -> main OK")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--vms",
        type=int,
        nargs="+",
        metavar="INDEX",
        help="MEmu VM indices to test (default: all running VMs).",
    )
    args = parser.parse_args(argv)

    logger = Logger()
    pmc = PyMemuc()

    running = _running_vm_indices(pmc)
    if not running:
        print("No running MEmu VMs found.", file=sys.stderr)
        return 1

    if args.vms is not None:
        targets = [i for i in args.vms if i in running]
        missing = sorted(set(args.vms) - set(running))
        if missing:
            print(f"Skipping non-running VM indices: {missing}", file=sys.stderr)
        if not targets:
            print("None of the requested VM indices are running.", file=sys.stderr)
            return 1
    else:
        targets = running

    print(f"Testing war state on MEmu VM indices: {targets}\n")

    results: dict[int, tuple[bool, str]] = {}
    for vm_index in targets:
        print(f"=== VM {vm_index} ===")
        try:
            results[vm_index] = run_one(pmc, logger, vm_index)
        except Exception as e:  # one VM blowing up shouldn't abort the rest
            results[vm_index] = (False, f"exception: {type(e).__name__}: {e}")
        passed, reason = results[vm_index]
        print(f"--> VM {vm_index}: {'PASS' if passed else 'FAIL'} ({reason})\n")

    print("=== Summary ===")
    for vm_index in targets:
        passed, reason = results[vm_index]
        print(f"  VM {vm_index}: {'PASS' if passed else 'FAIL'} - {reason}")

    return 0 if all(p for p, _ in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
