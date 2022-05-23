
from asyncio import sslproto
from http.client import PROXY_AUTHENTICATION_REQUIRED

import time

from matplotlib import pyplot as plt
from numpy import true_divide

from pyclashbot.client import check_quit_key_press, click, refresh_screen, screenshot, scroll_down, scroll_down_fast, scroll_up_fast
from pyclashbot.image_rec import find_references, pixel_is_equal
from pyclashbot.logger import Logger
from pyclashbot.state import check_if_on_clash_main_menu, return_to_clash_main_menu

#can removepyautogui. its here for debugging
import pyautogui

def upgrade_cards_from_main(logger):
    #get to card menu from main
    logger.log("Getting to card page")
    getto_card_page(logger)
    loops=0
    while loops<10:
        loops=loops+1
        check_quit_key_press()
        #check if loops is too many
        if loops>10:
            logger.log("Found no upgrades. Returning")
            return
        #look for upgrade arrows
        arrow_coords=find_upgradable_cards()
        if arrow_coords is not None:
        #if arrows found
            logger.log("Found upgrade arrow.")
            #click arrow
            logger.log("Clicking upgrade arrow")
            click(arrow_coords[1],arrow_coords[0])
            time.sleep(0.5)
            #click upgrade1
            logger.log("Clicking first upgrade button")
            upgrade_1_coords=look_for_upgrade_button_1()
            if upgrade_1_coords is not None:
                click(upgrade_1_coords[1],upgrade_1_coords[0])
            else:
                logger.log("Couldn't find upgrade1 button")
            time.sleep(0.5)
            #click upgrade2
            logger.log("Clicking second upgrade button")
            upgrade_2_coords=look_for_upgrade_button_2()
            if upgrade_2_coords is not None:
                click(upgrade_2_coords[1],upgrade_2_coords[0])
            else:
                logger.log("Couldn't find upgrade2 button")
            time.sleep(0.5)
            #click upgrade_confirm
            logger.log("Clicking upgrade confirm button")
            upgrade_confirm_coords=look_for_upgrade_confirm_button()
            if upgrade_confirm_coords is not None:
                click(upgrade_confirm_coords[1],upgrade_confirm_coords[0])
            else:
                logger.log("Couldn't find upgrade confirm button")
            time.sleep(0.5)
            #skip through
            logger.log("Skipping through screens.")
            click(x=349,y=250)
            time.sleep(0.2)
            click(x=20,y=540,clicks=5,interval=0.2)
            scroll_down_fast()
            time.sleep(0.2)
            scroll_down_fast()
            time.sleep(0.2)
        else:
        #if arrows not found
            logger.log("No upgrades found yet.")
            #scroll
            scroll_down_fast()
            scroll_down_fast()
            scroll_down_fast()
            scroll_down_fast()
            scroll_down_fast()
            scroll_down_fast()
            time.sleep(0.5)
    time.sleep(1)
    return_to_clash_main_menu()
    time.sleep(1)
    
    
def look_for_upgrade_button_1():
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
        "14.png",
        "15.png",
        "16.png",
        "17.png",
        "18.png",
        "19.png",
        "20.png",
        "21.png",
        "22.png",
        "23.png",
        "24.png",
        "25.png",
        "26.png",
        "27.png",
        "28.png",
        "29.png",
        "30.png",
        "31.png",
    ]
    locations = find_references(
        screenshot=screenshot(),
        folder="upgrade_button_1",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None


def look_for_upgrade_button_2():
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
        "14.png",
    ]
    locations = find_references(
        screenshot=screenshot(),
        folder="upgrade_button_2",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None


def look_for_upgrade_confirm_button():
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
        "6.png",
        "7.png",
    ]
    locations = find_references(
        screenshot=screenshot(),
        folder="upgrade_confirm_button",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None


def find_upgradable_cards():
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
        "14.png",
        "15.png",
        "16.png",
        "17.png",
        "18.png",
        "19.png",
        "20.png",
        "21.png",
        "22.png",
        "23.png",
        "24.png",
        "25.png",
        "26.png",
        "27.png",
        "28.png",
        "29.png",
        "30.png",
        "31.png",
        "32.png",
        "33.png",
        "34.png",
        "35.png",
        "36.png",
        "37.png",
        "38.png",
        "39.png",
        "40.png",
        "41.png",
        "42.png",
        "43.png",
        "44.png",
        "45.png",
        "46.png",
        "47.png",
        "48.png",
        "49.png",
        "50.png",
        "51.png",
        "52.png",
        "53.png",
        "54.png",
        "55.png",
        "56.png",
        "57.png",
        "58.png",
        "59.png",
        "60.png",
        "61.png",
        "62.png",
        "63.png",
        "64.png",
        "65.png",
        "66.png",
        "e1.png",
        "e2.png",
        "e3.png",
        "e4.png",
        "e5.png",
        "e6.png",
        "e7.png",
        "e8.png",
        "e9.png",
        "e10.png",
        "e11.png",
        "e12.png",
        "e13.png",
        "e14.png",
        "e15.png",
        "e16.png",
        "e17.png",
        "e18.png",
        "e19.png",
        "e20.png",
        "e21.png",
        "e22.png",
        "e23.png",
        "e24.png",
        "e25.png",
        "e26.png",
        "e27.png",
        "e28.png",
        "e29.png",
        "e30.png",
        "e31.png",
        "e32.png",
        "e33.png",
        "e34.png",
        "e35.png",
        "e36.png",
        "e37.png",
        "e38.png",
        "e39.png",
        "e40.png",
        "e41.png",
        "e42.png",
        "e43.png",
        "e44.png",
        
    ]

    locations = find_references(
        screenshot=screenshot(),
        folder="green_upgrade_button",
        names=references,
        tolerance=0.97
    )

    for location in locations:
        if location is not None:
            if confirm_upgrade_arrow(location):
                return location
    return None


def confirm_upgrade_arrow(location):
    #location of center of arrow
    x=location[1]+3
    y=location[0]+7
    coords=[x,y]
    
    iar = refresh_screen()
    arrow_pix = iar[y][x]
    sentinel = [146,255,94]

    if pixel_is_equal(arrow_pix,sentinel,20):
        return True
    return False


def getto_card_page(logger):
    click(x=100,y=630)
    time.sleep(2)
    loops=0
    while not check_for_elixer_icon():
        logger.log("Not elixer button. Moving pages")
        time.sleep(1)
        click(x=100,y=630)
        loops=loops+1
        if loops>10:
            logger.log("Couldn't make it to card page")
            return"quit"
        time.sleep(0.2)
    scroll_up_fast()
    logger.log("Made it to card page")
    time.sleep(1)
 
    
def check_for_elixer_icon():
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
        screenshot=screenshot(),
        folder="card_page_elixer_icon",
        names=references,
        tolerance=0.97
    )

    for location in locations:
        if location is not None:
            return location
    return None


def find_card_page_logo():
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
    ]
    locations = find_references(
        screenshot=screenshot(),
        folder="card_page_logo",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            # click(location[1],location[0])
            return location
    return None
