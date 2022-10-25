import os
import sys
import time

import keyboard
import numpy
import pyautogui
import pygetwindow
from ahk import AHK
from matplotlib import pyplot as plt

from pyclashbot.dependency import setup_ahk

setup_ahk()  # setup autohotkey, install if necessary
ahk = AHK()


def get_next_ssid(current_ssid, ssid_total):
    """ Method to cycle through a list of ints (1 -> 2 -> 3 -> 1 -> 2 -> 3 -> ...)

    Args:
        current_ssid (int): Current SSID
        ssid_total (int): Total number of SSIDs

    Returns:
        int: Next SSID
    """
    return 0 if (current_ssid + 1) == ssid_total else current_ssid + 1


def screenshot(region=None):
    """ Method to return a screenshot of a given region

    Args:
        region (tuple, optional): Region to take a screenshot of. Defaults to None.

    Returns:
        PIL.Image: Screenshot of the given region
    """
    if region is None:
        region = [0, 0, 500, 700]
    return pyautogui.screenshot(region=region)  # type: ignore


def scroll_up_fast():
    """ Method for scrolling up faster when interacting with a scrollable menu """
    origin = pyautogui.position()
    pyautogui.moveTo(x=215, y=300)
    pyautogui.dragTo(x=215, y=350, button='left', duration=0.5)
    pyautogui.moveTo(x=origin[0], y=origin[1])


def scroll_down_fast():
    """ Method for scrolling down faster when interacting with a scrollable menu """
    origin = pyautogui.position()
    pyautogui.moveTo(x=215, y=350)
    pyautogui.dragTo(x=215, y=300, button='left', duration=0.5)
    pyautogui.moveTo(x=origin[0], y=origin[1])


def scroll_down_super_fast():
    """ Method for scrolling down even faster when interacting with a scrollable menu """
    origin = pyautogui.position()
    pyautogui.moveTo(x=215, y=400)
    pyautogui.dragTo(x=215, y=300, button='left', duration=0.2)
    pyautogui.moveTo(x=origin[0], y=origin[1])


def check_quit_key_press():
    """  Method for terminating the program upon key press"""
    if keyboard.is_pressed("space"):
        print("Space is held. Quitting the program")
        sys.exit()
    if keyboard.is_pressed("pause"):
        print("Pausing program until pause is held again")
        time.sleep(5)
        pressed = False
        while not (pressed):
            time.sleep(0.05)
            if keyboard.is_pressed("pause"):
                print("Pause held again. Resuming program.")
                time.sleep(3)
                pressed = True


def get_file_count(directory):
    """ Method to return the amount of a files in a given directory

    Args:
        directory (str): Directory to count files in

    Returns:
        int: Amount of files in the given directory
    """
    # print('file count:', count)
    return sum(len(files) for root_dir, cur_dir, files in os.walk(directory))


def orientate_memu():
    """ Method for orientating Memu client """
    try:
        window_memu = pygetwindow.getWindowsWithTitle('MEmu')[0]
        window_memu.minimize()
        window_memu.restore()
        time.sleep(0.2)
        try:
            window_memu.moveTo(0, 0)
        except pygetwindow.PyGetWindowException:
            print("Had trouble moving MEmu window.")
        time.sleep(0.2)
        try:
            window_memu.resizeTo(460, 680)
        except pygetwindow.PyGetWindowException:
            print("Had trouble resizing MEmu window")
    except Exception:
        print("Couldnt orientate MEmu")


def orientate_memu_multi():
    """ Method for orientating the Memu Multi Manager """
    try:
        try:
            window_mimm = pygetwindow.getWindowsWithTitle(
                'Multiple Instance Manager')[0]
        except Exception:
            window_mimm = pygetwindow.getWindowsWithTitle('Multi-MEmu')[0]

        window_mimm.minimize()
        window_mimm.restore()
        # window_mimm.moveTo(200, 200)
        time.sleep(0.2)
        window_mimm.moveTo(0, 0)
    except Exception:
        print("Couldnt orientate MIMM")


def show_image(image):
    """ Method to show a PIL image using matlibplot

    Args:
        image (PIL.Image): Image to show
    """
    plt.imshow(numpy.array(image))
    plt.show()


def compare_coords(coord1, coord2):
    """  Method to compare the equality of two coords

    Args:
        coord1 (tuple): First coord
        coord2 (tuple): Second coord

    Returns:
        bool: True if the coords are equal, False otherwise
    """
    return (coord1[0] == coord2[0] and coord1[1] == coord2[1])


def click(x, y, duration=1):
    """  Method for clicking a given coordinate

    Args:
        x (int): X coordinate
        y (int): Y coordinate
        duration (int, optional): Duration of the click. Defaults to 1.
    """
    # 30 speed = 3 seconds
    speed = duration * 10

    # Tolerance for timer comparisons
    tol = 0.5

    # timer for mouse movement
    start = time.time()
    ahk.mouse_move(x=x, y=y, speed=speed, blocking=False)

    while ahk.mouse_position != (x, y):
        if (time.time() - start) > (duration) + tol:
            start = time.time()
            ahk.mouse_move(x=x, y=y, speed=speed, blocking=False)
    ahk.click()


def scroll_down():
    """  Method for scrolling down when interacting with a scrollable menu """
    origin = pyautogui.position()
    pyautogui.moveTo(x=215, y=350)
    pyautogui.dragTo(x=215, y=300, button='left', duration=1)
    pyautogui.moveTo(x=origin[0], y=origin[1])


def orientate_terminal():
    """ Method for orientating the terminal """
    try:
        window = pygetwindow.getWindowsWithTitle("Py-ClashBot")[0]
        window.moveTo(725, 0)
    except Exception:
        print("Couldn't orientate terminal")
