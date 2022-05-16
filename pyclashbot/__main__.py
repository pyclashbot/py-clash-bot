import random
import time

import keyboard
import matplotlib.pyplot as plt
import numpy as np
import pyautogui
import pygetwindow as gw
from PIL import Image

from pyclashbot.logger import Logger
from pyclashbot.image_rec import find_references, find_reference, compare_images, pixel_is_equal
from pyclashbot.card import *

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
    time.sleep(2)
    window_memu.moveTo(0, 0)
    window_memu.resizeTo(460, 680)


def orientate_memu_multi():
    check_quit_key_press()
    window_mimm.minimize()
    window_mimm.restore()
    window_mimm.moveTo(200, 200)
    time.sleep(1)
    window_mimm.moveTo(0, 0)


def open_clash(duration):
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
        return
    pyautogui.moveTo(x=coords[1], y=coords[0], duration=duration)
    pyautogui.click()
    # return coords

    wait_for_clash_main_menu(duration)


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


def check_if_has_chests():
    has_chests = [0] * 4

    
    
    chest_slot_1_image = pyautogui.screenshot(region=(47,493, 65, 75))
    chest_slot_2_image = pyautogui.screenshot(region=(134,493, 65, 75))
    chest_slot_3_image = pyautogui.screenshot(region=(220,493, 65, 75))
    chest_slot_4_image = pyautogui.screenshot(region=(311,493, 65, 75))
    reference_folder = "chest_images"
    references = [
        "golden_chest_1.png",
        "golden_chest_2.png",
        "golden_chest_3.png",
        "golden_chest_4.png",
        "golden_chest_5.png",
        "gold_chest_1.png",
        "gold_chest_2.png",
        "gold_chest_3.png",
        "gold_chest_4.png",
        "gold_chest_5.png",
        "gold_chest_6.png",
        "silver_chest_1.png",
        "silver_chest_2.png",
        "silver_chest_3.png",
        "silver_chest_4.png",
        "silver_chest_5.png",
    ]
    location_slot_1 = find_references(
        screenshot=chest_slot_1_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97
    )
    location_slot_2 = find_references(
        screenshot=chest_slot_2_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97
    )
    location_slot_3 = find_references(
        screenshot=chest_slot_3_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97
    )
    location_slot_4 = find_references(
        screenshot=chest_slot_4_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97
    )
    for location in location_slot_1:
        if location is not None:
            has_chests[0]=1
    for location in location_slot_2:
        if location is not None:
            has_chests[1]=1
    for location in location_slot_3:
        if location is not None:
            has_chests[2]=1
    for location in location_slot_4:
        if location is not None:
            has_chests[3]=1
    return has_chests
    
    
    
    
    
    return has_chests


def open_chests(duration):
    check_quit_key_press()
    n = check_if_has_chests()
    if n[0] == 1:
        logger.log("Chest detected in slot 1")
        logger.log("clicking chest1")
        pyautogui.moveTo(x=78, y=554, duration=duration)
        pyautogui.click()
        check_quit_key_press()
        time.sleep(2)
        logger.log("opening chest1")
        pyautogui.moveTo(x=210, y=455, duration=duration)
        pyautogui.click()
        time.sleep(1)
        pyautogui.click()
        time.sleep(1)
        logger.log("skipping through chest1")
        pyautogui.click(x=20, y=556, clicks=20, interval=0.2, button='left')
        check_quit_key_press()
    if n[1] == 1:
        logger.log("Chest detected in slot 2")
        logger.log("clicking chest2")
        pyautogui.moveTo(x=162, y=549, duration=duration)
        check_quit_key_press()
        pyautogui.click()
        time.sleep(2)
        logger.log("opening chest2")
        pyautogui.moveTo(x=210, y=455, duration=duration)
        time.sleep(1)
        pyautogui.click()
        pyautogui.click()
        time.sleep(1)
        logger.log("skipping through chest2")
        pyautogui.click(x=20, y=556, clicks=20, interval=0.2, button='left')
        check_quit_key_press()
    if n[2] == 1:
        logger.log("Chest detected in slot 3")
        logger.log("clicking chest3")
        check_quit_key_press()
        pyautogui.moveTo(x=263, y=541, duration=duration)
        pyautogui.click()
        time.sleep(2)
        logger.log("opening chest3")
        pyautogui.moveTo(x=210, y=455, duration=duration)
        time.sleep(1)
        pyautogui.click()
        pyautogui.click()
        time.sleep(1)
        logger.log("skipping through chest3")
        pyautogui.click(x=20, y=556, clicks=20, interval=0.2, button='left')
        check_quit_key_press()
    if n[3] == 1:
        logger.log("Chest detected in slot 4")
        logger.log("clicking chest4")
        pyautogui.moveTo(x=349, y=551, duration=duration)
        check_quit_key_press()
        pyautogui.click()
        time.sleep(2)
        logger.log("opening chest4")
        pyautogui.moveTo(x=210, y=455, duration=duration)
        time.sleep(1)
        pyautogui.click()
        pyautogui.click()
        time.sleep(1)
        logger.log("skipping through chest4")
        pyautogui.click(x=20, y=556, clicks=20, interval=0.2, button='left')
        check_quit_key_press()


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


