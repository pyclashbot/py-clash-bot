import random
import time
from os.path import join
from typing import Union

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

    iar = refresh_screen()
    chest1_pix = iar[572][93]
    chest2_pix = iar[566][158]
    chest3_pix = iar[572][277]
    chest4_pix = iar[574][326]

    sentinel = [1] * 3
    sentinel[0] = 34
    sentinel[1] = 122
    sentinel[2] = 173

    if not pixel_is_equal(chest1_pix, sentinel, 40):
        has_chests[0] = 1
    if not pixel_is_equal(chest2_pix, sentinel, 40):
        has_chests[1] = 1
    if not pixel_is_equal(chest3_pix, sentinel, 40):
        has_chests[2] = 1
    if not pixel_is_equal(chest4_pix, sentinel, 40):
        has_chests[3] = 1

    check_quit_key_press()
    return has_chests


def open_chests(duration):
    check_quit_key_press()
    n = check_if_has_chests()
    if n[0] == 1:
        logger.log("Chest detected in slot 1")
        pyautogui.moveTo(x=78, y=554, duration=duration)
        pyautogui.click()
        check_quit_key_press()
        time.sleep(1)
        pyautogui.moveTo(x=210, y=455, duration=duration)
        pyautogui.click()
        time.sleep(1)
        pyautogui.click()
        time.sleep(1)
        pyautogui.click(x=20, y=556, clicks=20, interval=0.2, button='left')
        check_quit_key_press()
    if n[1] == 1:
        logger.log("Chest detected in slot 2")
        pyautogui.moveTo(x=162, y=549, duration=duration)
        check_quit_key_press()
        pyautogui.click()
        time.sleep(1)
        pyautogui.moveTo(x=210, y=455, duration=duration)
        time.sleep(1)
        pyautogui.click()
        pyautogui.click()
        time.sleep(1)
        pyautogui.click(x=20, y=556, clicks=20, interval=0.2, button='left')
        check_quit_key_press()
    if n[2] == 1:
        logger.log("Chest detected in slot 3")
        check_quit_key_press()
        pyautogui.moveTo(x=263, y=541, duration=duration)
        pyautogui.click()
        time.sleep(1)
        pyautogui.moveTo(x=210, y=455, duration=duration)
        time.sleep(1)
        pyautogui.click()
        pyautogui.click()
        time.sleep(1)
        pyautogui.click(x=20, y=556, clicks=20, interval=0.2, button='left')
        check_quit_key_press()
    if n[3] == 1:
        logger.log("Chest detected in slot 4")
        pyautogui.moveTo(x=349, y=551, duration=duration)
        check_quit_key_press()
        pyautogui.click()
        time.sleep(1)
        pyautogui.moveTo(x=210, y=455, duration=duration)
        time.sleep(1)
        pyautogui.click()
        pyautogui.click()
        time.sleep(1)
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
    pyautogui.moveTo(x=coords[1], y=coords[0], duration=duration)
    pyautogui.click()
    time.sleep(2)
    # click request
    coords = look_for_request_button()
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
    comparisons = ["empty"]*8
    comparisons = find_all_cards(deck_image, comparisons)

    time.sleep(2)
    pyautogui.moveTo(x=245, y=640, duration=1)
    pyautogui.click()
    time.sleep(2)
    return comparisons


