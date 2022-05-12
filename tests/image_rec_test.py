import unittest
from PIL import Image
from pyclashbot.__main__ import compare_images


class ImageRecTest(unittest.TestCase):
    def test_image_rec(self):
        # Use pyautogui to screnshot
        ss = Image.open("tests/assets/test_image.png")
        # load template image from file
        tp = Image.open("tests/assets/pass_template.png")
        # run image rec and record if found
        self.assertTrue(compare_images(ss, tp) is not None)

    def test_no_image_rec(self):
        # Use pyautogui to screnshot
        ss = Image.open("tests/assets/test_image.png")
        # load template image from file
        tp = Image.open("tests/assets/fail_template.png")
        # run image rec and record if found
        self.assertTrue(compare_images(ss, tp) is None)