import time

import numpy
import pyautogui
from ahk import AHK

from pyclashbot.bot.navigation import (
    check_if_on_clash_main_menu,
    get_to_clash_main_settings_page,
    get_to_party_mode_page_from_settings_page,
    get_to_ssid_switch_page,
    get_to_switch_accounts_tab,
    handle_card_mastery_notification,
    open_profile_page,
    wait_for_clash_main_menu,
)
from pyclashbot.detection import (
    check_for_location,
    find_references,
    get_first_location,
    pixel_is_equal,
)
from pyclashbot.memu import click, screenshot, scroll_down, scroll_up_fast
from pyclashbot.memu.client import (
    get_file_count,
    make_reference_image_list,
    scroll_down_fast,
)
from pyclashbot.utils.logger import Logger

ahk = AHK()
logger = Logger()


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


def find_2v2_quick_match_button():
    # method to find the 2v2 quickmatch button in the party mode menu
    current_image = screenshot()
    reference_folder = "2v2_quick_match"

    references = make_reference_image_list(
        get_file_count(
            "2v2_quick_match",
        )
    )

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97,
    )

    coord = get_first_location(locations)
    return None if coord is None else [coord[1] + 200, coord[0] + 50]


def check_for_reward_limit():
    # method to find the 2v2 quickmatch button in the party mode menu
    current_image = screenshot()
    reference_folder = "reward_limit"

    references = make_reference_image_list(
        get_file_count(
            "reward_limit",
        )
    )

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97,
    )

    for location in locations:
        if location is not None:
            click(211, 432)
            return True
    return False


def check_if_in_battle():
    references = ["1.png", "2.png", "3.png", "4.png", "5.png"]

    locations = find_references(
        screenshot=screenshot(),
        folder="check_if_in_battle",
        names=references,
        tolerance=0.97,
    )

    return bool(check_for_location(locations))


def check_if_in_a_clan(logger):
    # Method to check if the current account has a clan. starts and ends on clash main

    # starts and ends on clash main
    logger.change_status("Checking if in a clan")

    # should be on main
    if not check_if_on_clash_main_menu():
        logger.change_status("Not on main menu so cant run check_if_in_a_clan()")
        return "restart"

    # click profile
    open_profile_page()

    # get image array of flag where clan flag should be.
    iar = numpy.asarray(screenshot())
    pix_list = []
    for x_coord in range(82, 97):
        for y_coord in range(471, 481):
            this_pixel = iar[y_coord][x_coord]
            pix_list.append(this_pixel)

    # if any of these pixels are NOT grey, we ARE in a clan. Else return False
    is_in_a_clan = False
    for pix in pix_list:
        if not pixel_is_equal(pix, [50, 50, 50], tol=15):
            # print("Found a pixel that indicates we are in a clan")
            is_in_a_clan = True
    if not is_in_a_clan:
        print("Found no pixels that indicate we are in a clan")

    # return to main after getting this information
    logger.change_status("Returning to main menu")
    click(363, 93)
    wait_for_clash_main_menu(logger)

    return is_in_a_clan


def get_to_account(logger, account_number):
    # Method to change account to the given account number using the supercell
    # ID login screen in the options menu in the clash main menu
    # Account number is ints 0-3 for the first 4 accounts
    logger.change_status(f"Switching accounts to account number {str(account_number)}")

    # open settings
    print("Opening settings tab from clash main to get to account switch")
    get_to_clash_main_settings_page()

    # click switch accounts
    print("Clicking the switch accounts button.")
    get_to_ssid_switch_page()

    print("getting to then clicking the appropriate account")

    if account_number == 0:
        click(155, 350)

    elif account_number == 1:
        click(190, 420)

    elif account_number == 2:
        click(230, 510)

    elif account_number == 3:
        click(230, 595)

    elif account_number == 4:
        # scroll then click
        scroll_down_fast()
        click(170, 640)

    elif account_number == 5:
        # scroll then click
        for _ in range(4):
            scroll_down_fast()
            time.sleep(0.5)
        click(230, 585)

    elif account_number == 6:
        # scroll then click
        for _ in range(7):
            scroll_down_fast()
            time.sleep(0.5)
        click(240, 550)

    elif account_number == 7:
        # scroll then click
        for _ in range(7):
            scroll_down_fast()
            time.sleep(0.5)

        click(230, 625)

    if wait_for_clash_main_menu(logger) == "restart":
        logger.change_status("Failed waiting for clash main")
        return "restart"

    logger.change_status(
        "Successful account switch. Incrementing account switch counter."
    )
    logger.add_account_switch()

    handle_new_challenge(logger)
    handle_special_offer(logger)
    handle_card_mastery_notification()
    time.sleep(1)
    return None


