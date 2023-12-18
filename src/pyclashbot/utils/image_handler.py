from os.path import exists

import cv2
import numpy as np


class InvalidImageError(Exception):
    """Exception raised when an image is invalid"""

    def __init__(self, message: str, path: str = None):
        self.path = path
        self.message = message
        super().__init__(self.message)


def open_from_buffer(
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


def open_from_path(path: str) -> np.ndarray[np.uint8]:
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
        try:
            return open_from_buffer(im_stream.read())
        except InvalidImageError as error:
            raise InvalidImageError(
                f"File {path} is not a valid image. {error.message}",
                path=path,
            ) from error
