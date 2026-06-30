"""Screenshot a MEmu VM once a second for 10 seconds into screenshots/{index}.png.

    uv run python tests/screenshot_burst.py          # VM 0
    uv run python tests/screenshot_burst.py --vm 2   # VM 2

Needs an elevated terminal (memuc requires admin).
"""

from __future__ import annotations

import argparse
import os
import time

import cv2
from pymemuc import PyMemuc

from pyclashbot.emulators.memu import MemuScreenCapture

OUT_DIR = r"D:\my_files\my_programs\clash\py-clash-bot\screenshots"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vm", type=int, default=0, help="MEmu VM index (default: 0).")
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)
    cap = MemuScreenCapture(PyMemuc())

    for index in range(10):
        path = os.path.join(OUT_DIR, f"{index}.png")
        cv2.imwrite(path, cap[args.vm])
        print(f"saved {path}")
        if index < 9:
            time.sleep(1)


if __name__ == "__main__":
    main()
