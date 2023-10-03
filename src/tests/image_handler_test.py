"""Unit Test for the image handler"""
import unittest
import os
import numpy as np

from pyclashbot.utils.image_handler import (
    open_from_buffer,
    open_from_path,
    InvalidImageError,
)


class ImageHandlerTest(unittest.TestCase):
    """Test the image handler"""

    def setUp(self):
        """Define the path to the test image folder"""
        self.test_image_folder = os.path.join(os.path.dirname(__file__), "assets")

    def test_valid_image_from_buffer(self):
        """Load a valid image from the buffer"""
        with open(os.path.join(self.test_image_folder, "valid_image.png"), "rb") as im_file:
            image_data = im_file.read()
            img = open_from_buffer(image_data)
            self.assertIsInstance(img, np.ndarray)
            self.assertEqual(img.shape[2], 3)  # RGB image

    def test_valid_image_from_path(self):
        """Load a valid image from a path"""
        image_path = os.path.join(self.test_image_folder, "valid_image.png")
        img = open_from_path(image_path)
        self.assertIsInstance(img, np.ndarray)
        self.assertEqual(img.shape[2], 3)  # RGB image

    def test_invalid_image_from_buffer(self):
        """Test with an invalid image from the buffer"""
        with open(
            os.path.join(self.test_image_folder, "invalid_image_data.png"), "rb"
        ) as im_file:
            image_data = im_file.read()
            with self.assertRaises(InvalidImageError):
                open_from_buffer(image_data)

    def test_invalid_image_from_path(self):
        """Test with an invalid image from a path"""
        image_path = os.path.join(self.test_image_folder, "invalid_image_data.png")
        with self.assertRaises(InvalidImageError):
            open_from_path(image_path)

    def test_nonexistent_file(self):
        """Test with a nonexistent file"""
        non_existent_path = os.path.join(
            self.test_image_folder, "nonexistent_image.png"
        )
        with self.assertRaises(FileNotFoundError):
            open_from_path(non_existent_path)

    def test_non_png_file(self):
        """Test with a non-PNG file"""
        non_png_path = os.path.join(self.test_image_folder, "non_png_image.jpg")
        with self.assertRaises(ValueError):
            open_from_path(non_png_path)

    def test_all_white_image(self):
        """Test with an all white image"""
        all_white_path = os.path.join(self.test_image_folder, "all_white_image.png")
        with self.assertRaises(InvalidImageError):
            open_from_path(all_white_path)

    def test_all_black_image(self):
        """Test with an all black image"""
        all_black_path = os.path.join(self.test_image_folder, "all_black_image.png")
        with self.assertRaises(InvalidImageError):
            open_from_path(all_black_path)


if __name__ == "__main__":
    unittest.main()
