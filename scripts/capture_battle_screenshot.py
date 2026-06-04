#!/usr/bin/env python3
"""Save a 419x633 emulator screenshot for placement map overlays.

Windows + MEmu example:
  uv run python scripts/capture_battle_screenshot.py

Output: docs/reference/battle-screenshot.png
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "reference" / "battle-screenshot.png"
EXPECTED = (419, 633)


def main() -> None:
    try:
        from pyclashbot.emulators.memu import MemuEmulatorController
        from pyclashbot.utils.logger import Logger
    except ImportError as e:
        print(f"Cannot import emulator: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        emu = MemuEmulatorController(Logger(), debug_mode=True)
        frame = emu.screenshot()
    except Exception as e:
        print("Emulator capture failed:", e, file=sys.stderr)
        print("Save a mid-battle PNG manually to docs/reference/battle-screenshot.png", file=sys.stderr)
        print("See docs/reference/README.md", file=sys.stderr)
        sys.exit(1)

    if not isinstance(frame, np.ndarray) or frame.size == 0:
        print("Empty screenshot", file=sys.stderr)
        sys.exit(1)

    if frame.ndim == 3 and frame.shape[2] >= 3:
        img = Image.fromarray(frame[:, :, :3])
    else:
        img = Image.fromarray(frame)

    if img.size != EXPECTED:
        print(f"Warning: expected {EXPECTED}, got {img.size}; resizing", file=sys.stderr)
        img = img.resize(EXPECTED, Image.Resampling.LANCZOS)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.save(OUT)
    print(f"Saved {OUT} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
