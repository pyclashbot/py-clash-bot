import random
from tabnanny import check
import time
from unittest.mock import NonCallableMagicMock

import keyboard
import matplotlib.pyplot as plt
import numpy as np
import pyautogui
import pygetwindow as gw

from pyclashbot.card import fight_with_deck_list, find_all_cards
from pyclashbot.image_rec import (find_reference, find_references,
                                  pixel_is_equal)
from pyclashbot.logger import Logger

logger = Logger()

try:
    window_memu = gw.getWindowsWithTitle('MEmu')[0]
    window_mimm = gw.getWindowsWithTitle('Multiple Instance Manager')[0]
except (IndexError, KeyError):
    logger.log("MEmu or Multiple Instance Manager not detected!")

                 
def refresh_screen():
    check_quit_key_press()
    orientate_window()
    screenshot = pyautogui.screenshot()
    check_quit_key_press()
    iar = np.array(screenshot)
    return iar


def show_image(iar):
    plt.imshow(iar)
    check_quit_key_press()
    plt.show()


def orientate_window():
    #logger.log("Orientating memu client")
    window_memu = gw.getWindowsWithTitle('MEmu')[0]
    check_quit_key_press()
    window_memu.minimize()
    window_memu.restore()
    time.sleep(1)
    window_memu.moveTo(0, 0)
    time.sleep(1)
    window_memu.resizeTo(460, 680)


def orientate_memu_multi():
    check_quit_key_press()
    window_mimm.minimize()
    window_mimm.restore()
    window_mimm.moveTo(200, 200)
    time.sleep(1)
    window_mimm.moveTo(0, 0)


def open_clash():
    orientate_window()
    time.sleep(1)
    check_quit_key_press()
    logger.log("opening clash")

    coords = find_reference(
        screenshot=refresh_screen(),
        folder="logo",
        name="clash_logo.png",
        tolerance=0.97
    )

    if coords is None:
        logger.log("Clash logo wasn't found")
        return "quit"
    pyautogui.click(x=coords[1], y=coords[0])
    # return coords

    if wait_for_clash_main_menu() == "quit":
        return "quit"


def check_if_on_memu_main():
    iar = refresh_screen()
    check_quit_key_press()

    pix2 = iar[71][142]
    pix3 = iar[77][275]

    sentinel = [1] * 3
    sentinel[0] = 5
    sentinel[1] = 18
    sentinel[2] = 35
    check_quit_key_press()
    if not pixel_is_equal(pix2, sentinel, 10):
        return False
    if not pixel_is_equal(pix3, sentinel, 10):
        return False
    return True


def check_if_unlock_chest_button_exists():
    current_image = pyautogui.screenshot()
    reference_folder = "unlock_chest_button"
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
        "6.png"
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97
    )

    for location in locations:
        if location is not None:
            # found a location
            pyautogui.click(x=210, y=455)
            return True
    return False


def open_chests():

    logger.log("clicking chest1")
    pyautogui.click(x=78, y=554)
    time.sleep(1)
    check_quit_key_press()
    check_if_unlock_chest_button_exists()
    time.sleep(0.2)
    check_quit_key_press()
    pyautogui.click(x=20, y=556, clicks=20, interval=0.1, button='left')
    logger.log("clicking chest2")
    pyautogui.click(x=162, y=549)
    time.sleep(1)
    check_quit_key_press()
    check_if_unlock_chest_button_exists()
    time.sleep(0.2)
    check_quit_key_press()
    pyautogui.click(x=20, y=556, clicks=20, interval=0.2, button='left')
    logger.log("clicking chest3")
    pyautogui.click(x=263, y=541)
    time.sleep(1)
    check_quit_key_press()
    check_if_unlock_chest_button_exists()
    time.sleep(0.2)
    check_quit_key_press()
    pyautogui.click(x=20, y=556, clicks=20, interval=0.1, button='left')
    logger.log("clicking chest4")
    pyautogui.click(x=349, y=551)
    time.sleep(1)
    check_quit_key_press()
    check_if_unlock_chest_button_exists()
    time.sleep(0.2)
    check_quit_key_press()
    pyautogui.click(x=20, y=556, clicks=20, interval=0.1, button='left')


def check_if_on_clash_main_menu():
    current_image = pyautogui.screenshot()
    reference_folder = "clash_main_menu"
    references = [
        "clash_main_1.png",
        "clash_main_2.png",
        "clash_main_3.png",
        "clash_main_4.png",
        "clash_main_5.png"
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.99
    )

    for location in locations:
        if location is not None:
            return True  # found a location
    return False


def check_if_can_request():
    iar = refresh_screen()
    pix1 = iar[612][326]
    pix2 = iar[606][334]
    pix3 = iar[608][326]
    sentinel = [1] * 3
    sentinel[0] = 49
    sentinel[1] = 186
    sentinel[2] = 71
    check_quit_key_press()

    if not pixel_is_equal(pix1, sentinel, 10):
        return False
    if not pixel_is_equal(pix2, sentinel, 10):
        return False
    if not pixel_is_equal(pix3, sentinel, 10):
        return False
    check_quit_key_press()
    return True




