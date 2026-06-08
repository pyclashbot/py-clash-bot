"""Screenshot pipeline smoke: capture returns a valid, non-black frame.

The lone survivor of the old MEmu-specific suite, generalized to any backend via
the shared emulator. A SUITE entry (not a standalone test) so it runs after the
boot setup test rather than before it.
"""

from __future__ import annotations

import numpy as np

_BLACK_THRESHOLD = 15.0


def run_test(emulator, logger) -> tuple[bool, str]:
    frame = emulator.screenshot()

    if not isinstance(frame, np.ndarray):
        return (False, f"screenshot() should return np.ndarray, got {type(frame)}")
    if frame.size == 0:
        return (False, "screenshot returned an empty array")

    mean_intensity = float(frame.mean())
    print(f"[screenshot] shape={frame.shape} dtype={frame.dtype} mean={mean_intensity:.2f}")
    if mean_intensity <= _BLACK_THRESHOLD:
        return (
            False,
            f"frame is near-black (mean={mean_intensity:.2f} <= {_BLACK_THRESHOLD}); "
            "emulator may be off, locked, or showing a black screen",
        )

    return (True, "")
