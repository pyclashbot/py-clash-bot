import multiprocessing
import sys
from os.path import join
from typing import Union

import cv2
import numpy as np
from joblib import Parallel, delayed
from PIL import Image


def find_references(screenshot: Union[np.ndarray, Image.Image], folder: str, names: list[str], tolerance=0.97):
    """find reference images in a screenshot

    Args:
        screenshot (Union[np.ndarray, Image.Image]): find references in screenshot
        folder (str): folder to find references (from within reference_images)
        names (list[str]): names of references
        tolerance (float, optional): tolerance. Defaults to 0.97.

    Returns:
        list[Union[tuple[int,int],None]: coordinate locations
    """
    num_cores = multiprocessing.cpu_count()
    return Parallel(n_jobs=num_cores, prefer="threads")(
        delayed(find_reference)(screenshot, folder, name, tolerance) for name in names)


def find_reference(screenshot: Union[np.ndarray, Image.Image], folder: str, name: str, tolerance=0.97):
    """find a reference image in a screenshot

    Args:
        screenshot (Union[np.ndarray, Image.Image]): find reference in screenshot
        folder (str): folder to find reference (from within reference_images)
        name (str): name of reference
        tolerance (float, optional): tolerance. Defaults to 0.97.

    Returns:
        Union[tuple[int,int], None]: coordinate location
    """
    reference_folder = "reference_images"
    return compare_images(screenshot, Image.open(join(reference_folder, folder, name)), tolerance)


def pixel_is_equal(pix1, pix2, tol):
    """check pixel equality

    Args:
        pix1 (list[int]): [R,G,B] pixel
        pix2 (list[int]): [R,G,B] pixel
        tol (float): tolerance

    Returns:
        bool: are pixels equal
    """
    diff_r = abs(pix1[0] - pix2[0])
    diff_g = abs(pix1[1] - pix2[1])
    diff_b = abs(pix1[2] - pix2[2])
    if (diff_r < tol) and (diff_g < tol) and (diff_b < tol):
        return True
    else:
        return False


def compare_images(image: Union[np.ndarray, Image.Image], template: Union[np.ndarray, Image.Image], threshold=0.8):
    """detects pixel location of a template in an image
    Args:
        image (Union[np.ndarray, Image.Image]): image to find template within
        template (Union[np.ndarray, Image.Image]): template image to match to
        threshold (float, optional): matching threshold. defaults to 0.8
    Returns:
        Union[tuple[int,int], None]: a tuple of pixel location (x,y)
    """

    # show template
    # template.show()

    # Convert image to np.array
    image = np.array(image)
    template = np.array(template)

    # Convert image colors
    img_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_RGB2GRAY)

    # Perform match operations.
    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    # Store the coordinates of matched area in a numpy array
    loc = np.where(res >= threshold)  # type: ignore

    if len(loc[0]) != 1:
        return None

    return (int(loc[0][0]), int(loc[1][0]))
