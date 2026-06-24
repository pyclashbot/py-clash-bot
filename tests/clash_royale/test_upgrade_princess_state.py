"""Standalone runner for upgrade_princess_state (main -> card page -> main).

Assumes a MEmu emulator is already open and sitting on the clash main menu.
Discovers running VMs and runs the state on each sequentially; pass `--vm N`
to target one specific VM, otherwise it runs on all running VMs.

Run with the GLOBAL Python (pymemuc lives there):
    & "C:\\Program Files\\Python311\\python.exe" tests/clash_royale/test_upgrade_princess_state.py
    & "C:\\Program Files\\Python311\\python.exe" tests/clash_royale/test_upgrade_princess_state.py --vm 8
"""

import argparse
import sys

from pymemuc import PyMemuc

from pyclashbot.bot.upgrade_princess_state import upgrade_princess_state
from pyclashbot.emulators.memu import MemuEmulatorController
from pyclashbot.utils.logger import Logger


def running_vm_indices() -> list[int]:
    pmc = PyMemuc()
    return [vm["index"] for vm in pmc.list_vm_info() if vm.get("running")]


def run_on_vm(emulator, vm_index: int, logger: Logger) -> bool:
    emulator.vm_index = vm_index
    print(f"\n=== VM {vm_index} ===")
    ok = upgrade_princess_state(emulator, logger)
    print(f"VM {vm_index}: {'PASS' if ok else 'FAIL'}")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vm", type=int, default=None, help="Run on this VM index only")
    args = parser.parse_args()

    targets = [args.vm] if args.vm is not None else running_vm_indices()
    if not targets:
        print("No running MEmu VMs found.")
        return 1

    logger = Logger()
    # Route the state's verbose log()/change_status() lines to the console.
    logger.set_current_state("upgrade_princess", console=True)
    emulator = MemuEmulatorController(logger)

    results = {vm: run_on_vm(emulator, vm, logger) for vm in targets}

    print("\n=== SUMMARY ===")
    for vm, ok in results.items():
        print(f"VM {vm}: {'PASS' if ok else 'FAIL'}")

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
