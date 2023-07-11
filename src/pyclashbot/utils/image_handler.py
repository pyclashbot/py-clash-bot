from os.path import exists

import cv2
import numpy as np


class InvalidImageError(Exception):
    """Exception raised when an image is invalid"""

    def __init__(self, path: str, message: str):
        self.path = path
        self.message = message
        super().__init__(self.message)


def open_image(path) -> np.ndarray:
    """
    A method to validate and open an image file
    :param path: the path to the image file
    :return: the image as a numpy array
    """
    if not exists(path):
        raise FileNotFoundError(f"File {path} does not exist")
    if not path.endswith(".png"):
        raise ValueError(f"File {path} is not a png image")
    img = cv2.imread(path)  # pylint: disable=no-member
    if img is None:
        raise InvalidImageError(path, f"File {path} is not a valid image")
    return img