def look_for_request_button():
    references = [
        "req_logo_1.png",
        "req_logo_2.png",
        "req_logo_3.png",
        "req_logo_4.png",
        "req_logo_5.png"
    ]

    locations = find_references(
        screenshot=refresh_screen(),
        folder="request_page_card_logos",
        names=references,
        tolerance=0.99
    )

    for location in locations:
        if location is not None:
            return location
    return None


def check_if_on_clan_chat_page():
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
    ]

    locations = find_references(
        screenshot=refresh_screen(),
        folder="check_if_on_clan_chat_page",
        names=references,
        tolerance=0.97
    )

    for location in locations:
        if location is not None:
            return True
    return False


def return_to_clash_main_menu():
    check_quit_key_press()
    logger.log("Returning to clash main menu")
    pyautogui.click(x=180, y=625)
    time.sleep(1)
    check_quit_key_press()


def start_2v2():              
    logger.log("Initiating 2v2 match from main menu")
    logger.log("Clicking party mode")
    party_button_coords = find_party_button()
    if party_button_coords is None:
        return "quit"
    pyautogui.click(x=party_button_coords[1],y=party_button_coords[0])
    logger.log("Scrolling until 2v2 button is found")
    while find_2v2_quick_match_button() is None:
        scroll_down()
        time.sleep(1)
    logger.log("Clicking 2v2 quickmatch button")
    quick_match_button_coords = find_2v2_quick_match_button()
    if quick_match_button_coords is None:
        return "quit"
    pyautogui.click(x=quick_match_button_coords[1],y=quick_match_button_coords[0])
    time.sleep(0.25)
    check_for_reward_limit()


def find_2v2_quick_match_button():
    current_image = pyautogui.screenshot()
    reference_folder = "2v2_quick_match"
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97
    )
    time.sleep(1)
    for location in locations:
        if location is not None:
            return location  # found a location
    return None


def find_party_button():
    current_image = pyautogui.screenshot()
    reference_folder = "party_button"
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97
    )
    time.sleep(1)
    for location in locations:
        if location is not None:
            return location  # found a location
    return None


def start_1v1_ranked():
    check_quit_key_press()
    logger.log("Navigating to 1v1 ranked match")
    pyautogui.click(x=140, y=440)
    wait_for_battle_start()
    check_quit_key_press()


def wait_for_battle_start():
    logger.log("Waiting for battle start")
    n = 1
    n1 = 0
    check_quit_key_press()
    while n == 1:
        if check_if_in_battle():
            n = 0
        pyautogui.click(x=100, y=100)
        time.sleep(0.25)
        n1 += 1
        if n1 > 120:
            logger.log("Waited longer than 30 sec for a fight")
            return "quit"
        refresh_screen()
        check_quit_key_press()


def fight_in_2v2():
    check_quit_key_press()
    card_coord = random_card_coord_picker()
    placement_coord = look_for_enemy_troops()
    if placement_coord is None:
        print("picking random coord")
        placement_coord = random_placement_coord_maker()
    else:
        print("picking coord: ", placement_coord)
        placement_coord[1] = placement_coord[1] + 30
    # pick card
    pyautogui.click(x=card_coord[0], y=card_coord[1],
                    clicks=1, interval=0, button='left')
    # place card
    pyautogui.click(
        x=placement_coord[0], y=placement_coord[1], clicks=1, interval=0, button='left')


def random_placement_coord_maker():
    check_quit_key_press()
    n = random.randint(1, 6)
    coords = [1] * 2
    if n == 0:
        coords[0] = 55
        coords[1] = 333
    if n == 1:
        coords[0] = 55
        coords[1] = 333
    if n == 2:
        coords[0] = 73
        coords[1] = 439
    if n == 3:
        coords[0] = 177
        coords[1] = 502
    if n == 4:
        coords[0] = 240
        coords[1] = 515
    if n == 5:
        coords[0] = 346
        coords[1] = 429
    if n == 6:
        coords[0] = 364
        coords[1] = 343
    check_quit_key_press()
    return coords


def random_card_coord_picker():
    check_quit_key_press()
    n = random.randint(1, 4)
    coords = [1] * 2
    if n == 1:
        # logger.log("randomly selected card 1")
        coords[0] = 146
        coords[1] = 588
    if n == 2:
        # logger.log("randomly selected card 2")
        coords[0] = 206
        coords[1] = 590
    if n == 3:
        # logger.log("randomly selected card 3")
        coords[0] = 278
        coords[1] = 590
    if n == 4:
        # logger.log("randomly selected card 4")
        coords[0] = 343
        coords[1] = 588
    check_quit_key_press()

    return coords



def leave_end_battle_window():
    check_quit_key_press()
    logger.log("battle is over. return to clash main menu")
    pyautogui.click(x=81, y=630)
    pyautogui.click(x=211, y=580)
    wait_for_clash_main_menu()
    check_quit_key_press()


def refresh_clan_tab():
    check_quit_key_press()
    pyautogui.click(x=300, y=630)
    return_to_clash_main_menu()
    time.sleep(3)
    check_quit_key_press()


