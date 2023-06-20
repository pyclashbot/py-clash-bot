import os
import sys
import time
from os.path import dirname, join

import pygetwindow
from ahk import AHK
from ahk.directives import NoTrayIcon
from PIL import Image, ImageGrab

if getattr(sys, "frozen", False):
    # The application is frozen
    ahk = AHK(
        executable_path=os.path.join(sys.frozen_dir, "AutoHotkey.exe"),  # type: ignore
        directives=[NoTrayIcon],
    )
else:
    ahk = AHK(directives=[NoTrayIcon])


def screenshot(
    region: list[int | float] | tuple[int, int, int, int] | None = None
) -> Image.Image:
    """Method to return a screenshot of a given region

    Args:
        region (tuple, optional): Region to take a screenshot of. Defaults to None.

    Returns:
        PIL.Image.Image: Screenshot of the given region
    """
    if region is None:
        region = (0, 0, 500, 700)
    else:
        # due to API change, the last two values of the region are now the width and height,
        # not the bottom right corner like with the old API.
        # this fix keeps functionality the same in our codebase
        new_region = (
            region[0],
            region[1],
            region[0] + region[2],
            region[1] + region[3],
        )
        region = tuple(int(x) for x in new_region)
    return ImageGrab.grab(bbox=region)


def make_reference_image_list(size):
    # Method to make a reference array of a given size
    reference_image_list = []

    for n in range(size):
        n = n + 1
        image_name = f"{n}.png"
        reference_image_list.append(image_name)

    return reference_image_list


def get_file_count(folder):
    """Method to return the amount of a files in a given directory

    Args:
        directory (str): Directory to count files in

    Returns:
        int: Amount of files in the given directory
    """
    directory = join(dirname(__file__)[:-4], "detection", "reference_images", folder)

    return sum(len(files) for _, _, files in os.walk(directory))


class MouseMoveException(Exception):
    """Exception for when the mouse moves unexpectedly"""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def click(x, y, duration: float = 1, max_attempts=3, clicks=1, interval=0.1):
    """Method for clicking a given coordinate

    Args:
        x (int): X coordinate
        y (int): Y coordinate
        duration (float, optional): Duration of the click. Defaults to 1.
        max_attempts (int, optional): Maximum amount of attempts to click the given coordinate. Defaults to 3. Set to less than 1 for infinite attempts.
    """
    # save this image to image log
    # save_this_screen_image_to_log(logger)

    origin = ahk.mouse_position
    duration = min(10, duration)  # 10 seconds max (ahk limitation)
    speed = duration * 10  # speed for ahk (0-100)

    # Tolerance for timer comparisons
    tol = 0.5

    # timer for mouse movement
    start = time.time()
    ahk.mouse_move(x=x, y=y, speed=int(speed), blocking=False)

    attempts = 0

    try:
        while ahk.mouse_position != (x, y):
            if attempts > max_attempts > 0:
                raise MouseMoveException(
                    "Couldnt move mouse to given coordinates, aborting"
                )
            if time.time() - start > duration + tol:
                start = time.time()
                time.sleep(duration + tol)
                ahk.mouse_move(x=x, y=y, speed=int(speed), blocking=False)
                attempts += 1
        for _ in range(clicks):
            ahk.click()
            time.sleep(interval)
    except Exception:
        print("Click method caused a restart...")
        return "restart"
    ahk.mouse_move(x=origin[0], y=origin[1], blocking=False)


def scroll_up():
    """Method for scrolling up faster when interacting with a scrollable menu"""
    origin = ahk.mouse_position
    ahk.mouse_position = (215, 300)
    ahk.mouse_drag(x=0, y=50, relative=True, blocking=True)
    ahk.mouse_position = origin


def scroll_down():
    """Method for scrolling down faster when interacting with a scrollable menu"""
    origin = ahk.mouse_position
    ahk.mouse_position = (215, 350)
    ahk.mouse_drag(x=0, y=-50, relative=True, blocking=True)
    ahk.mouse_position = origin


def scroll_down_fast():
    """Method for scrolling down even faster when interacting with a scrollable menu"""
    origin = ahk.mouse_position
    ahk.mouse_position = (215, 400)
    ahk.mouse_drag(x=0, y=-100, relative=True, blocking=True)
    ahk.mouse_position = origin


def scroll_up_fast():
    """Method for scrolling down even faster when interacting with a scrollable menu"""
    origin = ahk.mouse_position
    ahk.mouse_position = (215, 300)
    ahk.mouse_drag(x=0, y=100, relative=True, blocking=True)
    ahk.mouse_position = origin


def scroll_up_fast_on_left_side_of_screen():
    """Method for scrolling down even faster when interacting with a scrollable menu using the left side of the screen"""
    origin = ahk.mouse_position
    ahk.mouse_position = (66, 300)
    ahk.mouse_drag(x=0, y=100, relative=True, blocking=True)
    ahk.mouse_position = origin


def orientate_terminal():
    """Method for orientating the terminal"""
    try:
        window = pygetwindow.getWindowsWithTitle("Py-ClashBot")[0]  # type: ignore
        window.moveTo(732, 0)
    except Exception:
        print("Couldn't orientate terminal")
