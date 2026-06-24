"""Standalone runner: verbosely check check_if_on_clash_main_menu per emulator.

Assumes the emulator is sitting on the clash main menu. For each running VM it
prints, per color palette, every sampled pixel (actual BGR vs expected BGR and
whether it matches) so you can see exactly which pixel/palette fails and why.
A VM is "on main menu" when any single palette matches all of its pixels.

Run with the project venv (pyclashbot must be importable):
    $env:PYTHONUTF8=1; uv run python tests/clash_royale/test_check_if_on_clash_main_menu.py
    $env:PYTHONUTF8=1; uv run python tests/clash_royale/test_check_if_on_clash_main_menu.py --vm 1
"""

import argparse
import sys

from pymemuc import PyMemuc

from pyclashbot.bot.state_detect import check_if_on_clash_main_menu
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.emulators.memu import MemuEmulatorController
from pyclashbot.utils.logger import Logger

TOL = 25

# (y, x) coords sampled by check_if_on_clash_main_menu, with their landmark note.
COORDS = [
    (14, 209, "white"),
    (14, 325, "white"),
    (19, 298, "yellow"),
    (17, 399, "green"),
    (581, 261, "green"),
    (584, 166, "bluegrey"),
    (621, 166, "bluegrey"),
]

PALETTES = {
    "google play": [
        [255, 255, 255],
        [255, 255, 255],
        [53, 199, 233],
        [25, 198, 65],
        [138, 105, 71],
        [139, 105, 72],
        [155, 120, 82],
    ],
    "memu": [
        [255, 255, 255],
        [255, 255, 255],
        [53, 200, 233],
        [24, 199, 65],
        [138, 105, 71],
        [139, 105, 72],
        [155, 120, 81],
    ],
    "post-update": [
        [57, 151, 206],
        [21, 148, 42],
        [36, 17, 1],
        [231, 190, 123],
        [140, 105, 74],
        [140, 105, 74],
        [156, 121, 82],
    ],
}


def report_vm(emulator, vm_index: int) -> bool:
    emulator.vm_index = vm_index
    iar = emulator.screenshot()
    print(f"\n=== VM {vm_index} ===")

    any_palette = False
    for pal_name, colors in PALETTES.items():
        all_ok = True
        rows = []
        for (y, x, note), expected in zip(COORDS, colors):
            actual = [int(c) for c in iar[y][x]]
            ok = pixel_is_equal(actual, expected, TOL)
            all_ok = all_ok and ok
            rows.append(
                f"      ({x:>3},{y:>3}) {note:<8} actual={actual} expected={expected} -> {'OK' if ok else 'FAIL'}",
            )
        any_palette = any_palette or all_ok
        print(f"  [palette: {pal_name}] => {'MATCH' if all_ok else 'no match'}")
        for r in rows:
            print(r)

    # Cross-check against the real function so the test can't silently drift.
    result = check_if_on_clash_main_menu(emulator)
    print(f"  RESULT VM {vm_index}: on_main_menu={result} (any palette matched={any_palette})")
    return result


def running_vm_indices() -> list[int]:
    pmc = PyMemuc()
    return [vm["index"] for vm in pmc.list_vm_info() if vm.get("running")]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vm", type=int, default=None, help="Run on this VM index only")
    args = parser.parse_args()

    targets = [args.vm] if args.vm is not None else running_vm_indices()
    if not targets:
        print("No running MEmu VMs found.")
        return 1

    emulator = MemuEmulatorController(Logger())
    results = {vm: report_vm(emulator, vm) for vm in targets}

    print("\n=== SUMMARY ===")
    for vm, ok in results.items():
        print(f"VM {vm}: {'on main menu' if ok else 'NOT on main menu'}")

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
