from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from os import walk
from os.path import abspath, dirname, join

import cv2
import numpy as np

from pyclashbot.memu.client import screenshot
from pyclashbot.utils.image_handler import open_image


def get_file_count(folder) -> int:
    """Method to return the amount of a files in a given directory

    Args:
        directory (str): Directory to count files in

    Returns:
        int: Amount of files in the given directory
    """
    directory = join(dirname(__file__), "reference_images", folder)

    return sum(len(files) for _, _, files in walk(directory))


def make_reference_image_list(size):
    # Method to make a reference array of a given size
    reference_image_list = []

    for index in range(size):
        index += 1
        image_name: str = f"{index}.png"
        reference_image_list.append(image_name)

    return reference_image_list


# image comparison


def get_first_location(
    locations: list[list[int] | None], flip=False
) -> list[int] | None:
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
    image: np.ndarray,
    folder: str,
    names: list[str],
    tolerance=0.97,
) -> list[list[int] | None]:
    """find all reference images in a screenshot

    Args:
        screenshot (numpy.ndarray): find references in screenshot
        folder (str): folder to find references (from within reference_images)
        names (list[str]): names of references
        tolerance (float, optional): tolerance. Defaults to 0.97.

    Returns:
        list[list[int] | None]: coordinate locations
    """
    top_level = dirname(__file__)
    reference_folder = abspath(join(top_level, "reference_images", folder))

    reference_images = [open_image(join(reference_folder, name)) for name in names]

    with ThreadPoolExecutor(
        max_workers=len(reference_images), thread_name_prefix="EmulatorThread"
    ) as executor:
        futures: list[Future[list[int] | None]] = [
            executor.submit(
                compare_images,
                image,
                template,
                tolerance,
            )
            for template in reference_images
        ]
        return [future.result() for future in as_completed(futures)]


def compare_images(
    image: np.ndarray,
    template: np.ndarray,
    threshold=0.8,
):
    """detects pixel location of a template in an image
    Args:
        image (numpy.ndarray): image to find template within
        template (numpy.ndarray): template image to match to
        threshold (float, optional): matching threshold. defaults to 0.8
    Returns:
        list[list[int] | None]: a list of pixel location (x,y)
    """
    # pylint: disable=no-member
    # Convert image colors
    img_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)  # type: ignore
    template_gray = cv2.cvtColor(  # type: ignore
        template, cv2.COLOR_RGB2GRAY  # type: ignore
    )

    # Perform match operations.
    res = cv2.matchTemplate(  # type: ignore
        img_gray, template_gray, cv2.TM_CCOEFF_NORMED  # type: ignore
    )

    # Store the coordinates of matched area in a np array
    loc = np.where(res >= threshold)  # type: ignore

    return None if len(loc[0]) != 1 else [int(loc[0][0]), int(loc[1][0])]


# pixel comparison


def line_is_color(  # pylint: disable=too-many-arguments
    vm_index, x_1, y_1, x_2, y_2, color
) -> bool:
    coordinates = get_line_coordinates(x_1, y_1, x_2, y_2)
    iar = np.asarray(screenshot(vm_index))

    for coordinate in coordinates:
        pixel = iar[coordinate[1]][coordinate[0]]
        pixel = convert_pixel(pixel)

        if not pixel_is_equal(color, pixel, tol=35):
            return False
    return True


def check_line_for_color(  # pylint: disable=too-many-arguments
    vm_index, x_1, y_1, x_2, y_2, color: tuple[int, int, int]
) -> bool:
    coordinates = get_line_coordinates(x_1, y_1, x_2, y_2)
    iar = np.asarray(screenshot(vm_index))

    for coordinate in coordinates:
        pixel = iar[coordinate[1]][coordinate[0]]
        pixel = convert_pixel(pixel)

        if pixel_is_equal(color, pixel, tol=35):
            return True
    return False


def check_region_for_color(vm_index, region, color):
    left, top, width, height = region

    iar = np.asarray(screenshot(vm_index))

    for x_index in range(left, left + width):
        for y_index in range(top, top + height):
            pixel = iar[y_index][x_index]
            pixel = convert_pixel(pixel)
            if pixel_is_equal(color, pixel, tol=35):
                return True

    return False


def region_is_color(vm_index, region, color):
    left, top, width, height = region

    iar = np.asarray(screenshot(vm_index))

    for x_index in range(left, left + width, 2):
        for y_index in range(top, top + height, 2):
            pixel = iar[y_index][x_index]
            pixel = convert_pixel(pixel)
            # print(x_index, y_index, pixel)
            if not pixel_is_equal(color, pixel, tol=35):
                return False

    return True


def convert_pixel(bad_format_pixel):
    red = bad_format_pixel[2]
    green = bad_format_pixel[1]
    blue = bad_format_pixel[0]
    return [red, green, blue]


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


def get_line_coordinates(x_1, y_1, x_2, y_2) -> list[tuple[int, int]]:
    coordinates = []
    delta_x = abs(x_2 - x_1)
    delta_y = abs(y_2 - y_1)
    step_x = -1 if x_1 > x_2 else 1
    step_y = -1 if y_1 > y_2 else 1
    error = delta_x - delta_y

    while x_1 != x_2 or y_1 != y_2:
        coordinates.append((x_1, y_1))
        double_error = 2 * error
        if double_error > -delta_y:
            error -= delta_y
            x_1 += step_x
        if double_error < delta_x:
            error += delta_x
            y_1 += step_y

    coordinates.append((x_1, y_1))
    return coordinates
