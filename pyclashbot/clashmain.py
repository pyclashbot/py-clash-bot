import random
import time

import numpy
import pyautogui

from pyclashbot.client import click, screenshot, scroll_down
from pyclashbot.image_rec import (check_for_location, find_references,
                                  get_first_location, pixel_is_equal)


def wait_for_clash_main_menu(logger):
    logger.change_status("Waiting for clash main menu")
    waiting=not check_if_on_clash_main_menu()

    while waiting:
        #wait 1 sec
        time.sleep(1)
        
        #click dead space
        click(32, 364)

        #check if stuck on trophy progression page
        if check_if_stuck_on_trophy_progression_page():
            time.sleep(1)
            click(210,621)
            
        #check if still waiting
        waiting= not(check_if_on_clash_main_menu())
        
    logger.change_status("Done waiting for clash main menu")
        
def check_if_stuck_on_trophy_progression_page():
    iar=numpy.asarray(screenshot())
    color=[85,177,255]
    pix_list=[
        iar[620][225],
        iar[625][230],
        iar[630][238],
        iar[635][245],
    ]
    for pix in pix_list: 
        if not pixel_is_equal(pix,color,tol=45):return False
    return True




def handle_puzzleroyale_popup(logger):
    # Method to handle puzzleroyale popup
    if look_for_puzzleroyale_popup():
        logger.change_status("Handling puzzle royale popup")
        click(366, 121)
        time.sleep(3)


def look_for_puzzleroyale_popup():
    # Method to check for puzzleroyale popup
    iar = numpy.array(screenshot())

    pix_list = [
        iar[173][102],
        iar[290][96],
        iar[154][312],
    ]

    color = [244, 183, 118]

    return all((pixel_is_equal(pix, color, tol=45)) for pix in pix_list)


def check_for_gem_logo_on_main():
    # Method to check if the clash main menu is on screen
    iar = numpy.array(screenshot())

    pix_list=[
        iar[64][403],
        iar[67][406],
        iar[70][408],
    ]
    color=[75,180,35]
    
    #for pix in pix_list:print(pix)
    
    for pix in pix_list:
        if not pixel_is_equal(pix, color, tol=45):
            return False
        return True
    
    
def check_for_blue_background_on_main():
    # Method to check if the clash main menu is on screen
    iar = numpy.array(screenshot())

    pix_list=[
        iar[350][3],
        iar[360][6],
        iar[368][7],
        iar[372][9],
    ]
    color=[9,69,119]
    
    #for pix in pix_list:print(pix)
    
    for pix in pix_list:
        if not pixel_is_equal(pix, color, tol=45):
            return False
        return True

    
def check_if_on_clash_main_menu():
    if not check_for_gem_logo_on_main():
        #print("Gem logo not found")
        return False
    if not check_for_blue_background_on_main():
        #print("Blue background not found")
        return False
    
    return True


def get_to_account(logger, account_number):
    # Method to change account to the given account number using the supercell
    # ID login screen in the options menu in the clash main menu
    handle_gold_rush_event(logger)
    time.sleep(2)

    logger.change_status(
        f"Switching accounts to account number {str(account_number)}")

    #open settings
    click(x=364, y=99)

    #click switch accounts
    click(200,460)

    if account_number == 0:
        #logger.change_status("Clicking account 1")
        click(x=211, y=388)
    if account_number == 1:
        #logger.change_status("Clicking account 2")
        click(x=193, y=471)
    if account_number == 2:
        #logger.lchange_statusog("Clicking account 3")
        click(x=200, y=560)

    time.sleep(3)
    logger.add_account_switch()
    if wait_for_clash_main_menu(logger) == "restart":
        return "restart"

    # handling the various things notifications and such that need to be
    # cleared before bot can get going
    time.sleep(0.5)
    handle_gold_rush_event(logger)
    time.sleep(0.5)
    handle_new_challenge(logger)
    time.sleep(0.5)
    handle_special_offer(logger)
    time.sleep(0.5)
    handle_card_mastery_notification()
    time.sleep(0.5)


def check_for_gold_rush_event():
    # Method to see if a gold rush event is happening on the clash main menu

    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
    ]
    locations = find_references(
        screenshot=screenshot(),
        folder="gold_rush_event",
        names=references,
        tolerance=0.97
    )
    loc = get_first_location(locations)
    return loc is not None


def handle_gold_rush_event(logger):
    # Method to handle a gold rush event notification obstructing the bot

    logger.change_status(
        "Handling the possibility of a gold rush event notification obstructing the bot.")
    time.sleep(0.5)
    pyautogui.click(193, 465)
    time.sleep(0.5)
    pyautogui.click(193, 465)
    time.sleep(0.5)


def handle_new_challenge(logger):
    # Method to handle a new challenge notification obstructing the bot

    logger.change_status(
        "Handling the possibility of a new challenge notification obstructing the bot.")
    time.sleep(0.5)
    click(376, 639)
    time.sleep(0.5)
    click(196, 633)
    time.sleep(0.5)
    if check_if_on_trophy_progession_rewards_page():
        logger.change_status(
            "Handling the possibility of trophy progession rewards page obstructing the bot.")
        click(212, 633)
        time.sleep(0.5)