def check_if_exit_battle_button_exists():
    current_image = pyautogui.screenshot()
    reference_folder = "exit_battle"
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
        "6.png"
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.99
    )

    for location in locations:
        if location is not None:
            return True  # found a location
    return False


def check_if_in_a_clan_from_main():
    logger.log("Checking if you're in a clan")
    pyautogui.click(x=315, y=630, clicks=3, interval=1)
    time.sleep(2)
    current_image = pyautogui.screenshot()
    reference_folder = "not_in_a_clan"
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
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97
    )
    pyautogui.click(x=175, y=630)
    time.sleep(1)
    for location in locations:
        if location is not None:
            logger.log("seems you're not in a clan")
            time.sleep(1)
            return_to_clash_main_menu()
            time.sleep(1)
            return False  # found a location
    logger.log("seems you're in a clan")
    time.sleep(1)
    time.sleep(1)
    return True


def scroll_down():
    pyautogui.moveTo(x=215,y=350)
    pyautogui.dragTo(x=215,y=300, button='left',duration=1)
   
    
def scroll_up():
    pyautogui.moveTo(x=215,y=300)
    pyautogui.dragTo(x=215,y=350, button='left',duration=1)


def find_donates():
    references = [
        "donate_button_1.png",
        "donate_button_2.png",
        "donate_button_3.png",
        "donate_button_4.png",
        "donate_button_5.png",
        "donate_button_6.png",
        "7.png",
        "8.png",
        "9.png",
        "10.png",
        "11.png",
        "12.png",
        "13.png",
        "14.png",
        "15.png",
        "18.png",
        "19.png",
        "20.png", 
    ]

    loops = 0
    while loops<3:
        locations = find_references(
            screenshot=refresh_screen(),
            folder="donate",
            names=references,
            tolerance=0.99
        )
        for location in locations:
            if location is not None:
                return location
        scroll_down()
        loops=loops+1
    return None


def click_donates():

    #find+click donate
    donate_button_loc = find_donates()
    if donate_button_loc is not None:
        logger.log("Found a donate coord. Clicking it")
        pyautogui.click(
            x=donate_button_loc[1], y=donate_button_loc[0], clicks=3, interval=0.25)
        time.sleep(1)
    #find + click more donates button
    more_donates_button_loc = check_if_more_donates()
    if more_donates_button_loc is not None:
        logger.log("Detected off-screen donates. Clicking it")
        pyautogui.click(
            x=more_donates_button_loc[1], y=more_donates_button_loc[0])
        time.sleep(1)
    #find+click donate
    donate_button_loc = find_donates()
    if donate_button_loc is not None:
        logger.log("Found a donate coord. Clicking it")
        pyautogui.click(
            x=donate_button_loc[1], y=donate_button_loc[0], clicks=3, interval=0.25)
        time.sleep(1)
    #find + click more donates button
    more_donates_button_loc = check_if_more_donates()
    if more_donates_button_loc is not None:
        logger.log("Detected off-screen donates. Clicking it")
        pyautogui.click(
            x=more_donates_button_loc[1], y=more_donates_button_loc[0])
        time.sleep(1)
    #find+click donate
    donate_button_loc = find_donates()
    if donate_button_loc is not None:
        logger.log("Found a donate coord. Clicking it")
        pyautogui.click(
            x=donate_button_loc[1], y=donate_button_loc[0], clicks=3, interval=0.25)
        time.sleep(1)   
    #find+click 'scroll to bottom arrow button'
    down_arrow_loc = check_if_clan_chat_down_arrow_exists()
    if down_arrow_loc is not None:
        logger.log("Found 'page to bottom' arrow. Clicking it")
        pyautogui.click(x=down_arrow_loc[1], y=down_arrow_loc[0])
    
    
    time.sleep(0.2)
    return_to_clash_main_menu()


def check_if_clan_chat_down_arrow_exists():
    current_image = pyautogui.screenshot()
    reference_folder = "check_if_clan_chat_down_arrow_exists"
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97
    )
    time.sleep(1)
    for location in locations:
        if location is not None:
            return location  # found a location
    return None


def getto_donate_page():
    check_quit_key_press()
    logger.log("Moving to clan chat page")
    pyautogui.click(x=317, y=627)
    time.sleep(1)
    loops =0
    while (not check_if_on_clan_chat_page()) and (loops<20):
        time.sleep(1)
        pyautogui.click(x=317, y=627)
        time.sleep(1)
        pyautogui.click(x=393, y=580)
        time.sleep(1)
        loops=loops+1
        check_quit_key_press()
    if check_if_on_clan_chat_page():
        return
    else:
        return "quit"
    


def check_if_more_donates():
    current_image = pyautogui.screenshot()
    reference_folder = "more_donates_button"
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png",
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97
    )
    time.sleep(1)
    for location in locations:
        if location is not None:
            return location  # found a location
    return None


def check_quit_key_press():
    if keyboard.is_pressed("space"):
        logger.log("space is pressed. Quitting the program")
        quit()


