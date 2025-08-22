from concurrent.futures import Future, ThreadPoolExecutor, as_completed
import os
from os.path import abspath, dirname, join

import cv2
import numpy as np

from pyclashbot.utils.image_handler import open_from_path


# =============================================================================
# IMAGE RECOGNITION FUNCTIONS
# =============================================================================

def find_image(
    image: np.ndarray,
    folder: str,
    tolerance: float = 0.88,
) -> tuple[int, int] | None:
    """Find the first matching reference image in a screenshot
    
    Args:
        image: image to search through
        folder: folder containing reference images (within reference_images directory)
        tolerance: matching tolerance (0.0 to 1.0)
        
    Returns:
        tuple[int, int] | None: (x, y) coordinates of found image, or None if not found
    """
    locations = find_references(image, folder, tolerance)
    coord = get_first_location(locations)
    if coord is not None:
        return (coord[1], coord[0])  # Convert from [y, x] to (x, y)
    return None


def find_references(
    image: np.ndarray,
    folder: str,
    tolerance=0.88,
) -> list[list[int] | None]:
    """Find all reference images in a screenshot

    Args:
    ----
        image (numpy.ndarray): image to find references in
        folder (str): folder to find references (from within reference_images)
        tolerance (float, optional): tolerance. Defaults to 0.88.

    Returns:
    -------
        list[list[int] | None]: coordinate locations

    """
    top_level = dirname(__file__)
    reference_folder = abspath(join(top_level, "reference_images", folder))

    reference_images = [
        open_from_path(join(reference_folder, name))
        for name in os.listdir(reference_folder)
        if name.endswith(".png") or name.endswith(".jpg")
    ]

    with ThreadPoolExecutor(
        max_workers=len(reference_images),
        thread_name_prefix="ImageRecognition",
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
    """Detects pixel location of a template in an image using template matching

    Args:
        image (numpy.ndarray): image to find template within
        template (numpy.ndarray): template image to match to
        threshold (float, optional): matching threshold. Defaults to 0.8

    Returns:
        list[int] | None: pixel location [y, x] or None if not found
    """
    img_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_RGB2GRAY)

    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    return None if len(loc[0]) != 1 else [int(loc[0][0]), int(loc[1][0])]


# =============================================================================
# PIXEL RECOGNITION FUNCTIONS
# =============================================================================


def pixel_is_equal(
    pix1: tuple[int, int, int] | list[int],
    pix2: tuple[int, int, int] | list[int],
    tol: float,
) -> bool:
    """Check if two pixels are equal within tolerance

    Args:
    ----
        pix1: first RGB pixel
        pix2: second RGB pixel
        tol: color tolerance

    Returns:
    -------
        bool: whether pixels are equal within tolerance

    """
    diff_r = abs(int(pix1[0]) - int(pix2[0]))
    diff_g = abs(int(pix1[1]) - int(pix2[1]))
    diff_b = abs(int(pix1[2]) - int(pix2[2]))
    return (diff_r < tol) and (diff_g < tol) and (diff_b < tol)


def check_line_for_color(
    emulator,
    x_1: int,
    y_1: int,
    x_2: int,
    y_2: int,
    color: tuple[int, int, int],
) -> bool:
    """Check if any pixel along a line matches a specific color

    Args:
        emulator: emulator instance
        x_1, y_1, x_2, y_2: line coordinates
        color: RGB color to check for

    Returns:
        bool: True if any pixel on line matches color
    """
    coordinates = get_line_coordinates(x_1, y_1, x_2, y_2)
    iar = np.asarray(emulator.screenshot())

    for coordinate in coordinates:
        pixel = iar[coordinate[1]][coordinate[0]]
        pixel = convert_pixel(pixel)

        if pixel_is_equal(color, pixel, tol=35):
            return True
    return False


def region_is_color(emulator, region: list, color: tuple[int, int, int]) -> bool:
    """Check if entire region matches a specific color (sampled every 2 pixels)

    Args:
        emulator: emulator instance
        region: [left, top, width, height] region to check
        color: RGB color to check for

    Returns:
        bool: True if entire region matches color
    """
    left, top, width, height = region
    iar = np.asarray(emulator.screenshot())

    for x_index in range(left, left + width, 2):
        for y_index in range(top, top + height, 2):
            pixel = iar[y_index][x_index]
            pixel = convert_pixel(pixel)
            if not pixel_is_equal(color, pixel, tol=35):
                return False

    return True


def all_pixels_are_equal(
    pixels_1: list,
    pixels_2: list,
    tol: float,
) -> bool:
    """Check if two lists of pixels are equal within tolerance

    Args:
        pixels_1: first list of pixels
        pixels_2: second list of pixels
        tol: color tolerance

    Returns:
        bool: True if all pixels match within tolerance
    """
    for pixel1, pixel2 in zip(pixels_1, pixels_2):
        if not pixel_is_equal(pixel1, pixel2, tol):
            return False
    return True


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def get_first_location(
    locations: list[list[int] | None],
    flip=False,
) -> list[int] | None:
    """Get the first valid location from a list of locations

    Args:
    ----
        locations: list of coordinate locations
        flip: whether to flip x,y coordinates

    Returns:
    -------
        list[int] | None: first valid location or None

    """
    return next(
        (
            [location[1], location[0]] if flip else location
            for location in locations
            if location is not None
        ),
        None,
    )


def check_for_location(locations: list[list[int] | None]) -> bool:
    """Check if any location in the list is valid

    Args:
    ----
        locations: list of coordinate locations

    Returns:
    -------
        bool: True if any location is not None

    """
    return any(location is not None for location in locations)


def convert_pixel(bgr_pixel) -> list[int]:
    """Convert BGR pixel format to RGB

    Args:
        bgr_pixel: pixel in BGR format

    Returns:
        list[int]: pixel in RGB format [red, green, blue]
    """
    red = bgr_pixel[2]
    green = bgr_pixel[1]
    blue = bgr_pixel[0]
    return [red, green, blue]


def get_line_coordinates(
    x_1: int, y_1: int, x_2: int, y_2: int
) -> list[tuple[int, int]]:
    """Get all pixel coordinates along a line using Bresenham's algorithm

    Args:
        x_1, y_1: start coordinates
        x_2, y_2: end coordinates

    Returns:
        list[tuple[int, int]]: list of (x, y) coordinates along the line
    """
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
