from os.path import exists

import cv2
import numpy as np


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
        raise ValueError(f"File {path} is not a valid image")
    return img
