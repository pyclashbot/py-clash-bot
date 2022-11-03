import subprocess
import time


import pygetwindow

from pyclashbot.clashmain import wait_for_clash_main_menu
from pyclashbot.client import (
    check_quit_key_press,
    click,
    orientate_memu,
    orientate_memu_multi,
    orientate_terminal,
    screenshot,
)
from pyclashbot.dependency import setup_memu
from pyclashbot.image_rec import (
    check_for_location,
    find_references,
    get_first_location,
    pixel_is_equal,
)


import numpy

launcher_path = setup_memu()  # setup memu, install if necessary


def wait_for_window(logger, window_name):
    # Method to wait for a given window name to appear
    logger.change_status(f"Waiting for {window_name} to appear")
    while not pygetwindow.getWindowsWithTitle(window_name):
        pass
    logger.change_status(f"Done waiting for {window_name}")


def restart_and_open_clash(logger):
    # Method for restarting Memu and MeMU Multi Manager, opening clash, and
    # waiting for the clash main menu to appear.
    # If Memu is running, close it
    if len(pygetwindow.getWindowsWithTitle("MEmu")) != 0:
        close_memu(logger)

    # If MeMU Multi Manager is running, close it
    if len(pygetwindow.getWindowsWithTitle("Multiple Instance Manager")) != 0:
        close_memu_multi(logger)

    orientate_terminal()

    # Open the Memu Multi Manager
    logger.change_status("Opening MEmu launcher")
    subprocess.Popen(launcher_path)

    # Wait for memu multi to load
    wait_for_window(logger, window_name="Multiple Instance Manager")

    # Orientate the Memu Multi Manager
    orientate_memu_multi()

    # Start Memu Client
    logger.change_status("Starting Memu client instance")
    click(556, 141)

    # Wait for memu to load
    wait_for_window(logger, window_name="Memu")

    # orientate memu client
    orientate_memu()

    # Wait for Memu Client loading screen
    if wait_for_memu_loading_screen(logger)=="restart":
        return restart_and_open_clash(logger)
    time.sleep(3)

    # Skip Memu ads
    if find_clash_app_logo() is None:
        skip_ads(logger)
    time.sleep(3)

    # Wait for clash logo to appear
    if wait_for_clash_logo_to_appear(logger) == "restart":
        logger.change_status("Waited too long for clash logo to appear. Restarting")
        restart_and_open_clash(logger)
    time.sleep(3)

    # Click the clash logo
    logo_coords = find_clash_app_logo()
    if logo_coords is not None:
        click(logo_coords[1], logo_coords[0])

    # Wait for the clash main menu to appear
    orientate_memu()
    if wait_for_clash_main_menu(logger) == "restart":
        restart_and_open_clash(logger)
    time.sleep(3)

    # increment restart counter
    logger.add_restart()


def wait_for_memu_loading_screen(logger):
    # Method to wait for memu loading background to disappear

    logger.change_status("Waiting for Memu Client to load")
    waiting = True

    loops = 0
    while waiting:
        loops += 1
        if loops > 20:
            logger.change_status("Waited too long for memu client to load, restarting")
            return "restart"

        time.sleep(1)

        waiting = check_for_memu_loading_background()
    time.sleep(3)
    logger.change_status("Done waiting for Memu Client to load.")
    time.sleep(3)


def skip_ads(logger):
    # Method for skipping the memu ads that popip up when you start memu

    logger.change_status("Skipping ads")
    for _ in range(4):
        click(445, 600)
        time.sleep(1)
    time.sleep(3)


def wait_for_clash_logo_to_appear(logger):
    # Method for waiting for memu to finish loading and display the memu home
    # menu

    n = 0
    waiting = True
    loops = 0
    while waiting:
        loops += 1
        if loops > 35:
            logger.change_status("Waited too long for clash logo to appear, restarting")
            return "restart"
        n = n + 1
        time.sleep(1)
        logger.change_status(f"Waiting for clash logo to appaer: {str(n)}")

        logo_coords = find_clash_app_logo()

        if logo_coords is not None:
            waiting = False


def check_for_memu_loading_background():
    # Method to check if memu loading background is present in the given moment
    # Using 2 methods

    # Method 1 image recognition
    current_image = screenshot()
    reference_folder = "memu_loading_background"
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
        "6.png",
        "7.png",
        "8.png",
        "9.png",
        "10.png",
        "11.png",
        "12.png",
        "13.png",

    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.99,
    )

    if check_for_location(locations):

        return True

    # Method 2 pixel comparison
    iar = numpy.asarray(current_image)
    pix_list = [
        iar[120][120],
        iar[200][200],
        iar[350][50],
        iar[220][150],
    ]
    sentinel_pix_list = [
        [76, 78, 84],
        [18, 23, 28],
        [19, 13, 10],
        [23, 40, 48],
    ]
    pixel_check = True
    for index in range(4):
        current_pixel = pix_list[index]
        sentinel_pixel = sentinel_pix_list[index]
        if not pixel_is_equal(current_pixel, sentinel_pixel, tol=35):
            pixel_check = False
    if pixel_check:

        return True

    # Method 3 pixel comparison #2 (checks if all pixels are black)
    pixel_check_2 = True
    for pix in pix_list:
        if not pixel_is_equal(pix, [0, 0, 0], tol=30):
            pixel_check_2 = False
    return bool(pixel_check_2)


def find_clash_app_logo():
    # Method to find the coordinates of the clash app logo on the menu home
    # screen

    current_image = screenshot()
    reference_folder = "logo"
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
        "6.png",
        "7.png",
        "8.png",
        "9.png",
        "10.png",
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.99,
    )

    return get_first_location(locations)


def close_memu(logger):
    # Method to close memu
    memu_name_list = ["MEmu", "(MEmu)"]

    for name in memu_name_list:
        try:
            window = pygetwindow.getWindowsWithTitle(name)[0]
            window.close()
            logger.change_status("Closed Memu")
        except BaseException:
            logger.change_status("Couldn't close Memu")
    time.sleep(3)


def close_memu_multi(logger):
    # Method to close memu multi
    mmim_name_list = ["Multiple Instance Manager"]

    for name in mmim_name_list:
        try:
            window = pygetwindow.getWindowsWithTitle(name)[0]
            window.close()
            logger.change_status("Closed MMIM")

        except BaseException:
            logger.change_status("Couldnt close MMIM using title ", name)
    time.sleep(3)