def restart_client():
    check_quit_key_press()
    logger.log("closing client")
    time.sleep(1)
    pyautogui.click(x=540, y=140)
    time.sleep(1)
    check_quit_key_press()
    logger.log("opening client")
    pyautogui.click(x=540, y=140)
    time.sleep(3)
    if wait_for_memu_main() == "quit":
        return "quit"
    logger.log("skipping ads")
    orientate_window()
    time.sleep(1)
    pyautogui.click(x=440, y=600, clicks=5, interval=1)
    if open_clash() == "quit":
        return "quit"


def wait_for_clash_main_menu():
    n = 0
    while not check_if_on_clash_main_menu():

        check_quit_key_press()
        time.sleep(3)
        logger.log(f"Waiting for clash main menu/{n}")
        n = n+1
        if n > 20:
            logger.log("Waiting longer than a minute for clash main menu")
            return "quit"
        pyautogui.moveTo(x=50, y=190, duration=0.25)
        pyautogui.moveTo(x=10, y=170, duration=0.25)
        pyautogui.click()


def check_if_past_game_is_win():
    check_quit_key_press()
    open_activity_log()
    iar = refresh_screen()

    n = 40
    while n < 130:
        pix = iar[191][n]
        sentinel = [1] * 3
        sentinel[0] = 102
        sentinel[1] = 204
        sentinel[2] = 255
        if pixel_is_equal(pix, sentinel, 10):
            pyautogui.click(x=20, y=507)
            return True
        n = n+1
    time.sleep(1)
    pyautogui.click(x=385, y=507)
    pyautogui.click(x=20, y=507)
    return False


def open_activity_log():
    check_quit_key_press()
    pyautogui.click(x=360, y=99)
    time.sleep(1)
    check_quit_key_press()
    pyautogui.click(x=255, y=75)
    time.sleep(1)
    check_quit_key_press()


def check_if_windows_exist():
    if gw.getWindowsWithTitle('MEmu') == []:
        logger.log("MEmu window not found")
        return False
    if gw.getWindowsWithTitle('Multiple Instance Manager') == []:
        logger.log("MMIM window not found")
        return False
    return True


def look_for_enemy_troops():
    current_image = pyautogui.screenshot(region=(78,141, 271, 356))

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
        "32.png",
        "33.png",
        "34.png",
        "14_10.png",
        "1_1.png",
        "1_2.png",
        "1_3.png",
        "1_4.png",
        "2_1.png",
        "2_3.png",
        "2_2.png",
        "3_1.png",
        "3_2.png",
        "3_3.png",
        "3_4.png",
        "3_5.png",
        "5_1.png",
        "5_2.png",
        "5_3.png",
        "5_4.png",
        "6_1.png",
        "6_2.png",
        "6_3.png",
        "6_4.png",
        "7_1.png",
        "7_2.png",
        "7_3.png",
        "7_4.png",
        "7_5.png",
        "8_1.png",
        "8_2.png",
        "8_3.png",
        "8_4.png",
        "9_1.png",
        "9_2.png",
        "9_3.png",
        "9_4.png",
        "10_1.png",
        "10_2.png",
        "10_3.png",
        "10_4.png",
        "11_1.png",
        "11_2.png",
        "11_3.png",
        "11_4.png",
        "11_5.png",
        "12_1.png",
        "12_2.png",
        "12_3.png",
        "12_4.png",
        "12_5.png",
        "12_6.png",
        "13_2.png",
        "13_3.png",
        "14_2.png",
        "14_3.png",
        "14_4.png",
        "14_5.png",
        "14_6.png",
        "14_7.png",
        "14_8.png",
        "14_9.png",
    ]

    locations = find_references(
        screenshot=current_image,
        folder="ENEMY_TROOP_IMAGES",
        names=references,
        tolerance=0.97
    )

    for location in locations:
        if location is not None:
            return [location[1], location[0]]
    return None


def check_deck():
    # get to deck tab
    pyautogui.moveTo(x=115, y=634, duration=0.2)
    pyautogui.click()
    time.sleep(2)
    pyautogui.moveTo(x=90, y=110, duration=0.2)
    pyautogui.click()
    time.sleep(2)
    # screenshot deck region
    #deck_image = pyautogui.screenshot()
    deck_image = pyautogui.screenshot(region=(24, 203, 407, 324))

    # check for all cards
    current_deck = ["empty"]*8
    current_deck = find_all_cards(deck_image, current_deck)

    time.sleep(2)
    pyautogui.moveTo(x=245, y=640, duration=1)
    pyautogui.click()
    time.sleep(2)
    return current_deck


def wait_for_memu_main():
    loops = 0
    while check_if_on_memu_main() is False:
        loops = loops+1
        log = "Waiting for memu main:"+str(loops)
        logger.log(log)
        time.sleep(1)
        if loops > 20:
            logger.log("Waited too long for memu start")
            return "quit"


def check_if_in_battle():
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png"
    ]

    locations = find_references(
        screenshot=pyautogui.screenshot(),
        folder="check_if_in_battle",
        names=references,
        tolerance=0.97
    )

    for location in locations:
        if location is not None:
            return True
    return False


