import os
import time
from os.path import dirname, join

import matplotlib.pyplot as plt
import numpy
import pyautogui
import pygetwindow
from ahk import AHK

from pyclashbot.utils import setup_ahk
from pyclashbot.utils.image_logging import save_this_screen_image_to_log

setup_ahk()  # setup autohotkey, install if necessary
ahk = AHK()


def print_pix_list(pix_list):
    for pix in pix_list:
        print(pix[0], pix[1], pix[2])


def screenshot(region=None):
    """Method to return a screenshot of a given region

    Args:
        region (tuple, optional): Region to take a screenshot of. Defaults to None.

    Returns:
        PIL.Image: Screenshot of the given region
    """
    if region is None:
        region = [0, 0, 500, 700]
    return pyautogui.screenshot(region=region)  # type: ignore


def make_reference_image_list(size):
    # Method to make a reference array of a given size
    reference_image_list = []

    for n in range(size):
        n = n + 1
        image_name = f"{n}.png"
        reference_image_list.append(image_name)

    return reference_image_list


def scroll_up_fast():
    """Method for scrolling up faster when interacting with a scrollable menu"""
    origin = pyautogui.position()
    pyautogui.moveTo(x=215, y=300)
    pyautogui.dragTo(x=215, y=350, button="left", duration=0.5)
    pyautogui.moveTo(x=origin[0], y=origin[1])


def scroll_down_fast():
    """Method for scrolling down faster when interacting with a scrollable menu"""
    origin = pyautogui.position()
    pyautogui.moveTo(x=215, y=350)
    time.sleep(0.1)
    pyautogui.dragTo(x=215, y=300, button="left", duration=0.5)
    pyautogui.moveTo(x=origin[0], y=origin[1])


def scroll_down_super_fast():
    """Method for scrolling down even faster when interacting with a scrollable menu"""
    origin = pyautogui.position()
    pyautogui.moveTo(x=215, y=400)
    time.sleep(0.1)
    pyautogui.dragTo(x=215, y=300, button="left", duration=0.2)
    pyautogui.moveTo(x=origin[0], y=origin[1])


def scroll_up_super_fast():
    """Method for scrolling down even faster when interacting with a scrollable menu"""
    origin = pyautogui.position()
    pyautogui.moveTo(x=215, y=300)
    time.sleep(0.1)
    pyautogui.dragTo(x=215, y=400, button="left", duration=0.2)
    pyautogui.moveTo(x=origin[0], y=origin[1])


def get_file_count(folder):
    """Method to return the amount of a files in a given directory

    Args:
        directory (str): Directory to count files in

    Returns:
        int: Amount of files in the given directory
    """
    directory = join(dirname(__file__)[:-4], "detection", "reference_images", folder)

    return sum(len(files) for root_dir, cur_dir, files in os.walk(directory))


def compare_coords(coord1, coord2):
    """Method to compare the equality of two coords

    Args:
        coord1 (tuple): First coord
        coord2 (tuple): Second coord

    Returns:
        bool: True if the coords are equal, False otherwise
    """
    return coord1[0] == coord2[0] and coord1[1] == coord2[1]


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
    save_this_screen_image_to_log(logger)

    origin = ahk.mouse_position
    duration = min(10, duration)  # 10 seconds max (ahk limitation)
    speed = duration * 10  # speed for ahk (0-100)

    # Tolerance for timer comparisons
    tol = 0.5

    # timer for mouse movement
    start = time.time()
    ahk.mouse_move(x=x, y=y, speed=speed, blocking=False)

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
                ahk.mouse_move(x=x, y=y, speed=speed, blocking=False)
                attempts += 1
        for _ in range(clicks):
            ahk.click()
            time.sleep(interval)
    except Exception:
        print("Click method caused a restart...")
        return "restart"
    ahk.mouse_move(x=origin[0], y=origin[1], blocking=False)


def scroll_down():
    """Method for scrolling down when interacting with a scrollable menu"""
    origin = pyautogui.position()
    pyautogui.moveTo(x=215, y=350)
    pyautogui.dragTo(x=215, y=300, button="left", duration=1)
    pyautogui.moveTo(x=origin[0], y=origin[1])


def orientate_terminal():
    """Method for orientating the terminal"""
    try:
        window = pygetwindow.getWindowsWithTitle("Py-ClashBot")[0]
        window.moveTo(732, 0)
    except Exception:
        print("Couldn't orientate terminal")


def show_image(image):
    """Method to show a PIL image using matlibplot

    Args:
        image (PIL.Image): Image to show
    """
    plt.imshow(numpy.array(image))
    plt.show()
