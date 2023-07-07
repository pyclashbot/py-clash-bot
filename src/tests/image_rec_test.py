import contextlib
import timeit
import unittest

from PIL import Image
from pymemuc import PyMemucError

with contextlib.suppress(PyMemucError):
    from pyclashbot.detection import compare_images


class ImageRecTest(unittest.TestCase):
    def test_image_rec(self):
        ss = Image.open("tests/assets/test_image.png")
        # load template image from file
        tp = Image.open("tests/assets/pass_template.png")
        # run image rec and record if found
        self.assertTrue(compare_images(ss, tp) is not None)

    def test_no_image_rec(self):
        ss = Image.open("tests/assets/test_image.png")
        # load template image from file
        tp = Image.open("tests/assets/fail_template.png")
        # run image rec and record if found
        self.assertTrue(compare_images(ss, tp) is None)

    def test_thresholding(self):
        # between test_image and pass_template, detection above 0.66
        # between test_iamge and fail_template, no detection
        # between clashss and clashtemp, detection about 0.96

        ss_path = "tests/assets/clashss.png"
        tp_path = "tests/assets/clashtemp.png"
        ss = Image.open(ss_path)
        tp = Image.open(tp_path)

        granularity = 100

        threshold = None

        for i in range(granularity):
            threshold = (
                i / granularity
                if compare_images(ss, tp, i / granularity) is not None
                else None
            )
        print(f"Detected threshold for {tp_path} in {ss_path} @ {threshold}")
        self.assertTrue(threshold is not None)

    def test_compare_speed(self):
        testcode = """
def test():
    from pyclashbot.image_rec import compare_images
    from PIL import Image
    ss_path = "tests/assets/clashss.png"
    tp_path = "tests/assets/clashtemp.png"
    ss = Image.open(ss_path)
    tp = Image.open(tp_path)
    compare_images(ss, tp)
        """
        count = 5000000
        print(
            f"{timeit.timeit(testcode, number=count)} seconds for {count} image compares"
        )


if __name__ == "__main__":
    unittest.main()
