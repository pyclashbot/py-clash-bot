import random
import time
from os.path import dirname, join

import numpy

from pyclashbot.card_detection import make_reference_image_list
from pyclashbot.clashmain import check_for_gem_logo_on_main
from pyclashbot.client import (click, get_file_count, screenshot,
                               scroll_down_super_fast, scroll_up_fast,
                               scroll_up_super_fast)
from pyclashbot.image_rec import (check_for_location, find_references,
                                  get_first_location, pixel_is_equal)


def check_if_card_is_upgradable(card_coord=[],upgrade_coord=[]):
    #click card
    click(card_coord[0],card_coord[1])
    time.sleep(0.2)
    
    #check upgrade coord
    upgrade_color=[107,235,118]
    pixel=numpy.asarray(screenshot())[upgrade_coord[1]][upgrade_coord[0]]
    
    if pixel_is_equal(pixel,upgrade_color,tol=35):
        return True
    return False


def check_for_upgradable_cards():
    card_coord_list=[
        [94,277],
        [179,277],
        [255,277],
        [338,277],
        [94,406],
        [179,406],
        [255,406],
        [338,406],
    ]
    upgrade_coord_list=[
        [48,345],
        [132,345],
        [215,345],
        [367,343],
        [50,467],
        [198,467],
        [283,468],
        [365,465],
    ]
    card_upgrade_list=[]
    for card_index in range(8):
        card_coord=card_coord_list[card_index]
        upgrade_coord=upgrade_coord_list[card_index]
        if check_if_card_is_upgradable(card_coord=card_coord,upgrade_coord=upgrade_coord):
            card_upgrade_list.append("Upgrade")
        else:
            card_upgrade_list.append("No upgrade")
    return card_upgrade_list


def upgrade_card(logger,card_index):
    card_coord_list=[
        [81,337],
        [169,339],
        [253,338],
        [330,337],
        [81,464],
        [164,468],
        [248,466],
        [334,468],
    ]
    
    #Click the given card
    card_coord=card_coord_list[card_index]
    click(card_coord[0],card_coord[1])
    
    #Click the upgrade button below the card
    click(card_coord[0],card_coord[1])
    
    # Click upgrade for gold button
    click(238, 606)
    time.sleep(1)

    #Check for second upgrade for gold button
    if check_for_final_upgrade_button():
        logger.add_card_upgraded()
    
    # Click second upgrade for gold button
    click(234, 536)

    # Click close to 'not enough gold' notification
    click(346, 252)

    # Click dead space to close card page
    for _ in range(5):
        click(26, 518)
    
    
def check_for_final_upgrade_button():
    iar=numpy.asarray(screenshot())
    color=[56,228,72]
    pix_list=[
        iar[540][200],
        iar[547][204],
        iar[555][208],
        iar[560][212],
    ]
    for pix in pix_list:
        if not pixel_is_equal(pix,color,tol=45):
            return False
    return True


def upgrade_current_cards(logger):
    upgradable_cards_list=check_for_upgradable_cards()

    index=0
    for card in upgradable_cards_list:
        if card == "Upgrade":         
            upgrade_card(logger,index)
        index+=1
    
    
def get_to_clash_main_from_card_page(logger):
    # Method to get to the clash royale main menu screen from the card page

    logger.change_status("Getting to clash main from card page")
    click(250, 630)
    loops = 0

    on_clash_main = check_for_gem_logo_on_main()
    while not (on_clash_main):
        loops += 1
        if loops > 15:
            logger.change_status("Couldn't get to clash main from card page")
            return "restart"
        click(212, 623)
        time.sleep(1)
        on_clash_main = check_for_gem_logo_on_main()


def get_to_card_page(logger):
    # Method to get to the card page on clash main from the clash main menu

    click(x=100, y=630)
    time.sleep(2)
    loops = 0
    while not check_if_on_first_card_page():
        #logger.change_status("Not elixer button. Moving pages")
        time.sleep(1)
        click(x=100, y=630)
        loops = loops + 1
        if loops > 10:
            logger.change_status("Couldn't make it to card page")
            return "restart"
        time.sleep(0.2)
    scroll_up_fast()
    #logger.change_status("Made it to card page")
    time.sleep(1)


def check_if_on_first_card_page():
    # Method to check if the elixer icon of your deck's AVG elixer when on the
    # card page exists yet
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
        
    ]

    locations = find_references(
        screenshot=screenshot(),
        folder="card_page_elixer_icon",
        names=references,
        tolerance=0.97
    )

    return get_first_location(locations)


def find_card_page_logo():
    # Method to find the card page logo in the icon list in the bottom of the
    # screen when on clash main
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


