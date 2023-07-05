import multiprocessing
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from os.path import abspath, dirname, join

import cv2
import numpy as np
from joblib import Parallel, delayed
from PIL import Image

from pyclashbot.memu.client import screenshot


# file stuff


def get_file_count(folder):
    """Method to return the amount of a files in a given directory

    Args:
        directory (str): Directory to count files in

    Returns:
        int: Amount of files in the given directory
    """
    directory = join(dirname(__file__), "reference_images", folder)

    print(directory)

    return sum(len(files) for _, _, files in os.walk(directory))


def make_reference_image_list(size):
    # Method to make a reference array of a given size
    reference_image_list = []

    for n in range(size):
        n = n + 1
        image_name = f"{n}.png"
        reference_image_list.append(image_name)

    return reference_image_list


# image comparison


def get_first_location(locations: list[list[int] | None], flip=False):
    """get the first location from a list of locations

    Args:
        locations (list[list[int]]): list of locations
        flip (bool, optional): flip coordinates. Defaults to False.

    Returns:
        list[int]: location
    """
    return next(
        (
            [location[1], location[0]] if flip else location
            for location in locations
            if location is not None
        ),
        None,
    )


def check_for_location(locations: list[list[int] | None]):
    """check for a location

    Args:
        locations (list[list[int]]): _description_

    Returns:
        bool: if location is found or not
    """
    return any(location is not None for location in locations)


def find_references(
    screenshot: np.ndarray | Image.Image,
    folder: str,
    names: list[str],
    tolerance=0.97,
) -> list[list[int] | None]:
    """find reference images in a screenshot

    Args:
        screenshot (np.ndarray | Image.Image): find references in screenshot
        folder (str): folder to find references (from within reference_images)
        names (list[str]): names of references
        tolerance (float, optional): tolerance. Defaults to 0.97.

    Returns:
        list[list[int] | None]: coordinate locations
    """
    num_cores = multiprocessing.cpu_count()
    with ThreadPoolExecutor(num_cores) as ex:
        futures = [
            ex.submit(find_reference, screenshot, folder, name, tolerance)
            for name in names
        ]
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                return [result]
    return [None]


def find_all_references(
    screenshot: np.ndarray | Image.Image,
    folder: str,
    names: list[str],
    tolerance=0.97,
) -> list[list[int] | None] | None:
    """find all reference images in a screenshot

    Args:
        screenshot (np.ndarray | Image.Image): find references in screenshot
        folder (str): folder to find references (from within reference_images)
        names (list[str]): names of references
        tolerance (float, optional): tolerance. Defaults to 0.97.

    Returns:
        list[list[int] | None]: coordinate locations
    """
    num_cores = multiprocessing.cpu_count()

    return Parallel(n_jobs=num_cores, prefer="threads")(
        delayed(find_reference)(screenshot, folder, name, tolerance) for name in names
    ) # type: ignore


def find_reference(
    screenshot: np.ndarray | Image.Image, folder: str, name: str, tolerance=0.97
) -> list[int] | None:
    """find a reference image in a screenshot

    Args:
        screenshot (np.ndarray | Image.Image): find reference in screenshot
        folder (str): folder to find reference (from within reference_images)
        name (str): name of reference
        tolerance (float, optional): tolerance. Defaults to 0.97.

    Returns:
        list[list[int] | None] | None: coordinate location
    """
    top_level = dirname(__file__)
    reference_folder = abspath(join(top_level, "reference_images"))

    path = join(reference_folder, folder, name)

    return compare_images(screenshot, Image.open(path), tolerance)


def compare_images(
    image: np.ndarray | Image.Image,
    template: np.ndarray | Image.Image,
    threshold=0.8,
):
    """detects pixel location of a template in an image
    Args:
        image (np.ndarray | Image.Image): image to find template within
        template (np.ndarray | Image.Image): template image to match to
        threshold (float, optional): matching threshold. defaults to 0.8
    Returns:
        list[list[int] | None]: a list of pixel location (x,y)
    """

    # show template
    # template.show()

    # Convert image to np.array

    image = np.array(image)
    template = np.array(template)

    # Convert image colors
    img_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)  # type: ignore # pylint: disable=no-member
    template_gray = cv2.cvtColor(  # type: ignore # pylint: disable=no-member
        template, cv2.COLOR_RGB2GRAY  # type: ignore # pylint: disable=no-member
    )

    # Perform match operations.
    res = cv2.matchTemplate(  # type: ignore # pylint: disable=no-member
        img_gray, template_gray, cv2.TM_CCOEFF_NORMED  # type: ignore # pylint: disable=no-member
    )

    # Store the coordinates of matched area in a np array
    loc = np.where(res >= threshold)  # type: ignore

    return None if len(loc[0]) != 1 else [int(loc[0][0]), int(loc[1][0])]


# pixel comparison


def check_line_for_color(vm_index, x1, y1, x2, y2, color: tuple[int, int, int]) -> bool:
    coordinates = get_line_coordinates(x1, y1, x2, y2)
    iar = np.asarray(screenshot(vm_index))

    for coordinate in coordinates:
        pixel = iar[coordinate[1]][coordinate[0]]

        if pixel_is_equal(color, pixel, tol=35):
            return True
    return False


def check_region_for_color(vm_index, region, color):
    left, top, width, height = region

    iar = np.asarray(screenshot(vm_index))

    for x in range(left, left + width):
        for y in range(top, top + height):
            pixel = iar[y][x]
            if pixel_is_equal(color, pixel, tol=35):
                return True

    return False


def region_is_color(vm_index, region, color):
    left, top, width, height = region

    iar = np.asarray(screenshot(vm_index))

    for x in range(left, left + width, 2):
        for y in range(top, top + height, 2):
            pixel = iar[y][x]
            if not (pixel_is_equal(color, pixel, tol=35)):
                return False

    return True


def pixel_is_equal(
    pix1: tuple[int, int, int] | list[int],
    pix2: tuple[int, int, int] | list[int],
    tol: float,
):
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
    return (diff_r < tol) and (diff_g < tol) and (diff_b < tol)


def get_line_coordinates(x1, y1, x2, y2) -> list[tuple[int, int]]:
    coordinates = []
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = -1 if x1 > x2 else 1
    sy = -1 if y1 > y2 else 1
    err = dx - dy

    while x1 != x2 or y1 != y2:
        coordinates.append((x1, y1))
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

    coordinates.append((x1, y1))
    return coordinates


if __name__ == "__main__":
    x1 = 5
    y1 = 5
    x2 = 10
    y2 = 6