def switch_accounts_to(ssid):
    check_quit_key_press()

    logger.log("Opening settings")
    pyautogui.click(x=364,y=99)
    time.sleep(3)
    check_quit_key_press()
    logger.log("Clicking switch button")
    pyautogui.click(x=198,y=401)
    time.sleep(3)
    check_quit_key_press()
    if ssid==1:
        logger.log("Clicking account 1")
        pyautogui.click(x=211,y=388)
    if ssid==2:
        logger.log("Clicking account 2")
        pyautogui.click(x=193,y=471)
    time.sleep(3)
    if wait_for_clash_main_menu() == "quit":
        return "quit"
    check_quit_key_press()


def check_for_reward_limit():
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
        "5.png"
    ]

    locations = find_references(
        screenshot=pyautogui.screenshot(),
        folder="reward_limit",
        names=references,
        tolerance=0.97
    )

    for location in locations:
        if location is not None:
            pyautogui.click(x=211,y=432)
            return True
    return False


def check_state():
    time.sleep(3)
    if check_if_on_clash_main_menu():
        logger.log("On clash main")
        return "clash_main"
    if check_if_in_battle():
        logger.log("In a fight")
        return "fighting"
    return None

# region donate_cards
def look_for_donates_by_card():
    #region earthquake
    earthquake = look_for_earthquake()
    if earthquake is not None:
        logger.log("Found a request for earthquake.")
        logger.log(earthquake)
        pyautogui.click(x=earthquake[1],y=earthquake[0])
    # endregion
    #region ice_spirit
    ice_spirit = look_for_ice_spirit()
    if ice_spirit is not None:
        logger.log("Found a request for ice_spirit.")
        logger.log(ice_spirit)
        pyautogui.click(x=ice_spirit[1],y=ice_spirit[0])
    # endregion
    #region skeleton_barrel
    skeleton_barrel = look_for_skeleton_barrel()
    if skeleton_barrel is not None:
        logger.log("Found a request for skeleton_barrel.")
        logger.log(skeleton_barrel)
        pyautogui.click(x=skeleton_barrel[1],y=skeleton_barrel[0])
    # endregion
    #region zappies
    zappies = look_for_zappies()
    if zappies is not None:
        logger.log("Found a request for zappies.")
        logger.log(zappies)
        pyautogui.click(x=zappies[1],y=zappies[0])
    # endregion
    #region skeletons
    skeletons = look_for_skeletons()
    if skeletons is not None:
        logger.log("Found a request for skeletons.")
        logger.log(skeletons)
        pyautogui.click(x=skeletons[1],y=skeletons[0])
    # endregion
    #region mini_pekka
    mini_pekka = look_for_skeletons()
    if mini_pekka is not None:
        logger.log("Found a request for mini_pekka.")
        logger.log(mini_pekka)
        pyautogui.click(x=mini_pekka[1],y=mini_pekka[0])
    # endregion
    #region inferno_tower
    inferno_tower = look_for_inferno_tower()
    if inferno_tower is not None:
        logger.log("Found a request for infero_tower.")
        logger.log(inferno_tower)
        pyautogui.click(x=inferno_tower[1],y=inferno_tower[0])
    # endregion
    #region goblins
    goblins = look_for_goblins()
    if goblins is not None:
        logger.log("Found a request for goblins.")
        logger.log(goblins)
        pyautogui.click(x=goblins[1],y=goblins[0])
    # endregion
    #region bomber
    coords = look_for_bomber()
    if coords is not None:
        logger.log("Found a request for bomber.")
        logger.log(coords)
        pyautogui.click(x=coords[1],y=coords[0])
    # endregion
    #region goblin_gang
    coords = look_for_goblin_gang()
    if coords is not None:
        logger.log("Found a request for goblin_gang.")
        logger.log(coords)
        pyautogui.click(x=coords[1],y=coords[0])
    # endregion