def handle_new_challenge(logger):
    # Method to handle a new challenge notification obstructing the bot
    logger.change_status("Handling new challenge notification")
    click(376, 639)
    time.sleep(0.33)
    click(196, 633)
    time.sleep(0.33)

    if check_if_on_trophy_progession_rewards_page():
        logger.change_status(
            "Handling the possibility of trophy progession rewards page obstructing the bot."
        )
        click(212, 633)


def handle_special_offer(logger):
    # Method to handle a special offer notification obstructing the bot
    logger.change_status("Handling special offer notification")
    click(35, 633)
    time.sleep(0.33)
    click(242, 633)
    time.sleep(0.33)

    if check_if_on_trophy_progession_rewards_page():
        click(212, 633)
        time.sleep(0.5)


def start_2v2(logger):
    # Method to start a 2v2 quickmatch through the party mode through the
    # clash main menu
    logger.change_status("Initiating 2v2 match from main menu")

    # if not on clash main at this point then this failed
    if not check_if_on_clash_main_menu():
        print("Not on clash main so cant run start_2v2()")
        return "restart"

    # getting to party tab
    print("Clicking options hamburber icon in clash main to get to party mode")
    get_to_clash_main_settings_page()

    print("getting to party mode page")
    get_to_party_mode_page_from_settings_page()

    if find_and_click_2v2_quickmatch_button(logger) == "restart":
        logger.change_status("failed to find 2v2 quickmatch button")
        return "restart"

    check_for_reward_limit()
    return None


def find_and_click_2v2_quickmatch_button(logger):
    # method to find and click the 2v2 quickmatch button in the party mode menu
    # starts in the party mode
    # ends when loading a match
    # logger.change_status("Finding and clicking 2v2 quickmatch button")
    # repeatedly scroll down until we find coords for the 2v2 quickmatch button
    origin = pyautogui.position()
    coords = None
    loops = 0
    pyautogui.moveTo(200, 200)
    time.sleep(1)
    while coords is None:
        loops += 1
        if loops > 20:
            logger.change_status("Could not find 2v2 quickmatch button, restarting")
            return "restart"
        scroll_down()
        time.sleep(1)
        coords = find_2v2_quick_match_button()
    time.sleep(0.33)
    # once we find the coords, click them
    print("Found 2v2 quickmatch button, clicking it")
    click(coords[0], coords[1])
    pyautogui.moveTo(origin[0], origin[1])
    logger.change_status("Done queueing a 2v2 quickmatch")


def wait_for_battle_start(logger):
    # Method to wait for a the loading sequence of a battle to finish

    logger.change_status("Waiting for battle start. . .")

    start_time = time.time()

    wait_time = 60

    while not check_if_in_battle_with_delay():
        if time.time() - start_time > wait_time:
            logger.change_status(f"Waited longer than {wait_time} sec for a fight")
            return "restart"


def check_if_pixels_indicate_in_battle():
    references = ["1.png", "2.png", "3.png", "4.png", "5.png"]

    locations = find_references(
        screenshot=screenshot(),
        folder="check_if_in_battle",
        names=references,
        tolerance=0.97,
    )

    if check_for_location(locations):
        return True


def check_if_in_battle_with_delay():
    start_time = time.time()
    while time.time() - start_time < 3:
        if check_if_pixels_indicate_in_battle():
            return True
    return False