def request_from_clash_main_menu(duration):
    check_quit_key_press()
    logger.log("Moving to clan chat page")
    pyautogui.moveTo(x=317, y=627, duration=duration)
    pyautogui.click()
    while not check_if_on_clan_chat_page():
        pyautogui.moveTo(x=317, y=627, duration=duration)
        pyautogui.click()
        time.sleep(2)
    logger.log("requesting giant")
    pyautogui.moveTo(x=86, y=564, duration=duration)
    pyautogui.click()
    # scroll till find card
    time.sleep(2)
    while check_for_request_card() is None:
        pyautogui.scroll(-90, x=0, y=0)
        time.sleep(3)
        check_quit_key_press()
    # click card
    coords = check_for_request_card()
    if coords is not None:
        pyautogui.moveTo(x=coords[1], y=coords[0], duration=duration)
        pyautogui.click()
        time.sleep(2)
    # click request
    coords = look_for_request_button()
    if coords is not None:
        pyautogui.moveTo(x=coords[1], y=coords[0], duration=duration)
        pyautogui.click()
        time.sleep(2)
    return_to_clash_main_menu(duration)


def check_for_request_card():
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
        tolerance=0.99
    )

    for location in locations:
        if location is not None:
            return location
    return None


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
    check_quit_key_press()
    iar = refresh_screen()
    pix1 = iar[573][109]
    pix2 = iar[573][116]
    pix3 = iar[573][121]
    sentinel = [1] * 3
    sentinel[0] = 255
    sentinel[1] = 188
    sentinel[2] = 42

    if not pixel_is_equal(pix1, sentinel, 10):
        return False
    if not pixel_is_equal(pix2, sentinel, 10):
        return False
    if not pixel_is_equal(pix3, sentinel, 10):
        return False
    check_quit_key_press()
    return True


def return_to_clash_main_menu(duration):
    check_quit_key_press()
    logger.log("Returning to clash main menu")
    pyautogui.moveTo(x=180, y=625, duration=duration)
    pyautogui.click()
    check_quit_key_press()


def start_2v2(duration):
    check_quit_key_press()
    logger.log("Navigating to 2v2 match")
    pyautogui.moveTo(x=280, y=440, duration=duration)
    pyautogui.click()
    time.sleep(2)
    pyautogui.scroll(-10, x=0, y=0)
    time.sleep(3)
    pyautogui.moveTo(x=300, y=300, duration=duration)
    pyautogui.click()
    check_quit_key_press()


def start_1v1_ranked(duration):
    check_quit_key_press()
    logger.log("Navigating to 1v1 ranked match")
    pyautogui.moveTo(x=140, y=440, duration=duration)
    pyautogui.click()
    wait_for_battle_start()
    check_quit_key_press()


def wait_for_battle_start():
    logger.log("Waiting for battle start")
    n = 1
    n1 = 0
    check_quit_key_press()
    while n == 1:
        n1 += 1
        if check_if_in_battle():
            n = 0
        time.sleep(1)
        if n1 > 90:
            logger.log("Waited longer than 90 sec for a fight")
            break
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


