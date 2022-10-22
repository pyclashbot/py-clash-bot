import time
from random import Random

import numpy
import pyautogui

from pyclashbot.clashmain import check_if_on_clash_main_menu
from pyclashbot.client import click, screenshot, scroll_down
from pyclashbot.image_rec import (check_for_location, find_references, get_first_location,
                       pixel_is_equal)


#Method to request a random card if request is available
def request_random_card_from_clash_main(logger):
    logger.change_status("Checking if we can request a card.")
    if not(check_if_in_a_clan(logger)):
        logger.change_status("Skipping request because we are not in a clan.")
        return
    time.sleep(1)

    logger.change_status("Requesting a card.")
    #getting to clan page
    if get_to_clan_page(logger)=="restart":
        return "restart"
    time.sleep(1)

    #Check if can request
    if check_if_can_request():
        # clicking request button in bottom left
        click(x=86, y=564)

        # run request alg
        if request_random_card(logger)=="restart": return "restart"
        logger.add_request()

    else:
        logger.change_status("Can't request a card right now.")

    #return to main
    if get_to_clash_main_from_request_page(logger)== "restart": return "restart"

#method to request a random card
def request_random_card(logger):
    #starts on the request screen (the one with a bunch of pictures of the cards)
    #ends back on the clash main menu
    logger.change_status("Requesting a random card.")

    #scroll a little for randomness
    n=Random().randint(0,500)
    pyautogui.moveTo(203,552)
    time.sleep(0.33)
    pyautogui.dragTo(203,552-n,0.33)

    logger.change_status("Looking for card to request.")
    has_card_to_request=False
    loops=0
    while not(has_card_to_request):
        loops+=1
        if loops>25:
            logger.change_status("Could not find a card to request.")
            return "restart"
        #click random coord in region of card selection
        click(Random().randint(72,343),Random().randint(264,570))
        time.sleep(3)

        #check if request button appears
        request_button_coord=look_for_request_button()

        if request_button_coord is not None:
            has_card_to_request=True
            #logger.change_status("Found a satisfactory card to request.")
            click(request_button_coord[1],request_button_coord[0])

#Method to look for the request button in the list of clan interaction buttons on the clan page to see if we can request
def look_for_request_button():
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
        "ifhy_1.png",
        "ifhy_2.png",
        "ifhy_3.png",
        "ifhy_4.png",
        "ifhy_5.png",
        "ifhy_6.png",
        "ifhy_7.png",
        "ifhy_8.png",
        "iuyfgh_1.png",
        "iuyfgh_2.png",
        "iuyfgh_3.png",
        "iuyfgh_4.png",
        "iuyfgh_5.png",
        "iuyfgh_6.png",
        "iuyfgh_7.png",
        "iuyfgh_8.png",
        "royal_guards_1.png",
        "royal_guards_2.png",
        "royal_guards_3.png",
        "royal_guards_4.png",
        "royal_guards_5.png",
        "royal_guards_6.png",
        "royal_guards_7.png",
        "royal_guards_8.png",
        "telotet_1.png",
        "telotet_2.png",
        "telotet_3.png",
        "telotet_4.png",
        "telotet_5.png",
        "telotet_6.png",
        "telotet_7.png",
        "telotet_8.png",
        "22.png",
        "23.png",
        "24.png",
        "25.png",
        "26.png",
    ]
    locations = find_references(
        screenshot=screenshot(),
        folder="request_button",
        names=references,
        tolerance=0.97
    )
    return get_first_location(locations)

#Method to return to clash main menu from request page
def get_to_clash_main_from_request_page(logger):
    logger.change_status("Getting to clash main from request page")
    click(172,612)
    time.sleep(1)
    on_main=check_if_on_clash_main_menu()
    loops=0
    while not(on_main):
        loops+=1
        if loops>25:
            logger.change_status("Could not get to clash main from request page.")
            return "restart"
        click(208,606)
        time.sleep(1)
        on_main=check_if_on_clash_main_menu()

#method to get to clan chat page from clash main
def get_to_clan_page(logger):
    click(312,629)
    on_clan_chat_page=check_if_on_clan_page()
    logger.change_status("Getting to clan page.")
    loops=0
    while not(on_clan_chat_page):
        loops+=1
        if loops>25:
            logger.change_status("Could not get to clan page.")
            return "restart"
        click(278,631)
        time.sleep(1)
        scroll_down()
        time.sleep(1)

        on_clan_chat_page=check_if_on_clan_page()

#Method to check if we're on the clan chat page
def check_if_on_clan_page():
    iar=numpy.asarray(screenshot())

    pix_list=[
        iar[570][216],
        iar[575][149],
        iar[557][150],
        iar[575][215],
    ]
    color=[183 , 105 ,253]
    return all((pixel_is_equal(pix,color,tol=45)) for pix in pix_list)

#Method to check if request is available
def check_if_can_request():
    iar=numpy.asarray(screenshot())
    pix_list=[
        iar[536][50],
        iar[542][56],
        iar[535][57],
        iar[536][47],
    ]
    color=[47, 69,105]
    return all((pixel_is_equal(pix,color,tol=35)) for pix in pix_list)


#Method to check if the current account has a clan
def check_if_in_a_clan(logger):
    #starts and ends on clash main
    logger.change_status("Checking if in a clan.")

    #click clan tab
    click(308,627)
    time.sleep(1)

    #cycle through clan tab a few times
    for _ in range(3): click(280,623)
    time.sleep(1)
    scroll_down()
    time.sleep(1)

    #get a pixel from this clan tab
    pixel_1=numpy.asarray(screenshot())[118][206]
    #print("pixel 1 is ",pixel_1)

    #cycle tab again
    click(280,623)
    time.sleep(1)

    #get second pixel
    pixel_2=numpy.asarray(screenshot())[118][206]
    #print("pixel 2 is ",pixel_2)

    #get back to clash main
    get_to_clash_main_from_request_page(logger)



    #if pixels aren't equal return True (in a clan because there are two available pages instead of one)
    if not(pixel_is_equal(pixel_1,pixel_2,tol=25)):
        logger.change_status("You're in a clan")
        time.sleep(1)
        return True
    logger.change_status("Not in a clan.")
    time.sleep(1)
    return False







