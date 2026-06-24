"""Standalone runner: report which princess button is showing on each emulator.

Assumes the emulator is already on the card page WITH the princess card button
already clicked (the info/upgrade overlay is on screen). For each running VM it
prints, per fingerprint, every sampled pixel (actual BGR vs expected BGR and
whether it matches) so you can see exactly which pixel fails and why.

Run with the project venv (pyclashbot must be importable):
    $env:PYTHONUTF8=1; uv run python tests/clash_royale/test_princess_button_detection.py
    $env:PYTHONUTF8=1; uv run python tests/clash_royale/test_princess_button_detection.py --vm 1
"""

import argparse
import sys

from pymemuc import PyMemuc

from pyclashbot.bot.state_detect import (
    PRINCESS_FINGERPRINT_TOL,
    PRINCESS_FINGERPRINTS,
)
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.emulators.memu import MemuEmulatorController
from pyclashbot.utils.logger import Logger


def running_vm_indices() -> list[int]:
    pmc = PyMemuc()
    return [vm["index"] for vm in pmc.list_vm_info() if vm.get("running")]


def report_vm(emulator, vm_index: int) -> None:
    emulator.vm_index = vm_index
    iar = emulator.screenshot()
    print(f"\n=== VM {vm_index} ===")

    matched = []
    for name, (coords, colors) in PRINCESS_FINGERPRINTS.items():
        all_ok = True
        rows = []
        for (y, x), expected in zip(coords, colors):
            actual = [int(c) for c in iar[y][x]]
            ok = pixel_is_equal(actual, expected, PRINCESS_FINGERPRINT_TOL)
            all_ok = all_ok and ok
            rows.append(f"    ({x:>3},{y:>3}) actual={actual} expected={expected} -> {'OK' if ok else 'FAIL'}")
        print(f"  [{name}] => {'MATCH' if all_ok else 'no match'}")
        for r in rows:
            print(r)
        if all_ok:
            matched.append(name)

    print(f"  RESULT VM {vm_index}: {', '.join(matched) if matched else 'none detected'}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vm", type=int, default=None, help="Run on this VM index only")
    args = parser.parse_args()

    targets = [args.vm] if args.vm is not None else running_vm_indices()
    if not targets:
        print("No running MEmu VMs found.")
        return 1

    emulator = MemuEmulatorController(Logger())
    for vm in targets:
        report_vm(emulator, vm)

    return 0


if __name__ == "__main__":
    sys.exit(main())