def check_for_card_in_hand(card):
    hand_screenshot = pyautogui.screenshot()

    # if card == "mega_knight":
    # coords_reverse= compare_images(hand_screenshot, Image.open(join("pyclashbot", "reference_images", "hand_cards", "mega_knight.png")), 0.97)
    # if coords_reverse is not None:
    #     return [coords_reverse[1],coords_reverse[0]]

    if card == "skeletons":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "skeletons.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find skeletons")
    if card == "ice_spirit":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "ice_spirit.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find ice_spirit")
    if card == "fire_spirit":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "fire_spirit.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find fire_spirit")
    if card == "e_spirit":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "e_spirit.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find e_spirit")
    if card == "mirror":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "mirror.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find mirror")
    if card == "heal_spirit":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "heal_spirit.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find heal_spirit")
    if card == "goblins":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "goblins.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find goblins")
    if card == "bomber":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "bomber.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find bomber")

    if card == "spear_goblins":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "spear_goblins.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find spear_goblins")
    if card == "ice_golem":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "ice_golem.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find ice_golem")
    if card == "bats":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "bats.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find bats")
    if card == "wall_breaker":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "wall_breaker.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find wall_breaker")
    if card == "rage":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "rage.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find rage")
    if card == "zap":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "zap.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find zap")
    if card == "log":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "log.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find log")
    if card == "barb_barrel":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "barb_barrel.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find barb_barrel")
    if card == "snowball":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "snowball.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find snowball")
    if card == "knight":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "knight.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find knight")
    if card == "archers":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "archers.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find archers")
    if card == "minions":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "minions.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find minions")
    if card == "skeleton_army":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "skeleton_army.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find skeleton_army")
    if card == "ice_wizard":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "ice_wizard.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find ice_wizard")
    if card == "guards":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "guards.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find guards")
    if card == "princess":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "princess.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find princess")
    if card == "miner":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "miner.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find miner")
    if card == "mega_minion":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "mega_minion.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find mega_minion")
    if card == "dart_goblin":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "dart_goblin.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find dart_goblin")
    if card == "goblin_gang":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "goblin_gang.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find goblin_gang")
    if card == "bandit":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "bandit.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find bandit")
    if card == "royal_ghost":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "royal_ghost.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find royal_ghost")
    if card == "skeleton_barrel":
        coords_reverse = compare_images(hand_screenshot, Image.open(join(
            "pyclashbot", "reference_images", "hand_cards", "skeleton_barrel.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find skeleton_barrel")
    if card == "fisherman":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "fisherman.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find fisherman")
    if card == "firecracker":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "firecracker.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find firecracker")
    if card == "elixer_golem":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "elixer_golem.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find elixer_golem")
    if card == "cannon":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "cannon.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find cannon")
    if card == "tombstone":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "tombstone.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find tombstone")
    if card == "arrows":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "arrows.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find arrows")
    if card == "goblin_barrel":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "goblin_barrel.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find goblin_barrel")
    if card == "tornado":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "tornado.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find tornado")
    if card == "clone":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "clone.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find clone")
    if card == "earthquake":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "earthquake.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find earthquake")
    if card == "royal_delivery":
        coords_reverse = compare_images(hand_screenshot, Image.open(join(
            "pyclashbot", "reference_images", "hand_cards", "royal_delivery.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find royal_delivery")
    if card == "valk":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "valk.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find valk")
    if card == "musketeer":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "musketeer.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find musketeer")
    if card == "baby_dragon":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "baby_dragon.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find baby_dragon")
    if card == "mini_pekka":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "mini_pekka.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find mini_pekka")
    if card == "hog":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "hog.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find hog")
    if card == "dark_knight":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "dark_knight.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find dark_knight")
    if card == "lumberjack":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "lumberjack.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find lumberjack")
    if card == "battle_ram":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "battle_ram.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find battle_ram")
    if card == "inferno_dragon":
        coords_reverse = compare_images(hand_screenshot, Image.open(join(
            "pyclashbot", "reference_images", "hand_cards", "inferno_dragon.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find inferno_dragon")
    if card == "e_wiz":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "e_wiz.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find e_wiz")
    if card == "hunter":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "hunter.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find hunter")
    if card == "zappies":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "zappies.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find zappies")
    if card == "magic_archer":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "magic_archer.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find magic_archer")
    if card == "mighty_miner":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "mighty_miner.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find mighty_miner")
    if card == "skeleton_king":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "skeleton_king.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find skeleton_king")
    if card == "golden_knight":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "golden_knight.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find golden_knight")
    if card == "mortar":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "mortar.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find mortar")
    if card == "bomb_tower":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "bomb_tower.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find bomb_tower")
    if card == "tesla":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "tesla.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find tesla")
    if card == "furnace":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "furnace.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find furnace")
    if card == "goblin_cage":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "goblin_cage.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find goblin_cage")
    if card == "goblin_drill":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "goblin_drill.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find goblin_drill")
    if card == "fireball":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "fireball.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find fireball")
    if card == "freeze":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "freeze.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find freeze")
    if card == "poison":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "poison.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find poison")
    if card == "giant":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "giant.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find giant")
    if card == "balloon":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "balloon.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find balloon")
    if card == "barbs":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "barbs.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find barbs")
    if card == "minions":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "minions.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find minions")
    if card == "bowler":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "bowler.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find bowler")
    if card == "executioner":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "executioner.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find executioner")
    if card == "ram_rider":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "ram_rider.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find ram_rider")
    if card == "rascals":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "rascals.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find rascals")
    if card == "cannon_cart":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "cannon_cart.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find cannon_cart")
    if card == "royal_hogs":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "royal_hogs.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find royal_hogs")
    if card == "archer_queen":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "archer_queen.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find archer_queen")
    if card == "goblin_hut":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "goblin_hut.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find goblin_hut")
    if card == "inferno_tower":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "inferno_tower.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find inferno_tower")
    if card == "graveyard":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "graveyard.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find graveyard")
    if card == "giant_skeleton":
        coords_reverse = compare_images(hand_screenshot, Image.open(join(
            "pyclashbot", "reference_images", "hand_cards", "giant_skeleton.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find giant_skeleton")
    if card == "royal_giant":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "royal_giant.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find royal_giant")
    if card == "sparky":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "sparky.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find sparky")
    if card == "elite_barbs":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "elite_barbs.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find elite_barbs")
    if card == "goblin_giant":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "goblin_giant.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find goblin_giant")
    if card == "elixer_pump":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "elixer_pump.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find elixer_pump")
    if card == "xbow":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "xbow.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find xbow")
    if card == "lightning":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "lightning.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find lightning")
    if card == "pekka":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "pekka.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find pekka")
    if card == "lavahound":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "lavahound.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find lavahound")
    if card == "royal_guards":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "royal_guards.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find royal_guards")
    if card == "mega_knight":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "mega_knight.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find mega_knight")
    if card == "barb_hut":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "barb_hut.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find barb_hut")
    if card == "golem":
        coords_reverse = compare_images(hand_screenshot, Image.open(
            join("pyclashbot", "reference_images", "hand_cards", "golem.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find golem")
    if card == "three_musketeers":
        coords_reverse = compare_images(hand_screenshot, Image.open(join(
            "pyclashbot", "reference_images", "hand_cards", "three_musketeers.png")), 0.97)
        if coords_reverse is not None:
            return [coords_reverse[1], coords_reverse[0]]
        else:
            logger.log("Could not find three_musketeers")


def fight_with_deck_list(deck_list):
    # turrets
    # if tesla in deck and in hand
    if (check_if_card_in_deck(deck_list, "tesla")) and (check_for_card_in_hand("tesla") is not None):
        logger.log("Decided to play tesla")
        card_coords = check_for_card_in_hand("tesla")
        placement_coords = [212, 385]
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
# melee tanks
     # if bandit in deck and bandit in hand
    if (check_if_card_in_deck(deck_list, "bandit")) and (check_for_card_in_hand("bandit") is not None):
        logger.log("Decided to play bandit")
        card_coords = check_for_card_in_hand("bandit")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+45
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if dark_knight in deck and dark_knight in hand
    if (check_if_card_in_deck(deck_list, "dark_knight")) and (check_for_card_in_hand("dark_knight") is not None):
        logger.log("Decided to play dark_knight")
        card_coords = check_for_card_in_hand("dark_knight")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if fire_spirit in deck and fire_spirit in hand
    if (check_if_card_in_deck(deck_list, "fire_spirit")) and (check_for_card_in_hand("fire_spirit") is not None):
        logger.log("Decided to play fire_spirit")
        card_coords = check_for_card_in_hand("fire_spirit")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+30
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if mega_knight in deck and mega_knight in hand
    if (check_if_card_in_deck(deck_list, "mega_knight")) and (check_for_card_in_hand("mega_knight") is not None):
        logger.log("Decided to play mega_knight")
        card_coords = check_for_card_in_hand("mega_knight")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1] + 30
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if mini_pekka in deck and mini_pekka in hand
    if (check_if_card_in_deck(deck_list, "mini_pekka")) and (check_for_card_in_hand("mini_pekka") is not None):
        logger.log("Decided to play mini_pekka")
        card_coords = check_for_card_in_hand("mini_pekka")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if pekka in deck and pekka in hand
    if (check_if_card_in_deck(deck_list, "pekka")) and (check_for_card_in_hand("pekka") is not None):
        logger.log("Decided to play pekka")
        card_coords = check_for_card_in_hand("pekka")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if royal_ghost in deck and royal_ghost in hand
    if (check_if_card_in_deck(deck_list, "royal_ghost")) and (check_for_card_in_hand("royal_ghost") is not None):
        logger.log("Decided to play royal_ghost")
        card_coords = check_for_card_in_hand("royal_ghost")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if royal_recruits in deck and in hand
    if (check_if_card_in_deck(deck_list, "royal_recruits")) and (check_for_card_in_hand("royal_recruits") is not None):
        logger.log("Decided to play royal_recruits")
        card_coords = check_for_card_in_hand("royal_recruits")
        placement_coords = [215, 390]
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if valk in deck and valk in hand
    if (check_if_card_in_deck(deck_list, "valk")) and (check_for_card_in_hand("valk") is not None):
        logger.log("Decided to play valk")
        card_coords = check_for_card_in_hand("valk")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if barb_barrel in deck and in hand
    if (check_if_card_in_deck(deck_list, "barb_barrel")) and (check_for_card_in_hand("barb_barrel") is not None) and (look_for_enemy_troops() is not None):
        logger.log("Decided to play barb_barrel")
        card_coords = check_for_card_in_hand("barb_barrel")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+30
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
# ranged
    # if e_wiz in deck and e_wiz in hand
    if (check_if_card_in_deck(deck_list, "e_wiz")) and (check_for_card_in_hand("e_wiz") is not None):
        logger.log("Decided to play e_wiz")
        card_coords = check_for_card_in_hand("e_wiz")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+25
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if firecracker in deck and firecracker in hand
    if (check_if_card_in_deck(deck_list, "firecracker")) and (check_for_card_in_hand("firecracker") is not None):
        logger.log("Decided to play firecracker")
        card_coords = check_for_card_in_hand("firecracker")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+65
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if goblin_gang in deck and goblin_gang in hand
    if (check_if_card_in_deck(deck_list, "goblin_gang")) and (check_for_card_in_hand("goblin_gang") is not None):
        logger.log("Decided to play goblin_gang")
        card_coords = check_for_card_in_hand("goblin_gang")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+35
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if mother_witch in deck and in hand
    if (check_if_card_in_deck(deck_list, "mother_witch")) and (check_for_card_in_hand("mother_witch") is not None):
        logger.log("Decided to play mother_witch")
        card_coords = check_for_card_in_hand("mother_witch")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+65
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if musketeer in deck and musketeer in hand
    if (check_if_card_in_deck(deck_list, "musketeer")) and (check_for_card_in_hand("musketeer") is not None):
        logger.log("Decided to play musketeer")
        card_coords = check_for_card_in_hand("musketeer")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+65
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if night_witch in deck and in hand
    if (check_if_card_in_deck(deck_list, "night_witch")) and (check_for_card_in_hand("night_witch") is not None):
        logger.log("Decided to play night_witch")
        card_coords = check_for_card_in_hand("night_witch")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+65
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if witch in deck and in hand
    if (check_if_card_in_deck(deck_list, "witch")) and (check_for_card_in_hand("witch") is not None):
        logger.log("Decided to play witch")
        card_coords = check_for_card_in_hand("witch")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+65
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if archer_queen in deck and archer_queen in hand
    if (check_if_card_in_deck(deck_list, "archer_queen")) and (check_for_card_in_hand("archer_queen") is not None):
        logger.log("Decided to play archer_queen")
        card_coords = check_for_card_in_hand("archer_queen")
        placement_coords = look_for_enemy_troops()
        if placement_coords is None:
            placement_coords = random_placement_coord_maker()
        else:
            placement_coords[1] = placement_coords[1]+65
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
# spells
    # if fireball in deck and in hand
    if (check_if_card_in_deck(deck_list, "fireball")) and (check_for_card_in_hand("fireball") is not None):
        logger.log("Decided to play fireball")
        card_coords = check_for_card_in_hand("fireball")
        n99 = random.randint(1, 2)
        if n99 == 1:
            placement_coords = [97, 203]
        if n99 == 2:
            placement_coords = [320, 208]
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if poison in deck and in hand
    if (check_if_card_in_deck(deck_list, "poison")) and (check_for_card_in_hand("poison") is not None):
        logger.log("Decided to play poison")
        card_coords = check_for_card_in_hand("poison")
        n99 = random.randint(1, 2)
        if n99 == 1:
            placement_coords = [97, 203]
        if n99 == 2:
            placement_coords = [320, 208]
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
# hogs
    # if battle_ram in deck and battle_ram in hand
    if (check_if_card_in_deck(deck_list, "battle_ram")) and (check_for_card_in_hand("battle_ram") is not None):
        logger.log("Decided to play archer_queen")
        card_coords = check_for_card_in_hand("archer_queen")
        placement_coords = random_placement_coord_maker()
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if hog in deck and hog in hand
    if (check_if_card_in_deck(deck_list, "hog")) and (check_for_card_in_hand("hog") is not None):
        logger.log("Decided to play hog")
        card_coords = check_for_card_in_hand("hog")
        placement_coords = random_placement_coord_maker()
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return
    # if ram_rider in deck and ram_rider in hand
    if (check_if_card_in_deck(deck_list, "ram_rider")) and (check_for_card_in_hand("ram_rider") is not None):
        logger.log("Decided to play ram_rider")
        card_coords = check_for_card_in_hand("ram_rider")
        placement_coords = random_placement_coord_maker()
        # click card
        pyautogui.moveTo(x=card_coords[0], y=card_coords[1], duration=0)
        pyautogui.click()
        # click placement
        pyautogui.moveTo(
            x=placement_coords[0], y=placement_coords[1], duration=0)
        pyautogui.click()
        return

    logger.log("No moves found. Waiting")
    time.sleep(3)
    check_quit_key_press()


def check_if_card_in_deck(deck_list, card):
    n = 0
    while n < 8:
        if deck_list[n] == card:
            return True
        n = n+1
    return False


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

        # plt.show()

        check_for_card_in_hand(card)

        # while 1 == 1:
        #     fight_with_deck_list(deck)

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
