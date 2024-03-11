"""
A module for getting screenshots from Memu VMs.
"""

import atexit
import base64
import re
import time

import cv2
import numpy as np
from pymemuc import PyMemucError

from pyclashbot.memu.pmc import pmc


class InvalidImageError(Exception):
    """Exception raised when an image is invalid"""

    def __init__(self, message: str, path: str | None = None):
        self.path = path
        self.message = message
        super().__init__(self.message)


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

    def open_from_b64(self, image_b64: str) -> np.ndarray[np.uint8]:
        """
        A method to validate and open an image from a base64 string
        :param image_b64: the base64 string to read the image from
        :return: the image as a numpy array
        :raises InvalidImageError: if the file is not a valid image
        """

        try:
            image_data = base64.b64decode(image_b64)
        except (TypeError, ValueError, base64.binascii.Error) as error:
            raise InvalidImageError("image_b64 is not a valid base64 string") from error
        return self.open_from_buffer(image_data)

    def open_from_buffer(
        self,
        image_data: bytes | bytearray | memoryview | np.ndarray[any],
    ) -> np.ndarray[np.uint8]:
        """
        A method to read an image from a byte array
        :param byte_array: the byte array to read the image from
        :return: the image as a numpy array
        :raises InvalidImageError: if the file is not a valid image
        """
        try:
            im_arr = np.frombuffer(image_data, dtype=np.uint8)
        except (BufferError, ValueError) as error:
            raise InvalidImageError("image_data is not a valid buffer") from error
        try:
            img = cv2.imdecode(im_arr, cv2.IMREAD_COLOR)  # pylint: disable=no-member
        except cv2.error as error:  # pylint: disable=catching-non-exception
            # pylint: disable=bad-exception-cause
            raise InvalidImageError("image_data bytes cannot be decoded") from error
        if img is None or len(img) == 0 or len(img.shape) != 3 or img.shape[2] != 3:
            raise InvalidImageError("image_data bytes are not a valid image")
        if np.all(img == 255) or np.all(img == 0):
            raise InvalidImageError(
                "image_data bytes are not a valid image. Image is all white or all black"
            )
        return img

    def __getitem__(self, vm_index: int) -> np.ndarray:
        while True:  # loop until a valid image is returned
            try:
                # read screencap from vm using screencap output encoded in base64
                shell_out = pmc.send_adb_command_vm(
                    vm_index=vm_index,
                    command="shell screencap -p | base64",
                )

                # remove non-image data from shell output
                image_b64 = re.sub(
                    r"already connected to 127\.0\.0\.1:[\d]*\n\n", "", shell_out
                ).replace("\n", "")
                return self.open_from_b64(image_b64)

            except (PyMemucError, FileNotFoundError, InvalidImageError):
                time.sleep(0.1)


screen_shotter = ScreenShotter()


@atexit.register
def cleanup():
    """Cleanup function to be called at exit"""
    global screen_shotter  # pylint: disable=global-statement
    del screen_shotter
