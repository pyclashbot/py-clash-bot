import time
import numpy


from pyclashbot.bot.navigation import get_to_bannerbox, wait_for_clash_main_menu
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.memu.client import click, screenshot


def collect_bannerbox_chests(logger):
    print("Opening bannerbox menu from main")
    get_to_bannerbox()

    #click '100 tickets' button
    print('clicking 100 tickets button in the bottom left to buy a chest')
    get_to_confrim_battlebox_purchase_page()

    #buy a chest if u can
    print("checking if can buy a chest this time")
    if check_if_can_purchase_a_battlebox():
        print("can buy a chest this time")
        buy_a_battlebox()
    else:
        print("cant buy a chest this time")
        #close confirm purchase page
        click(353,177)
        time.sleep(0.33)

    #close page
    print('closing bannerbox menu to get back to clash main')
    click(354,67)

    print('waiting for main to return')
    if wait_for_clash_main_menu(logger)=="restart":
        print("Failure wiht wait_for_clash_main_menu() in collect_bannerbox_chests()")
        return "restart"


def buy_a_battlebox():
    click(205,505)
    time.sleep(1)

    #skip thru rewards
    click(20,440,clicks=20,interval=0.33)
    

def check_if_can_purchase_a_battlebox():
    iar=numpy.asarray(screenshot())

    for x_coord in range(170,195):
        this_pixel=iar[500][x_coord]
        if pixel_is_equal(this_pixel,[255,0,0],tol=35):
            return False
    return True


def get_to_confrim_battlebox_purchase_page():
    click(312,606)
    wait_for_confirm_battlebox_purchase_page()


def wait_for_confirm_battlebox_purchase_page():
    while not check_for_confirm_battlebox_purchase_page():
        pass


def check_for_confirm_battlebox_purchase_page():
    iar=numpy.asarray(screenshot())

    confirm_purchase_text_exists=False
    for x_coord in range(150,250):
        this_pixel=iar[180][x_coord]
        if pixel_is_equal(this_pixel,[255,255,255],tol=35):
            confirm_purchase_text_exists=True


    info_button_exists=False
    for x_coord in range(337,352):
        this_pixel=iar[405][x_coord]
        if pixel_is_equal(this_pixel,[76,174,255],tol=35):
            info_button_exists=True



    if info_button_exists and confirm_purchase_text_exists:
        return True
    return False
