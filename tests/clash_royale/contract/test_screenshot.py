"""Screenshot smoke: capture returns a valid, non-black frame.

A SUITE entry (not a standalone test) so it runs after boot/main-menu setup.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from pyclashbot.emulators.base import BaseEmulatorController
    from pyclashbot.utils.logger import Logger

_BLACK_THRESHOLD = 15.0


def run_test(emulator: BaseEmulatorController, logger: Logger) -> tuple[bool, str]:
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