def check_if_in_battle():
    check_quit_key_press()
    iar = refresh_screen()
    pix1 = iar[551][56]
    pix2 = iar[549][78]
    pix3 = iar[567][73]
    sentinel = [1] * 3
    sentinel[0] = 255
    sentinel[1] = 255
    sentinel[2] = 255

    if not pixel_is_equal(pix1, sentinel, 10):
        return False
    if not pixel_is_equal(pix2, sentinel, 10):
        return False
    if not pixel_is_equal(pix3, sentinel, 10):
        return False
    check_quit_key_press()
    return True


def leave_end_battle_window(duration):
    check_quit_key_press()
    logger.log("battle is over. return to clash main menu")
    pyautogui.moveTo(x=81, y=630, duration=duration)
    pyautogui.click()
    time.sleep(5)
    check_quit_key_press()


def refresh_clan_tab(duration):
    check_quit_key_press()
    pyautogui.moveTo(x=300, y=630, duration=duration)
    pyautogui.click()
    return_to_clash_main_menu(duration)
    time.sleep(3)
    check_quit_key_press()


def check_if_exit_battle_button_exists():
    check_quit_key_press()
    iar = refresh_screen()
    pix1 = iar[634][52]
    pix3 = iar[640][107]
    sentinel = [1] * 3
    sentinel[0] = 76
    sentinel[1] = 174
    sentinel[2] = 255
    if not pixel_is_equal(pix1, sentinel, 10):
        return False
    if not pixel_is_equal(pix3, sentinel, 10):
        return False
    check_quit_key_press()
    return True


def find_donates():
    logger.log("searching screen for donate buttons")
    references = [
        "donate_button_1.png",
        "donate_button_2.png",
        "donate_button_3.png",
        "donate_button_4.png",
        "donate_button_5.png"
    ]

    locations = find_references(
        screenshot=pyautogui.screenshot(),
        folder="donate",
        names=references,
        tolerance=0.97
    )

    for location in locations:
        if location is not None:
            return location
    logger.log("Found none this go-around")
    return [500, 50]


def click_donates(duration):
    logger.log("clicking the donate buttons if there are any available")
    check_quit_key_press()
    n = 0
    while n < 3:
        coords = find_donates()
        if coords is not None:
            pyautogui.moveTo(x=coords[1], y=coords[0], duration=duration)
            pyautogui.click(x=coords[1], y=coords[0],
                            clicks=5, interval=0.2, button='left')

            if check_if_more_donates():
                pyautogui.moveTo(x=50, y=170, duration=duration)
                pyautogui.click()
                time.sleep(2)

            pyautogui.moveTo(x=coords[1], y=coords[0], duration=duration)
            pyautogui.click(x=coords[1], y=coords[0],
                            clicks=5, interval=0.2, button='left')
        n += 1
    pyautogui.moveTo(x=393, y=525, duration=duration)
    pyautogui.click()
    check_quit_key_press()
    return_to_clash_main_menu(duration)


def getto_donate_page(duration):
    check_quit_key_press()
    logger.log("Moving to clan chat page")
    pyautogui.moveTo(x=317, y=627, duration=duration)
    pyautogui.click()
    while not check_if_on_clan_chat_page():
        pyautogui.moveTo(x=317, y=627, duration=duration)
        pyautogui.click()
        time.sleep(2)
    check_quit_key_press()


def check_if_more_donates():
    check_quit_key_press()
    iar = refresh_screen()
    pix1 = iar[186][34]
    pix2 = iar[177][32]
    pix3 = iar[163][61]
    sentinel = [1] * 3
    sentinel[0] = 214
    sentinel[1] = 234
    sentinel[2] = 244

    more_donates_exists = True
    if not pixel_is_equal(pix1, sentinel, 10):
        more_donates_exists = False
    if not pixel_is_equal(pix2, sentinel, 10):
        more_donates_exists = False
    if not pixel_is_equal(pix3, sentinel, 10):
        more_donates_exists = False
    check_quit_key_press()
    return more_donates_exists


def check_quit_key_press():
    if keyboard.is_pressed("space"):
        logger.log("space is pressed. Quitting the program")
        quit()


