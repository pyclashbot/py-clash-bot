import random
import time

from pyclashbot.client import (check_quit_key_press, click, refresh_screen,
                               screenshot, scroll_down)
from pyclashbot.image_rec import find_references, pixel_is_equal
from pyclashbot.state import check_if_in_battle, wait_for_clash_main_menu


def start_1v1_ranked(logger):
    check_quit_key_press()
    logger.log("Navigating to 1v1 ranked match")
    click(140, 440)
    wait_for_battle_start(logger)
    check_quit_key_press()


def start_2v2(logger):
    logger.log("Initiating 2v2 match from main menu")
    logger.log("Clicking party mode")
    party_button_coords = find_party_button()
    if party_button_coords is None:
        return "quit"
    click(x=party_button_coords[1], y=party_button_coords[0])
    logger.log("Scrolling until 2v2 button is found")
    loops=0
    while find_2v2_quick_match_button() is None:
        if loops>20:
            return"quit"
        scroll_down()
        time.sleep(0.05)
        scroll_down()
        time.sleep(1)
        loops=loops+1
    logger.log("Clicking 2v2 quickmatch button")
    time.sleep(1)
    quick_match_button_coords = find_2v2_quick_match_button()
    if quick_match_button_coords is None:
        return "quit"
    time.sleep(1)
    click(x=quick_match_button_coords[1], y=quick_match_button_coords[0])
    time.sleep(0.25)
    check_for_reward_limit()


def find_2v2_quick_match_button():
    current_image = screenshot()
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
    current_image = screenshot()
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


def wait_for_battle_start(logger):
    logger.log("Waiting for battle start")
    n = 1
    n1 = 0
    check_quit_key_press()
    while n == 1:
        if check_if_in_battle():
            n = 0
        click(100, 100)
        time.sleep(0.25)
        n1 += 1
        if n1 > 120:
            logger.log("Waited longer than 30 sec for a fight")
            return "quit"
        refresh_screen()
        check_quit_key_press()


def fight_in_2v2(logger):
    check_quit_key_press()
    card_coord = random_card_coord_picker(logger)
    placement_coord = look_for_enemy_troops()
    if placement_coord is None:
        logger.log("picking random coord")
        placement_coord = random_placement_coord_maker(logger)
    else:
        logger.log("picking coord: ", placement_coord)
        placement_coord[1] = placement_coord[1] + 30
    # pick card
    click(card_coord[0], card_coord[1], clicks=1, interval=0)
    # place card
    click(x=placement_coord[0], y=placement_coord[1], clicks=1, interval=0)


def look_for_enemy_troops():
    current_image = screenshot(region=(78, 141, 271, 356))

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


def leave_end_battle_window(logger):
    check_quit_key_press()
    logger.log("battle is over. return to clash main menu")
    click(81, 630)
    time.sleep(0.2)
    click(211, 580)
    wait_for_clash_main_menu(logger)
    check_quit_key_press()


def check_if_exit_battle_button_exists():
    current_image = screenshot()
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


def open_activity_log(logger):
    check_quit_key_press()
    click(x=360, y=99)

    time.sleep(1)
    check_quit_key_press()
    click(x=255, y=75)

    time.sleep(1)
    check_quit_key_press()


def check_if_past_game_is_win(logger):
    check_quit_key_press()
    open_activity_log(logger)
    iar = refresh_screen()

    n = 40
    while n < 130:
        pix = iar[191][n]
        sentinel = [1] * 3
        sentinel[0] = 102
        sentinel[1] = 204
        sentinel[2] = 255
        if pixel_is_equal(pix, sentinel, 10):
            click(20, 507)

            return True
        n = n + 1
    time.sleep(1)
    click(385, 507)
    click(20, 507)
    return False


def random_card_coord_picker(logger):
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


def random_placement_coord_maker(logger):
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


def check_for_reward_limit():
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
