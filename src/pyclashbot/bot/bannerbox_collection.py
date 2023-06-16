import time

import numpy

from pyclashbot.bot.navigation import get_to_bannerbox, wait_for_clash_main_menu
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.memu.client import click, screenshot

"""Methods that have to do with the collection of the bannerbox rewards

"""


def collect_bannerbox_chests(logger):
    """main method for collecing the bannerbox chests from the clash main menu"""

    # get to the bannerbox menu
    logger.change_status("Opening bannerbox menu from main")
    if get_to_bannerbox(logger) == "restart":
        return "restart"

    # click '100 tickets' button
    logger.change_status(
        "clicking 100 tickets button in the bottom left to buy a chest"
    )
    if get_to_confrim_battlebox_purchase_page() == "restart":
        logger.change_status("Failure with get_to_confrim_battlebox_purchase_page()")
        return "restart"

    # handle welcome to bannerbox popup
    if check_for_welcome_to_bannerbox_popup():
        handle_welcome_to_bannerbox_popup()

    # buy a chest if possible
    logger.change_status("checking if can buy a chest this time")
    if check_if_can_purchase_a_battlebox():
        logger.change_status("can buy a chest this time")
        buy_a_battlebox()
    # if cant purchase a chest, close the confirm purchase page
    else:
        logger.change_status("cant buy a chest this time")
        # close confirm purchase page
        click(353, 177)
        time.sleep(0.33)

    # close page
    logger.change_status("closing bannerbox menu to get back to clash main")
    click(354, 67)

    # return to the clash main menu
    logger.change_status("waiting for main to return")
    if wait_for_clash_main_menu(logger) == "restart":
        logger.change_status(
            "Failure wiht wait_for_clash_main_menu() in collect_bannerbox_chests()"
        )
        return "restart"


def buy_a_battlebox():
    """method for buying a battlebox from the bannerbox menu
    args:
        None
    returns:
        None

    """
    click(205, 505)
    time.sleep(1)

    # skip thru rewards
    click(20, 440, clicks=20, interval=0.33)


def check_if_can_purchase_a_battlebox():
    """method for checking if a battlebox can be purchased while on the bannerbox menu
    args:
        None
    returns:
        bool, True if a battlebox can be purchased, False otherwise

    """
    iar = numpy.asarray(screenshot())

    for x_coord in range(170, 195):
        this_pixel = iar[500][x_coord]
        if pixel_is_equal(this_pixel, [255, 0, 0], tol=35):
            return False
    return True


def get_to_confrim_battlebox_purchase_page():
    """Method to get to the confirm battlebox purchase page from the bannerbox menu
    args:
        None
    returns:
        None
    """
    click(312, 606)
    if wait_for_confirm_battlebox_purchase_page() == "restart":
        return "restart"


def wait_for_confirm_battlebox_purchase_page():
    """Method to wait for the confirm battlebox purchase page to load
    args:
        None
    returns:
        None
    """
    start_time = time.time()
    while not check_for_confirm_battlebox_purchase_page():
        time_taken = time.time() - start_time
        if time_taken > 10:
            return "restart"


def check_for_confirm_battlebox_purchase_page():
    """Method to scan for the confirm battlebox purchase page
    args:
        None
    returns:
        bool, True if the confirm battlebox purchase page is found, False otherwise
    """
    iar = numpy.asarray(screenshot())

    confirm_purchase_text_exists = False
    for x_coord in range(150, 250):
        this_pixel = iar[180][x_coord]
        if pixel_is_equal(this_pixel, [255, 255, 255], tol=35):
            confirm_purchase_text_exists = True

    info_button_exists = False
    for x_coord in range(337, 352):
        this_pixel = iar[405][x_coord]
        if pixel_is_equal(this_pixel, [76, 174, 255], tol=35):
            info_button_exists = True

    if info_button_exists and confirm_purchase_text_exists:
        return True
    return False


def handle_welcome_to_bannerbox_popup():
    """Method to close the 'welcome to bannerbox' popup
    args:
        None
    returns:
        None
    """
    click(20, 440, clicks=5, interval=1)
    time.sleep(1)


def check_for_welcome_to_bannerbox_popup():
    """Method to scan for pixels that indicate the 'welcome to bannerbox' popup is present
    args:
        None
    returns:
        bool, True if the 'welcome to bannerbox' popup is present, False otherwise
    """
    iar = numpy.asarray(screenshot())

    welcome_to_bannerbox_text_exists = False
    for x_coord in range(180, 200):
        this_pixel = iar[403][x_coord]
        if pixel_is_equal(this_pixel, [98, 102, 113], tol=35):
            welcome_to_bannerbox_text_exists = True

    king_crown_graphic_exists = False
    for x_coord in range(60, 100):
        this_pixel = iar[440][x_coord]
        if pixel_is_equal(this_pixel, [255, 210, 155], tol=35):
            king_crown_graphic_exists = True

    if king_crown_graphic_exists and welcome_to_bannerbox_text_exists:
        return True
    return False