def restart_client(duration):
    check_quit_key_press()
    logger.log("closing client")
    pyautogui.moveTo(x=540, y=140, duration=duration)
    pyautogui.click()
    time.sleep(2)
    check_quit_key_press()
    logger.log("opening client")
    pyautogui.moveTo(x=540, y=140, duration=duration)
    pyautogui.click()
    time.sleep(5)
    check_quit_key_press()
    time.sleep(5)
    check_quit_key_press()
    time.sleep(5)
    logger.log("skipping ads")
    orientate_window()
    time.sleep(1)
    pyautogui.moveTo(x=440, y=600, duration=duration)
    time.sleep(1)
    pyautogui.click()
    time.sleep(1)
    pyautogui.click()
    time.sleep(1)
    pyautogui.click()
    time.sleep(1)
    open_clash(duration)


def wait_for_clash_main_menu(duration):
    n = 0
    while not check_if_on_clash_main_menu():

        check_quit_key_press()
        time.sleep(3)
        logger.log(f"Waiting for clash main menu/{n}")
        n = n+1
        if n > 20:
            logger.log("Waiting longer than a minute for clash main menu")
            break
        pyautogui.moveTo(x=50, y=190, duration=duration)
        pyautogui.moveTo(x=10, y=170, duration=duration)
        pyautogui.click()


def check_if_past_game_is_win(duration):
    check_quit_key_press()
    open_activity_log(duration)
    iar = refresh_screen()

    n = 40
    while n < 130:
        pix = iar[191][n]
        sentinel = [1] * 3
        sentinel[0] = 102
        sentinel[1] = 204
        sentinel[2] = 255
        if pixel_is_equal(pix, sentinel, 10):
            return True
        n = n+1
    time.sleep(1)
    pyautogui.moveTo(x=385, y=507, duration=duration)
    pyautogui.click(x=385, y=507, clicks=1, interval=0.2, button='left')
    return False


def open_activity_log(duration):
    check_quit_key_press()
    pyautogui.moveTo(x=360, y=99, duration=duration)
    pyautogui.click()
    time.sleep(1)
    check_quit_key_press()
    pyautogui.moveTo(x=255, y=75, duration=duration)
    pyautogui.click()
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
    current_image = refresh_screen()

    references = [
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


def main_loop():
    # vars
    fights = 0
    duration = 0.5
    fight_duration = 0.2
    loop_count = 0
    deck = ["witch", "fire_spirit", "mother_witch", "hog",
            "valk", "firecracker", "bandit", "musketeer"]

    if not check_if_windows_exist():
        return

    while True:
        time.sleep(1)
        logger.log(f"loop count: {loop_count}")
        loop_count += 1
        iar = refresh_screen()
        plt.imshow(iar)

        #plt.show()

        print(check_for_card_in_hand("barb_hut"))
        print(check_for_card_in_hand("goblin_drill"))
        print(check_for_card_in_hand("three_musketeers"))


        # orientate_memu_multi()
        # time.sleep(1)
        # restart_client(duration)
        # orientate_window()
        # if check_if_on_clash_main_menu():
        #     logger.log("We're on the main menu")
        #     time.sleep(1)
        #     logger.log("Handling chests")
        #     time.sleep(1)
        #     open_chests(duration)
        #     time.sleep(3)
        #     logger.log("Checking if can request")
        #     time.sleep(1)
        #     if check_if_can_request():
        #         logger.log("Can request. Requesting giant")
        #         time.sleep(1)
        #         request_from_clash_main_menu(duration)
        #     else:
        #         logger.log("Request is unavailable")
        #     logger.log("Checking if can donate")
        #     time.sleep(1)
        #     getto_donate_page(duration)
        #     click_donates(duration)
        # else:
        #     logger.log("not on clash main menu")

        # #check deck
        # deck = check_deck()
        # time.sleep(2)


        # logger.log("Handled chests, requests, and deck. Gonna start a battle")
        # time.sleep(1)
        # start_2v2(duration)
        # logger.add_fight()
        # wait_for_battle_start()
        # fightloops = 0
        # while not check_if_exit_battle_button_exists():
        #     fightloops = fightloops + 1
        #     logger.log(f"fightloop: {fightloops}")
        #     fight_with_deck_list(deck)
        #     if fightloops > 100:
        #         break
        # leave_end_battle_window(duration)
        # time.sleep(5)
        # if check_if_past_game_is_win(duration):
        #     logger.log("Last game was a win")
        #     logger.add_win()
        # else:
        #     logger.log("Last gane was a loss")
        #     logger.add_loss()
            
            
if __name__ == "__main__":
    main_loop()
