from os.path import exists

import cv2
import numpy as np


class InvalidImageError(Exception):
    """Exception raised when an image is invalid"""

    def __init__(self, message: str, path: str = None):
        self.path = path
        self.message = message
        super().__init__(self.message)


def open_from_bytes(byte_array: bytearray) -> np.ndarray:
    """
    A method to read an image from a byte array
    :param byte_array: the byte array to read the image from
    :return: the image as a numpy array
    :raises InvalidImageError: if the file is not a valid image
    """
    im_arr = np.asarray(byte_array, dtype=np.uint8)
    img = cv2.imdecode(im_arr, cv2.IMREAD_COLOR)  # pylint: disable=no-member
    if img is None:
        raise InvalidImageError("Byte array is not a valid image")
    if np.all(img == 255):
        raise InvalidImageError("Byte array is not a valid image. All pixels are white")
    return img


def open_from_path(path: str) -> np.ndarray:
    """
    A method to validate and open an image file
    :param path: the path to the image file
    :return: the image as a numpy array
    :raises FileNotFoundError: if the file does not exist
    :raises ValueError: if the file is not a png image
    :raises InvalidImageError: if the file is not a valid image
    """
    if not exists(path):
        raise FileNotFoundError(f"File {path} does not exist")
    if not path.lower().endswith(".png"):
        raise ValueError(f"File {path} is not a png image")
    with open(path, "rb") as im_stream:
        im_bytes = bytearray(im_stream.read())
        try:
            return open_from_bytes(im_bytes)
        except InvalidImageError as error:
            raise InvalidImageError(f"File {path} is not a valid image") from error
