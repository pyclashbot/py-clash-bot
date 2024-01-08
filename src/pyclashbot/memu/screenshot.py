"""
A module for taking screenshots from Memu Virtual Machines.
"""
import atexit
import time

import cv2
import numpy as np
from adbnativeblitz import AdbFastScreenshots

from pyclashbot.memu.configure import MEMU_CONFIGURATION
from pyclashbot.memu.pmc import adb_path, pmc
from pyclashbot.utils.logger import Logger  # Import the Logger


class ScreenShotter:
    """
    A class for taking screenshots.
    Stores adbblitz connections in a dictionary to avoid reconnecting for each screenshot.
    """

    def __init__(self, logger: Logger):  # Add a logger argument
        self.connections: dict[int, AdbFastScreenshots] = {}
        self.height = int(MEMU_CONFIGURATION["resolution_width"])
        self.width = int(MEMU_CONFIGURATION["resolution_height"])
        self.logger = logger  # Store the logger in the object

    def _crop_image(self, image: np.ndarray) -> np.ndarray:
        return image[:, 500:1100, :]

    def _resize_image(self, image: np.ndarray) -> np.ndarray:
        return cv2.resize(image, (self.height, self.width))

    def __getitem__(self, vm_index: int) -> np.ndarray:
        while True:
            try:
                if vm_index not in self.connections:
                    host, port = pmc.get_adb_connection(vm_index=vm_index)
                    self.connections[vm_index] = AdbFastScreenshots(
                        device_serial=f"{host}:{port}",
                        adb_path=adb_path,
                    )
                    self.connections[vm_index]._start_capturing()

                time.sleep(0.01)
                start_time = time.time()
                while not self.connections[vm_index].stop_recording:
                    if time.time() - start_time > 5:  # 5 seconds timeout
                        self.logger.log(
                            "Timeout while waiting for screenshot. Restarting.")
                        break  # Exit the inner while loop to restart

                    if not self.connections[vm_index].lastframes:
                        time.sleep(0.005)
                        continue

                    image = self.connections[vm_index].lastframes[-1].copy()
                    image = self._crop_image(image)
                    image = self._resize_image(image)
                    return image

            except Exception as e:
                self.logger.log(
                    f"Failed to get screenshot: {str(e)}. Restarting.")

    def close_connections(self):
        for conn in self.connections.values():
            conn.stop_recording = True
            conn.stop_capture()
            del conn

    def __del__(self):
        self.close_connections()


# Example of usage with a logger
logger = Logger()  # Create a Logger instance
# Pass the logger to ScreenShotter
screen_shotter = ScreenShotter(logger=logger)


@atexit.register
def cleanup():
    """Cleanup function to be called at exit"""
    screen_shotter.close_connections()