def look_for_earthquake():
    references = [
        "earthquake.png",
    ]
    locations = find_references(
        screenshot=pyautogui.screenshot(region=(0,0, 700, 700)),
        folder="donate_card_images",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None
def look_for_ice_spirit():
    references = [
        "ice_spirit.png",
        "ice_spirit_1.png",
        "ice_spirit_2.png",
    ]
    locations = find_references(
        screenshot=pyautogui.screenshot(region=(0,0, 700, 700)),
        folder="donate_card_images",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None
def look_for_skeleton_barrel():
    references = [
        "skeleton_barrel.png",
        "skeleton_barrel_1.png",
        "skeleton_barrel_2.png",
    ]
    locations = find_references(
        screenshot=pyautogui.screenshot(region=(0,0, 700, 700)),
        folder="donate_card_images",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None
def look_for_zappies():
    references = [
        "zappies.png",
    ]
    locations = find_references(
        screenshot=pyautogui.screenshot(region=(0,0, 700, 700)),
        folder="donate_card_images",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None
def look_for_skeletons():
    references = [
        "skeletons.png",
    ]
    locations = find_references(
        screenshot=pyautogui.screenshot(region=(0,0, 700, 700)),
        folder="donate_card_images",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None
def look_for_mini_pekka():
    references = [
        "mini_pekka.png",
    ]
    locations = find_references(
        screenshot=pyautogui.screenshot(region=(0,0, 700, 700)),
        folder="donate_card_images",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None
def look_for_inferno_tower():
    references = [
        "inferno_tower.png",
    ]
    locations = find_references(
        screenshot=pyautogui.screenshot(region=(0,0, 700, 700)),
        folder="donate_card_images",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None
def look_for_goblins():
    references = [
        "goblins.png",
    ]
    locations = find_references(
        screenshot=pyautogui.screenshot(region=(0,0, 700, 700)),
        folder="donate_card_images",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None
def look_for_bomber():
    references = [
        "bomber.png",
    ]
    locations = find_references(
        screenshot=pyautogui.screenshot(region=(0,0, 700, 700)),
        folder="donate_card_images",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None
def look_for_goblin_gang():
    references = [
        "goblin_gang.png",
    ]
    locations = find_references(
        screenshot=pyautogui.screenshot(region=(0,0, 700, 700)),
        folder="donate_card_images",
        names=references,
        tolerance=0.97
    )
    for location in locations:
        if location is not None:
            return location
    return None

   
# endregion  
    
# region request_cards

def request_from_clash_main_menu(card_to_request):
    check_quit_key_press()
    logger.log("Moving to clan chat page")
    pyautogui.click(x=317, y=627)
    time.sleep(1)
    while not check_if_on_clan_chat_page():
        pyautogui.click(x=317, y=627)
        time.sleep(2)
    log = "requesting: "+str(card_to_request)
    logger.log(log)
    pyautogui.click(x=86, y=564)
    # scroll till find card +click card
    coords = scroll_to_request_card(card_to_request)
    if coords=="quit":
        return "quit"
    if coords is not None:
        pyautogui.click(x=coords[1], y=coords[0])
        time.sleep(2)
    # click request
    coords = look_for_request_button()
    if coords is not None:
        pyautogui.click(x=coords[1], y=coords[0])
        time.sleep(2)
    return_to_clash_main_menu()


def scroll_to_request_card(card_to_request):
    if card_to_request=="archers":
        return scroll_till_find_archers()
    if card_to_request=="arrows":
        return scroll_till_find_arrows()
    if card_to_request=="barb_hut":
        return scroll_till_find_barb_hut()
    if card_to_request=="barbs":
        return scroll_till_find_barbs()
    if card_to_request=="bats":
        return scroll_till_find_bats()
    if card_to_request=="bomb_tower":
        return scroll_till_find_bomb_tower()
    if card_to_request=="bomber":
        return scroll_till_find_bomber()
    if card_to_request=="cannon":
        return scroll_till_find_cannon()
    if card_to_request=="dart_goblin":
        return scroll_till_find_dart_goblin()
    if card_to_request=="e_spirit":
        return scroll_till_find_e_spirit()
    if card_to_request=="earthquake":
        return scroll_till_find_earthquake()
    if card_to_request=="elite_barbs":
        return scroll_till_find_elite_barbs()
    if card_to_request=="elixer_golem":
        return scroll_till_find_elixer_golem()
    if card_to_request=="elixer_pump":
        return scroll_till_find_elixer_pump()
    if card_to_request=="flying_machine":
        return scroll_till_find_flying_machine()
    if card_to_request=="furnace":
        return scroll_till_find_furnace()
    if card_to_request=="giant":
        return scroll_till_find_giant()
    if card_to_request=="goblin_cage":
        return scroll_till_find_goblin_cage()
    if card_to_request=="goblin_hut":
        return scroll_till_find_goblin_hut()
    if card_to_request=="goblins":
        return scroll_till_find_goblins()
    if card_to_request=="heal_spirit":
        return scroll_till_find_heal_spirit()
    if card_to_request=="healer":
        return scroll_till_find_healer()
    if card_to_request=="ice_golem":
        return scroll_till_find_ice_golem()
    if card_to_request=="ice_spirit":
        return scroll_till_find_ice_spirit()
    if card_to_request=="knight":
        return scroll_till_find_knight()
    if card_to_request=="mega_minion":
        return scroll_till_find_mega_minion()
    if card_to_request=="minion_hoard":
        return scroll_till_find_minion_hoard()
    if card_to_request=="minions":
        return scroll_till_find_minions()
    if card_to_request=="mortar":
        return scroll_till_find_mortar()
    if card_to_request=="musketeer":
        return scroll_till_find_musketeer()
    if card_to_request=="rascals":
        return scroll_till_find_rascals()
    if card_to_request=="rocket":
        return scroll_till_find_rocket()
    if card_to_request=="royal_delivery":
        return scroll_till_find_royal_delivery()
    if card_to_request=="royal_giant":
        return scroll_till_find_royal_giant()
    if card_to_request=="royal_hogs":
        return scroll_till_find_royal_hogs()
    if card_to_request=="skeleton_barrel":
        return scroll_till_find_skeleton_barrel()
    if card_to_request=="skeleton_dragons":
        return scroll_till_find_skeleton_dragons()
    if card_to_request=="skeletons":
        return scroll_till_find_skeletons()
    if card_to_request=="snowball":
        return scroll_till_find_snowball()
    if card_to_request=="spear_goblins":
        return scroll_till_find_spear_goblins()
    if card_to_request=="tombstone":
        return scroll_till_find_tombstone()
    if card_to_request=="wizard":
        return scroll_till_find_wizard()
    if card_to_request=="zappies":
        return scroll_till_find_zappies()
    if card_to_request=="fire_spirit":
        return scroll_till_find_fire_spirit()
    if card_to_request=="fireball":
        return scroll_till_find_fireball()
    if card_to_request=="valk":
        return scroll_till_find_valk()
    if card_to_request=="goblin_gang":
        return scroll_till_find_goblin_gang()
    if card_to_request=="zap":
        return scroll_till_find_zap()
    if card_to_request=="inferno_tower":
        return scroll_till_find_inferno_tower()
    
#archers
def scroll_till_find_archers():
    loops=0
    n = None
    while (n is None):
        references = [
            "archers.png",
        ]
        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )
        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#giant
def scroll_till_find_giant():
    loops=0
    n = None
    while (n is None):
        references = [
            "giant_1.png",
            "giant_2.png",
            "giant_3.png",
            "giant_4.png",
            "giant_5.png",
            "giant_6.png",
            "giant_7.png",
            "giant_8.png",
        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#archers
def scroll_till_find_giant():
    loops=0
    n = None
    while (n is None):
        references = [
            "giant_1.png",
            "giant_2.png",
            "giant_3.png",
            "giant_4.png",
            "giant_5.png",
            "giant_6.png",
            "giant_7.png",
            "giant_8.png",
        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#arrows
def scroll_till_find_arrows():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "arrows.png",
        ]
        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )
        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#barb_hut
def scroll_till_find_barb_hut():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "barb_hut.png",
        ]
        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )
        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#barbs
def scroll_till_find_barbs():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "barbs.png",
        ]
        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )
        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#bats
def scroll_till_find_bats():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "bats.png",
        ]
        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )
        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#bomb_tower
def scroll_till_find_bomb_tower():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "bomb_tower.png",
        ]
        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#bomber
def scroll_till_find_bomber():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "bomber.png",
 
        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#cannon
def scroll_till_find_cannon():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "cannon.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#dart_goblin
def scroll_till_find_dart_goblin():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "dart_goblin.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#e_spirit
def scroll_till_find_e_spirit():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "e_spirit.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#earthquake
def scroll_till_find_earthquake():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "earthquake.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#elite_barbs
def scroll_till_find_elite_barbs():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "elite_barbs.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#elixer_golem
def scroll_till_find_elixer_golem():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "elixer_golem.png",
    
        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#elixer_pump
def scroll_till_find_elixer_pump():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "elixer_pump.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#flying_machine
def scroll_till_find_flying_machine():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "flying_machine.png",
   
        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#furnace
def scroll_till_find_furnace():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "furnace.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#goblin_cage
def scroll_till_find_goblin_cage():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "goblin_cage.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#goblin_hut
def scroll_till_find_goblin_hut():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "goblin_hut.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#goblins
def scroll_till_find_goblins():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "goblins.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#heal_spirit
def scroll_till_find_heal_spirit():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "heal_spirit.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#healer
def scroll_till_find_healer():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "healer.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#ice_golem
def scroll_till_find_ice_golem():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "ice_golem.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#ice_spirit
def scroll_till_find_ice_spirit():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "ice_spirit.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#knight
def scroll_till_find_knight():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "knight.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#mega_minion
def scroll_till_find_mega_minion():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "mega_minion.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#minion_hoard
def scroll_till_find_minion_hoard():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "minion_hoard.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#minions
def scroll_till_find_minions():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "minions.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#mortar
def scroll_till_find_mortar():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "mortar.png",
        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#musketeer
def scroll_till_find_musketeer():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "musketeer.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#rascals
def scroll_till_find_rascals():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "rascals.png",
        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#rocket
def scroll_till_find_rocket():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "rocket.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#royal_delivery
def scroll_till_find_royal_delivery():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "royal_delivery.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#royal_giant
def scroll_till_find_royal_giant():
    n = None
    while (n is None)and(loops<50):
        references = [
            "royal_giant.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#royal_hogs
def scroll_till_find_royal_hogs():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "royal_hogs.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#skeleton_barrel
def scroll_till_find_skeleton_barrel():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "skeleton_barrel.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#skeleton_dragons
def scroll_till_find_skeleton_dragons():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "skeleton_dragons.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#skeletons
def scroll_till_find_skeletons():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "skeletons.png",
        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#snowball
def scroll_till_find_snowball():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "snowball.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#spear_goblins
def scroll_till_find_spear_goblins():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "spear_goblins.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#tombstone
def scroll_till_find_tombstone():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "tombstone.png",
        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#wizard
def scroll_till_find_wizard():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "wizard.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#zappies
def scroll_till_find_zappies():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "zappies.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#fire_spirit
def scroll_till_find_fire_spirit():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "fire_spirit.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#fireball
def scroll_till_find_fireball():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "fireball.png",
   
        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#valk
def scroll_till_find_valk():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "valk.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#goblin_gang
def scroll_till_find_goblin_gang():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "goblin_gang.png",
    
        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#zap
def scroll_till_find_zap():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "zap.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"
#inferno_tower
def scroll_till_find_inferno_tower():
    loops=0
    n = None
    while (n is None)and(loops<50):
        references = [
            "inferno_tower.png",

        ]

        locations = find_references(
            screenshot=refresh_screen(),
            folder="request_page_card_logos",
            names=references,
            tolerance=0.97
        )

        for location in locations:
            if location is not None:
                n= location
                if n is not None:
                    return n
        scroll_down()
    return "quit"

# endregion
    

def main_loop():
    # user vars (these will be specified thru the GUI, but these are the placeholders for now.)
    deck = ""
    fight_type = "2v2"
    card_to_request = "goblin_cage"
    cards_to_not_donate=["card_1","card_2","card_3"]
    ssid = random.randint(1,2)
    # vars
    loop_count = 0
    
    
    if not check_if_windows_exist():
        return
    
    
    orientate_memu_multi()
    time.sleep(0.2)
    orientate_window()
    state=check_state()
    if state is None:
        state="restart"
    
    while True:
        time.sleep(0.2)
        logger.log(f"loop count: {loop_count}")
        loop_count += 1
        iar = refresh_screen()
        plt.imshow(iar)
        
        
        #plt.show()
     

        
        
 
        if state == "restart":  
            logger.log("-----STATE=restart-----")
            logger.log("restart time loop")
            logger.log("Restarting menu client")
            if restart_client() == "quit":
                state = "restart"
            else:
                if check_if_on_clash_main_menu():
                    state = "clash_main"
                else:
                    state = "restart"
        if state == "clash_main":
            logger.log("-----STATE=clash_main-----")
            #account switch
            logger.log("Logging in to the correct account")
            if switch_accounts_to(ssid)=="quit":
                #if switching accounts fails
                logger.log("Failed to switch accounts. Restarting")
                state="restart"
            else:
                #if switching accounts works
                logger.log("Successfully switched accounts.")
                #open chests
                if check_if_on_clash_main_menu():
                    logger.log("Opening chests.")
                    open_chests()
                    time.sleep(2)
                    logger.log("Checking if can request.")
                    if check_if_can_request():
                        logger.log("Can request. Passing to request state.")
                        state="request"
                    else:
                        logger.log("Cannot request. Skipping request and passing to donate state.")
                        state="donate"
                else:
                    logger.log("Not on clash main. Restarting.")
                    state ="restart"
        if state == "request":
            logger.log("-----STATE=request-----")
            logger.log("Trying to get to donate page")
            if getto_donate_page() == "quit":
                #if failed to get to clan chat page
                logger.log("Failed to get to clan chat page. Restarting")
                state = "restart" 
            else:
                #if got to clan chat page
                log = "Trying to request "+str(card_to_request)+"."
                logger.log(log)
                if request_from_clash_main_menu(card_to_request) == "quit":
                    #if request failed
                    log = "Failed to request "+str(card_to_request)+"."
                    logger.log(log)
                else:
                    #if request works
                    log = "Successfully requested "+str(card_to_request)+"."
                    logger.log(log)
                logger.log("Done with requesting. Passing to donate state.")
                state="donate"
        if state == "donate":
            logger.log("-----STATE=donate-----")
            if getto_donate_page() == "quit":
                #if failed to get to clan chat page
                logger.log("Failed to get to clan chat page. Restarting")
                state = "restart" 
            else:
                #if got to clan chat page
                logger.log("Successfully got to clan chat page. Starting donate alg")
                click_donates()
                logger.log("Done with donating. Passing to start_fight state")
                state="start_fight"
        if state == "start_fight":
            logger.log("-----STATE=start_fight-----")
            if fight_type =="1v1":
                logger.log("I cant do 1v1s yet. Restarting")
                state="restart"
            if fight_type =="2v2":
                logger.log("Starting a 2v2 match.")
                start_2v2()
                if wait_for_battle_start()=="quit":
                    #if waiting for battle takes too long
                    logger.log("Waited too long for battle start. Restarting")
                    state="restart"
                else:
                    logger.log("Battle has begun. Passing to fighting state") 
                    state="fighting"      
        if state == "fighting":
            logger.log("-----STATE=fighting-----")
            fightloops=0
            while (check_if_in_battle())and(fightloops<100):
                check_quit_key_press()
                log="Plays: "+str(fightloops)
                logger.log(log)
                logger.log("Scanning field.")
                enemy_troop_position=look_for_enemy_troops()
                logger.log("Choosing play.")
                fight_with_deck_list(enemy_troop_position)
                fightloops=fightloops+1
            logger.log("Battle must be finished")
            time.sleep(10)
            leave_end_battle_window()
            wait_for_clash_main_menu()
            state="post_fight"
        if state == "post_fight":
            logger.log("STATE=post_fight")
            logger.log("Back on clash main")
            if check_if_past_game_is_win():
                logger.log("Last game was a win")
                logger.add_win()
            else:
                logger.log("Last game was a loss")
                logger.add_loss()
            #switch accounts feature
            if ssid==1:
                ssid=2 
            else:
                ssid=1
            state="clash_main"

            
            

           

       
        


if __name__ == "__main__":
    main_loop()
