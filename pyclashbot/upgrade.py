
#from socket import send_fds
import random
import time

import numpy
# here for debugging
import pyautogui

from pyclashbot.client import (check_quit_key_press, click, refresh_screen,
                               screenshot, scroll_down_fast,
                               scroll_down_super_fast, scroll_up_fast)
from pyclashbot.image_rec import (check_for_location, find_references,
                                  get_first_location, pixel_is_equal)
from pyclashbot.state import (check_if_on_level_up_screen,
                              return_to_clash_main_menu)


def upgrade_cards_from_main(logger):
    # get to card menu from main
    logger.log("Getting to card page")
    getto_card_page(logger)
    for loops in range(1, 6):
        check_quit_key_press()
        # check if loops is too many
        if loops > 5:
            logger.log("Found no upgrades. Returning")
            return
        # look for upgrade arrows
        arrow_coords = find_upgradable_cards()
        if arrow_coords is not None:
            # if arrows found
            logger.log("Found upgrade arrow.")
            # click arrow
            logger.log("Clicking upgrade arrow")
            click(arrow_coords[1], arrow_coords[0])
            time.sleep(0.5)
            # click upgrade1
            logger.log("Clicking first upgrade button")
            upgrade_1_coords = look_for_upgrade_button()
            if upgrade_1_coords is not None:
                click(upgrade_1_coords[1], upgrade_1_coords[0])
            else:
                logger.log("Couldn't find upgrade1 button")
            time.sleep(0.5)
            # click upgrade2
            logger.log("Clicking second upgrade button")
            upgrade_2_coords = look_for_upgrade_button()
            if upgrade_2_coords is not None:
                click(upgrade_2_coords[1], upgrade_2_coords[0])
            else:
                logger.log("Couldn't find upgrade2 button")
            time.sleep(0.5)
            # click upgrade_confirm
            logger.log("Clicking upgrade confirm button")
            upgrade_confirm_coords = look_for_upgrade_confirm_button()
            if upgrade_confirm_coords is not None:
                click(upgrade_confirm_coords[1], upgrade_confirm_coords[0])
            else:
                logger.log("Couldn't find upgrade confirm button")
            time.sleep(0.5)
            # skip through
            logger.log("Skipping through screens.")
            click(x=349, y=250)
            time.sleep(0.2)
            click(x=20, y=540, clicks=5, interval=0.2)
            time.sleep(0.2)
            if check_if_on_level_up_screen(logger):
                click(208, 560)
                time.sleep(2)

        else:
            # if arrows not found
            logger.log("No upgrades found yet.")
        # scroll
        n = random.randint(3, 7)
        while n > 0:
            scroll_down_fast()
            time.sleep(0.1)
            n -= 1
        time.sleep(3)
    time.sleep(1)
    return_to_clash_main_menu()
    time.sleep(1)


# TODO Rename this here and in `upgrade_cards_from_main`
def _extracted_from_upgrade_cards_from_main_25(arg0, logger, arg2, arg3):
    if arg0 is not None:
        click(arg0[1], arg0[0])
    else:
        logger.log(arg2)
    time.sleep(0.5)
            # click upgrade2
    logger.log(arg3)


def upgrade_cards_from_main_2(logger):
    # get to card menu from main
    logger.log("Getting to card page")
    getto_card_page(logger)
    coord_list=[
        [84,281],
        [169, 281],
        [258, 281],
        [346, 281],
        [169, 403],
        [258, 403],
        [346, 403],
        [78, 403],
    ]

    for coord in coord_list:
        click(coord[0],coord[1])
        upgrade_given_card(logger)
    
    n = random.randint(1, 16)
    while n > 0:
        scroll_down_super_fast()
        n -= 1
        
    for coord in coord_list:
        click(coord[0],coord[1])
        upgrade_given_card(logger)
    
       
       


def upgrade_given_card(logger):
    upgrade_coords = look_for_upgrade_button()
    if upgrade_coords is not None:
        #click first upgrade coord
        click(upgrade_coords[1], upgrade_coords[0])
        time.sleep(2)
        
        #click second upgrade coord
        click(232,610)
        time.sleep(2)
    
    
        #click third upgrade coord
        click(240,531)
        time.sleep(2)

    
        # skip through
        logger.log("Skipping through screens.")
        click(x=349, y=250)
        click(x=20, y=540, clicks=5, interval=0.05)


def look_for_upgrade_button():
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
    ]
    locations = find_references(
        screenshot=screenshot(),
        folder="upgrade_button",
        names=references,
        tolerance=0.97
    )
    return get_first_location(locations)


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
    return get_first_location(locations)


def find_upgradable_cards():
    references = [
        "r0.png",
        "r1.png",
        "r2.png",
        "r3.png",
        "r4.png",
        "r5.png",
        "r6.png",
        "e0.png",
        "e1.png",
        "e2.png",
        "e3.png",
        "e4.png",
        "0.png",
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
    ]

    region = [0, 0, 500, 700]
    locations = find_references(
        screenshot=screenshot(region),
        folder="green_upgrade_button",
        names=references,
        tolerance=0.97
    )
    return next((location for location in locations if (location is not None) and (confirm_upgrade_arrow(location))), None)


def confirm_upgrade_arrow(location):
    print("confirm_upgrade_arrow recieved a coord to confirm")
    # get location of center of arrow
    x = location[1] + 5
    y = location[0] + 3
    print("Location: ", location)
    print("Recieved coords: ", x, ",", y)

    # get center pixel of arrow and check if green
    region = [x, y, 5, 5]
    ss = screenshot(region)
    ss_iar = numpy.array(ss)
    pix1 = ss_iar[1][1]
    print(pix1)
    sentinel = [145, 255, 90]
    return bool(pixel_is_equal(pix1, sentinel, 20))


def getto_card_page(logger):
    click(x=100, y=630)
    time.sleep(2)
    loops = 0
    while not check_for_elixer_icon():
        logger.log("Not elixer button. Moving pages")
        time.sleep(1)
        click(x=100, y=630)
        loops = loops + 1
        if loops > 10:
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

    return get_first_location(locations)


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
    return check_for_location(locations)
