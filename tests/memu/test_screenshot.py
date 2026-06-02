"""Module-level smoke test: MEmu screenshot capture returns a non-black frame.

Run directly:
    py tests/memu/test_screenshot.py

Or via pytest:
    pytest tests/memu/test_screenshot.py

Requires MEmu to be installed and a clashbot VM reachable.
"""

from __future__ import annotations

import sys

import numpy as np

from pyclashbot.emulators.memu import MemuEmulatorController
from pyclashbot.utils.logger import Logger

BLACK_THRESHOLD = 15.0


def test_screenshot_not_black() -> None:
    logger = Logger()
    emu = MemuEmulatorController(logger, debug_mode=True)

    frame = emu.screenshot()

    assert isinstance(frame, np.ndarray), f"screenshot() should return np.ndarray, got {type(frame)}"
    assert frame.size > 0, "screenshot returned an empty array"

    mean_intensity = float(frame.mean())
    print(f"[test_screenshot] shape={frame.shape} dtype={frame.dtype} mean={mean_intensity:.2f}")

    assert mean_intensity > BLACK_THRESHOLD, (
        f"frame is near-black (mean={mean_intensity:.2f} <= {BLACK_THRESHOLD}); "
        "emulator may be off, locked, or showing a black screen"
    )


if __name__ == "__main__":
    try:
        test_screenshot_not_black()
    except AssertionError as e:
        print(f"FAIL: {e}", file=sys.stderr)
        sys.exit(1)
    print("PASS")
