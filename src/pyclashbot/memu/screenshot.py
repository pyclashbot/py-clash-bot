"""
A module for getting screenshots from Memu VMs.
"""
import atexit
import time

import cv2
import numpy as np
from adbnativeblitz import AdbFastScreenshots

from pyclashbot.memu.configure import MEMU_CONFIGURATION
from pyclashbot.memu.pmc import adb_path, pmc


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
        self.connections: dict[int, AdbFastScreenshots] = {}
        self.height = int(MEMU_CONFIGURATION["resolution_width"])
        self.width = int(MEMU_CONFIGURATION["resolution_height"])

    def _crop_image(self, image: np.ndarray) -> np.ndarray:
        return image[:, 500:1100, :]

    def _resize_image(self, image: np.ndarray) -> np.ndarray:
        return cv2.resize(image, (self.height, self.width))  # pylint: disable=no-member

    def __getitem__(self, vm_index: int) -> np.ndarray:
        if vm_index not in self.connections:
            host, port = pmc.get_adb_connection(vm_index=vm_index)
            self.connections[vm_index] = AdbFastScreenshots(
                device_serial=f"{host}:{port}",
                adb_path=adb_path,
            )
            # pylint: disable=protected-access
            self.connections[vm_index]._start_capturing()

        time.sleep(0.01)
        while not self.connections[vm_index].stop_recording:
            if not self.connections[vm_index].lastframes:
                # print("no frames yet")
                time.sleep(0.005)
                continue
            image = self.connections[vm_index].lastframes[-1].copy()

            # Crop and resize image (adbblitz returns a 1600x900 image and its scaling doesn't work)
            image = self._crop_image(image)
            image = self._resize_image(image)
            return image
        raise RuntimeError("Failed to get screenshot, is the connection open?")

    def __del__(self):
        for conn in self.connections.values():
            conn.stop_recording = True
            conn.stop_capture()


screen_shotter = ScreenShotter()


@atexit.register
def cleanup():
    """Cleanup function to be called at exit"""
    global screen_shotter  # pylint: disable=global-statement
    del screen_shotter
