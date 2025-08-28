import os
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
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
    subcrop: tuple[int, int, int, int] | None = None,
    show_image: bool = False,
) -> tuple[int, int] | None:
    """Find matching reference image in screenshot.
    
    Args:
        image: Screenshot to search in
        folder: Reference images folder name
        tolerance: Match threshold (0.0-1.0)
        subcrop: Optional search region (x1, y1, x2, y2)
    
    Returns:
        (x, y) coordinates if found, None otherwise
    """
    # Apply subcrop if specified
    search_region = image
    offset_x, offset_y = 0, 0
    
    if subcrop:
        x1, y1, x2, y2 = subcrop
        search_region = image[y1:y2, x1:x2]
        offset_x, offset_y = x1, y1

    # Find reference matches
    locations, filenames = find_references(search_region, folder, tolerance)
    match_coord = get_first_location(locations)
    
    if match_coord:
        # Log which reference image matched
        for i, loc in enumerate(locations):
            if loc is not None:
                print(f"Matched: {filenames[i]}")
                break
        
        # Convert to (x,y) and adjust for subcrop offset
        return (match_coord[1] + offset_x, match_coord[0] + offset_y)
    
    return None


def find_references(
    image: np.ndarray,
    folder: str,
    tolerance=0.88,
) -> tuple[list[list[int] | None], list[str]]:
    """Find all reference image matches using parallel processing."""
    # Load reference images
    ref_folder = abspath(join(dirname(__file__), "reference_images", folder))
    filenames = [f for f in os.listdir(ref_folder) if f.endswith((".png", ".jpg"))]
    reference_images = [open_from_path(join(ref_folder, name)) for name in filenames]
    
    # Parallel template matching
    with ThreadPoolExecutor(max_workers=len(reference_images), 
                           thread_name_prefix="ImageMatch") as executor:
        futures = [executor.submit(compare_images, image, template, tolerance) 
                  for template in reference_images]
        results = [future.result() for future in as_completed(futures)]
    
    return results, filenames


def compare_images(image: np.ndarray, template: np.ndarray, threshold=0.8):
    """Find template in image using OpenCV template matching.
    
    Returns:
        [y, x] coordinates if single match found, None otherwise
    """
    # Convert to grayscale for matching
    img_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_RGB2GRAY)

    # Skip if template is larger than search image
    if (template_gray.shape[0] > img_gray.shape[0] or 
        template_gray.shape[1] > img_gray.shape[1]):
        return None

    # Template matching
    result = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    match_locations = np.where(result >= threshold)

    # Return single match location or None
    return ([int(match_locations[0][0]), int(match_locations[1][0])] 
            if len(match_locations[0]) == 1 else None)


# =============================================================================
# PIXEL RECOGNITION FUNCTIONS
# =============================================================================


def pixel_is_equal(pix1, pix2, tol: float) -> bool:
    """Check if two RGB pixels are equal within tolerance."""
    return all(abs(int(pix1[i]) - int(pix2[i])) < tol for i in range(3))


def check_line_for_color(
    emulator,
    x_1: int,
    y_1: int,
    x_2: int,
    y_2: int,
    color: tuple[int, int, int],
) -> bool:
    """Check if any pixel along a line matches the specified color."""
    line_coords = get_line_coordinates(x_1, y_1, x_2, y_2)
    screenshot = np.asarray(emulator.screenshot())

    for x, y in line_coords:
        pixel = convert_pixel(screenshot[y][x])
        if pixel_is_equal(color, pixel, tol=35):
            return True
    
    return False


def region_is_color(emulator, region: list, color: tuple[int, int, int]) -> bool:
    """Check if entire region matches color (sampled every 2 pixels)."""
    left, top, width, height = region
    screenshot = np.asarray(emulator.screenshot())

    # Sample every other pixel for performance
    for x in range(left, left + width, 2):
        for y in range(top, top + height, 2):
            pixel = convert_pixel(screenshot[y][x])
            if not pixel_is_equal(color, pixel, tol=35):
                return False
    
    return True


def all_pixels_are_equal(pixels_1: list, pixels_2: list, tol: float) -> bool:
    """Check if all corresponding pixels in two lists are equal within tolerance."""
    return all(pixel_is_equal(p1, p2, tol) for p1, p2 in zip(pixels_1, pixels_2))


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def get_first_location(locations: list[list[int] | None], flip=False) -> list[int] | None:
    """Get first non-None location from list."""
    for location in locations:
        if location is not None:
            return [location[1], location[0]] if flip else location
    return None


def check_for_location(locations: list[list[int] | None]) -> bool:
    """Check if any location in list is valid (not None)."""
    return any(location is not None for location in locations)


def convert_pixel(bgr_pixel) -> list[int]:
    """Convert BGR pixel to RGB format."""
    return [bgr_pixel[2], bgr_pixel[1], bgr_pixel[0]]  # [R, G, B]


def get_line_coordinates(x_1: int, y_1: int, x_2: int, y_2: int) -> list[tuple[int, int]]:
    """Get all pixel coordinates along a line using Bresenham's algorithm."""
    coords = []
    dx, dy = abs(x_2 - x_1), abs(y_2 - y_1)
    step_x, step_y = (1 if x_1 < x_2 else -1), (1 if y_1 < y_2 else -1)
    error = dx - dy

    while x_1 != x_2 or y_1 != y_2:
        coords.append((x_1, y_1))
        error2 = 2 * error
        
        if error2 > -dy:
            error -= dy
            x_1 += step_x
        if error2 < dx:
            error += dx
            y_1 += step_y

    coords.append((x_1, y_1))
    return coords