def handle_special_offer(logger):
    # Method to handle a special offer notification obstructing the bot

    logger.change_status(
        "Handling the possibility of special offer notification obstructing the bot.")
    time.sleep(0.5)
    click(35, 633)
    time.sleep(0.5)
    click(242, 633)
    time.sleep(0.5)
    if check_if_on_trophy_progession_rewards_page():
        click(212, 633)
        time.sleep(0.5)


def check_if_on_trophy_progession_rewards_page():
    # Method to check if the bot is on the trophy progression rewards page in
    # the given moment
    iar = numpy.array(screenshot())
    pix_list = [
        iar[629][240],
        iar[631][185],
        iar[621][232],
    ]
    color = [78, 175, 255]

    return all((pixel_is_equal(pix, color, tol=35)) for pix in pix_list)

# Method to handle the chest unlocking on the clash main menu


def open_chests(logger):
    # unlock coord (210, 455)
    # chest 1 coord (78, 554)
    # chest 2 coord (162,549)
    # chest 3 coord (263,541)
    # chest 4 coord (349 551)
    # dead space coord (20, 556)
    # check_if_unlock_chest_button_exists()
    logger.change_status("Opening chests")

    chest_coord_list = [[78, 554], [162, 549], [263, 541], [349, 551]]

    chest_index = 0
    for chest_coord in chest_coord_list:
        chest_index = chest_index + 1
        logger.change_status(f"Checking chest slot {str(chest_index)}")
        # click chest
        click(chest_coord[0], chest_coord[1])
        time.sleep(1)

        if check_if_unlock_chest_button_exists():
            #print("Found unlock in chest", chest_index)
            time.sleep(0.5)

            logger.change_status(str(f"Unlocking chest {str(chest_index)}"))
            logger.add_chest_unlocked()
            time.sleep(0.5)
            click(210, 465)

        else:
            #logger.change_status("Handling possibility of rewards screen")
            for _ in range(10):
                click(20, 556)
            time.sleep(3)

        # close chest menu
        click(20, 556)
        time.sleep(0.33)


def check_if_unlock_chest_button_exists():
    # Method for checking if the unlock chest button exists in the menu that
    # appears when clicking a chest
    current_image = screenshot()
    reference_folder = "unlock_chest_button"
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

    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.90
    )

    return any(location is not None for location in locations)


def start_2v2(logger):
    # Method to start a 2v2 quickmatch through the party mode through the
    # clash main menu
    logger.change_status("Initiating 2v2 match from main menu")

    #getting to party tab
    click(365,108)
    time.sleep(1)
    click(263,248)
    time.sleep(1)

    if find_and_click_2v2_quickmatch_button(logger) == "restart":
        return "restart"

    check_for_reward_limit()


def find_and_click_2v2_quickmatch_button(logger):
    # method to find and click the 2v2 quickmatch button in the party mode menu
    # starts in the party mode
    # ends when loading a match
    #logger.change_status("Finding and clicking 2v2 quickmatch button")
    # repeatedly scroll down until we find coords for the 2v2 quickmatch button
    coords = None
    loops = 0
    while coords is None:
        loops += 1
        if loops > 20:
            logger.change_status(
                "Could not find 2v2 quickmatch button, restarting")
            return "restart"
        scroll_down()
        time.sleep(1)
        coords = find_2v2_quick_match_button()
    time.sleep(2)
    # once we find the coords, click them
    click(coords[0], coords[1])
    logger.change_status("Done queueing a 2v2 quickmatch")


def check_for_reward_limit():
    # Method to check for the reward limit popup notification and close it

    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png"
    ]

    locations = find_references(
        screenshot=screenshot(),
        folder="reward_limit",
        names=references,
        tolerance=0.97
    )

    for location in locations:
        if location is not None:
            click(211, 432)

            return True
    return False


def find_2v2_quick_match_button():
    # method to find the 2v2 quickmatch button in the party mode menu

    current_image = screenshot()
    reference_folder = "2v2_quick_match"
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

    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97
    )

    coord = get_first_location(locations)
    return None if coord is None else [coord[1] + 200, coord[0] + 50]


def wait_for_battle_start(logger):
    # Method to wait for a the loading sequence of a battle to finish

    logger.change_status("Waiting for battle start. . .")
    in_battle = False
    loops = 0

    while not in_battle:
        if check_if_in_battle():
            in_battle = True
        click(100, 100)
        time.sleep(0.25)
        loops += 1
        logger.change_status(str(f"Waiting for battle start... {loops}"))
        if loops > 120:
            logger.change_status("Waited longer than 30 sec for a fight")
            return "restart"


def check_if_in_battle():
    # Method to check if the bot is in a battle in the given moment

    for _ in range(10):
        references = [
            "1.png",
            "2.png",
            "3.png",
            "4.png",
            "5.png"
        ]

        locations = find_references(
            screenshot=screenshot(),
            folder="check_if_in_battle",
            names=references,
            tolerance=0.97
        )

        if check_for_location(locations):
            return True
        time.sleep(1)
    return False


def handle_card_mastery_notification():

    # Method to handle the possibility of a card mastery notification
    # obstructing the bot
    click(107, 623)
    time.sleep(1)

    click(240, 630)
    time.sleep(1)
