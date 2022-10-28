import numpy
import random
import time
from os.path import dirname, join

from pyclashbot.client import (click, get_file_count,
                               make_reference_image_list, screenshot,
                               scroll_down_super_fast, scroll_up_fast)
from pyclashbot.image_rec import (check_for_location, find_references,
                                  get_first_location, pixel_is_equal)
from pyclashbot.upgrade import get_to_clash_main_from_card_page


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


def select_second_deck(logger):
    # Method to select the second deck of this account

    #logger.change_status("Selecting deck number 2 for use.")
    # get to card page
    get_to_card_page(logger)
    time.sleep(1)

    # click number 2
    click(173, 190)
    time.sleep(1)

    # get to main menu from card page
    get_to_clash_main_from_card_page(logger)


def randomize_and_select_deck_2(logger):
    # Method to randomize deck number 2 of this account

    logger.change_status("Randomizing deck number 2")
    # get to card page
    get_to_card_page(logger)

    # select deck 2
    click(173, 190)
    time.sleep(1)

    #randomize this deck
    randomize_current_deck()

    # return to clash main
    get_to_clash_main_from_card_page(logger)


def randomize_current_deck():
    #figure out how much you can scroll down in your card list
    max_scrolls=count_scrolls_in_card_page()
    
    
    card_coord_list=[
        [75,271],
        [162,277],
        [250,267],
        [337,267],
        [77,400],
        [174,398],
        [250,411],
        [325,404],
    ]

    for card_coord in card_coord_list:
        replace_card_in_deck(card_coord=card_coord, max_scrolls=max_scrolls)


def replace_card_in_deck(card_coord=[],max_scrolls=4):
    if card_coord==[]:return

    #scroll down a random amount
    scrolls=random.randint(2,max_scrolls)
    while (scrolls>0)and(check_if_can_still_scroll()):
        scroll_down_super_fast()
        scrolls-=1
    #scroll_up_super_fast()

    time.sleep(0.22)

    #get a random card from this screen to use
    use_card_button_coord=find_use_card_button()

    while use_card_button_coord is None:
        click(x=random.randint(81,356),y=random.randint(120,485))
        time.sleep(0.22)
        use_card_button_coord=find_use_card_button()

    click(use_card_button_coord[0],use_card_button_coord[1])

    #select the card coord in the deck that we're replacing with the random card
    click(card_coord[0],card_coord[1])
    time.sleep(0.22)


def find_use_card_button():
    current_image = screenshot()
    reference_folder = "find_use_card_button"


    references = make_reference_image_list(
        get_file_count(
            join(
                dirname(__file__),
                "reference_images",
                "find_use_card_button")))


    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.9
    )

    coord = get_first_location(locations)
    return None if coord is None else [coord[1] , coord[0]]


def check_if_can_still_scroll():
    iar=numpy.asarray(screenshot())
    pix_list_1=[
        iar[559][83],
        iar[559][170],
        iar[559][250],
        iar[559][340],
    ]
    

    pix_list_2=[
        iar[495][83],
        iar[495][172],
        iar[495][259],
        iar[495][342],
    ]
    

    #blue check truth indicates that we've reached the base of the card list
    color_blue=[14,68,118]    
    all_pix_list=pix_list_2+pix_list_1
    blue_check_truth=True
    for pix in all_pix_list:
        if not(pixel_is_equal(pix,color_blue,tol=45)): blue_check_truth=False
        
    #pix list 1 truth indicates whether or not this row of pixels are all greyscale
    pix_list_1_truth=True
    for pix in pix_list_1:
        if not(check_if_pixel_is_grey(pix)): pix_list_1_truth = False
        
    #pix list 2 truth indicates whether or not this row of pixels are all greyscale
    pix_list_2_truth=True
    for pix in pix_list_2:
        if not(check_if_pixel_is_grey(pix)): pix_list_2_truth = False
    
    if blue_check_truth:
        #print("Blue fail")
        return False
    
    if pix_list_1_truth or pix_list_2_truth: 
        #print("Grey fail")
        return False
    
    return True
    

def check_if_pixel_is_grey(pixel):
    r=pixel[0]
    g=pixel[1]
    b=pixel[2]

    return abs(r-g) <= 10 and abs(r-b) <= 10 and abs(g-b) <= 10


def count_scrolls_in_card_page():
    #Count scrolls
    count=0
    while check_if_can_still_scroll():
        scroll_down_super_fast()
        count+=1
    
    #get back to top of page
    click(240,621)
    click(111,629)
    time.sleep(1)
    
    if count<4: return count
    else: return count-1
    
