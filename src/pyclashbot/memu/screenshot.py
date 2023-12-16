"""
A module for getting screenshots from Memu VMs.
"""
import atexit
import sys

import numpy as np
from adbblitz import AdbShotTCP

from pyclashbot.memu.pmc import pmc, adb_path

FROZEN = getattr(sys, "frozen", False)


class ScreenShotter:
    """
    Class for getting screenshots.
    Stores adbblitz connections in a dict to avoid reconnecting for each screenshot.

    Example:
        vm_index = 0
        screen_shotter = ScreenShotter()
        screenshot = screen_shotter[vm_index]
        del screen_shotter # Cleanup
    """

    def __init__(self):
        self.connections: dict[int, AdbShotTCP] = {}

    def __getitem__(self, vm_index: int) -> np.ndarray:
        if vm_index not in self.connections:
            host, port = pmc.get_adb_connection(vm_index=vm_index)
            self.connections[vm_index] = AdbShotTCP(
                device_serial=f"{host}:{port}",
                adb_path=adb_path,
                log_level="ERROR" if FROZEN else "INFO",
            )
        return np.array(self.connections[vm_index].get_one_screenshot())

    def __del__(self):
        for conn in self.connections.values():
            conn.quit()


screen_shotter = ScreenShotter()


@atexit.register
def cleanup():
    """Cleanup function to be called at exit"""
    global screen_shotter  # pylint: disable=global-statement
    del screen_shotter
