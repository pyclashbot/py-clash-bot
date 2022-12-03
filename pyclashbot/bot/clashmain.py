import time

import numpy
from ahk import AHK

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

# page navigation methods
def wait_for_clash_main_menu(logger):
    logger.change_status("Waiting for clash main menu")
    waiting = not check_if_on_clash_main_menu()

    loops = 0
    while waiting:
        print("Still waiting for clash main")
        # loop count
        loops += 1
        if loops > 25:
            logger.change_status(
                "Looped through wait_for_clash_main_menu too many times"
            )
            return "restart"

        # wait 1 sec
        time.sleep(1)

        # click dead space
        click(32, 364)

        # check if stuck on trophy progression page
        if check_if_stuck_on_trophy_progression_page():
            print("Stuck on trophy progression page. Clicking out")
            time.sleep(2)
            click(210, 621)

        # check if still waiting
        waiting = not check_if_on_clash_main_menu()

    logger.change_status("Done waiting for clash main menu")


def get_to_card_page(logger):
    # Method to get to the card page on clash main from the clash main menu
    click(x=100, y=630)
    time.sleep(2)
    loops = 0
    while not check_if_on_first_card_page():
        print("still not on card page. Cycling")
        time.sleep(1)
        click(x=100, y=630)
        loops = loops + 1
        if loops > 10:
            logger.change_status("Couldn't make it to card page")
            return "restart"
        time.sleep(1)
    scroll_up_fast()
    # logger.change_status("Made it to card page")
    time.sleep(1)


def get_to_clash_main_from_clan_page(logger):
    print("getting to main from clan page")
    # Method to return to clash main menu from request page
    click(172, 612)
    time.sleep(3)
    on_main = check_for_gem_logo_on_main()
    loops = 0
    while not on_main:
        print("Still not on main page. Cycling")
        loops += 1
        if loops > 7:
            logger.change_status("Could not get to clash main from request page.")
            return "restart"
        click(208, 636)
        time.sleep(1)
        on_main = check_for_gem_logo_on_main()
    time.sleep(3)


def get_to_clan_page(logger):
    # method to get to clan chat page from clash main
    print("getting to clan chat page.")
    click(312, 629)
    time.sleep(3)
    on_clan_chat_page = check_if_on_clan_page()
    loops = 0
    while not on_clan_chat_page:
        print("Still not on clan chat page.")
        # handle war chest popup
        if check_for_war_loot_menu():
            print("Found war loot. handling it.")
            handle_war_loot_menu()

        # handling infinite loop
        loops += 1
        if loops > 7:
            logger.change_status("Could not get to clan page.")
            return "restart"

        # cycle page
        click(278, 631)
        time.sleep(1)

        # scroll down because page wont cycle otherwise idk why. dumb game
        scroll_down()
        time.sleep(1)

        # update on_clan_chat_page
        on_clan_chat_page = check_if_on_clan_page()


# detection methods
def check_if_stuck_on_trophy_progression_page():
    iar = numpy.asarray(screenshot())
    color = [85, 177, 255]
    pix_list = [
        # iar[620][225],
        iar[625][230],
        iar[630][238],
        iar[635][245],
    ]

    # for pix in pix_list:print(pix[0],pix[1],pix[2])

    return all(pixel_is_equal(pix, color, tol=45) for pix in pix_list)


def check_if_on_first_card_page():
    # Method to check if the elixer icon of your deck's AVG elixer exists when on the
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
        tolerance=0.97,
    )

    return check_for_location(locations)


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

    pix_list = [
        iar[46][402],
        iar[52][403],
        iar[48][410],
    ]
    color = [75, 180, 35]

    # print_pix_list(pix_list)

    for pix in pix_list:
        return bool(pixel_is_equal(pix, color, tol=45))


def check_for_blue_background_on_main():
    # Method to check if the clash main menu is on screen
    iar = numpy.array(screenshot())

    pix_list = [
        iar[350][3],
        iar[360][6],
        iar[368][7],
        iar[372][9],
    ]
    color = [9, 69, 119]

    for pix in pix_list:
        return bool(pixel_is_equal(pix, color, tol=45))


def check_for_gold_logo_on_main():
    # Method to check if the clash main menu is on screen
    iar = numpy.array(screenshot())

    pix_list = [
        iar[48][299],
        iar[52][300],
        iar[44][302],
        iar[49][297],
    ]
    color = [201, 177, 56]

    # print_pix_list(pix_list)

    for pix in pix_list:
        return bool(pixel_is_equal(pix, color, tol=85))


def check_for_friends_logo_on_main():
    # Method to check if the clash main menu is on screen
    iar = numpy.array(screenshot())

    pix_list = [
        iar[90][269],
        iar[105][265],
        iar[103][272],
        iar[89][270],
        iar[107][266],
    ]
    color = [177, 228, 252]

    # print_pix_list(pix_list)

    # pixel check
    for pix in pix_list:
        return bool(pixel_is_equal(pix, color, tol=65))
    return False


def check_if_on_clash_main_menu():
    if not check_for_gem_logo_on_main():
        # print("gem fail")
        return False

    if not check_for_blue_background_on_main():
        # print("blue fail")
        return False

    if not check_for_friends_logo_on_main():
        # print("friends logo")
        return False

    if not check_for_gold_logo_on_main():
        # print("gold logo")
        return False
    return True


def check_if_on_clan_page():
    # Method to check if we're on the clan chat page

    iar = numpy.array(screenshot())

    pix_list = [
        iar[570][216],
        iar[575][149],
        iar[557][150],
        iar[575][215],
    ]
    color = [183, 105, 253]
    return all((pixel_is_equal(pix, color, tol=45)) for pix in pix_list)


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
        "12.png",
        "13.png",
        "14.png",
        "15.png",
        "16.png",
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.90,
    )

    return any(location is not None for location in locations)


def check_if_stuck_on_war_final_results_page():
    iar = numpy.asarray(screenshot())
    pix_list = [
        iar[575][235],
        iar[567][245],
        iar[575][255],
    ]

    return all(pixel_is_equal([180, 96, 253], pix, tol=45) for pix in pix_list)


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
        "20.png",
        "21.png",
        "22.png",
    ]

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97,
    )

    coord = get_first_location(locations)
    return None if coord is None else [coord[1] + 200, coord[0] + 50]


def check_for_reward_limit():
    # Method to check for the reward limit popup notification and close it

    references = ["1.png", "2.png", "3.png", "4.png", "5.png"]

    locations = find_references(
        screenshot=screenshot(), folder="reward_limit", names=references, tolerance=0.97
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


def check_for_war_loot_menu():
    iar = numpy.asarray(screenshot())

    pix_list = [
        iar[414][210],
        iar[418][217],
        iar[423][227],
        iar[427][237],
    ]
    color = [255, 190, 48]

    return all(pixel_is_equal(color, pix, tol=45) for pix in pix_list)


# interaction methods


def handle_puzzleroyale_popup(logger):
    # Method to handle puzzleroyale popup
    if look_for_puzzleroyale_popup():
        logger.change_status("Handling puzzle royale popup")
        click(366, 121)
        time.sleep(3)


def check_if_in_a_clan(logger):
    # Method to check if the current account has a clan. starts and ends on clash main

    # starts and ends on clash main
    logger.change_status("Checking if in a clan")

    # should be on main
    if not check_if_on_clash_main_menu():
        logger.change_status("Not on main menu so cant run check_if_in_a_clan()")
        return "restart"

    # click profile
    click(100, 130)
    time.sleep(3)

    # get image array of flag where clan flag should be.
    iar = numpy.asarray(screenshot())
    pix_list = []
    for x_coord in range(82, 97):
        for y_coord in range(471, 481):
            this_pixel = iar[y_coord][x_coord]
            pix_list.append(this_pixel)

    # print this pixel list
    # print_pix_list(pix_list)

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

    time.sleep(2)

    logger.change_status(
        f"Switching accounts to account number {str(account_number)}, (0-3)"
    )

    # open settings
    print("Opening settings butting from clash main to get to account switch")
    click(x=364, y=99)
    time.sleep(1)

    # click switch accounts
    print("Clicking the switch accounts button.")
    click(200, 460)
    time.sleep(3)

    print("getting to then clicking the appropriate account")

    if account_number == 0:
        click(155, 350)

    if account_number == 1:
        click(190, 420)

    if account_number == 2:
        click(230, 510)

    if account_number == 3:
        click(230, 595)

    if account_number == 4:
        # scroll then click
        scroll_down_fast()
        time.sleep(1)
        click(170, 640)

    if account_number == 5:
        # scroll then click
        for _ in range(4):
            scroll_down_fast()
            time.sleep(1)
        time.sleep(1)
        click(230, 585)

    if account_number == 6:
        # scroll then click
        for _ in range(7):
            scroll_down_fast()
            time.sleep(1)
        time.sleep(1)
        click(240, 550)

    if account_number == 7:
        # scroll then click
        for _ in range(7):
            scroll_down_fast()
            time.sleep(1)
        time.sleep(1)
        click(230, 625)

    for n in range(10):
        logger.change_status(f"Manual wait time for clash main menu to load: {n}")
        time.sleep(1)

    if wait_for_clash_main_menu(logger) == "restart":
        logger.change_status("Failed waiting for clash main")
        return "restart"

    logger.change_status(
        "Successful account switch. Incrementing account switch counter."
    )
    logger.add_account_switch()

    # handling the various things notifications and such that need to be
    # cleared before bot can get going
    # time.sleep(0.5)
    # handle_gold_rush_event(logger)
    time.sleep(0.5)
    handle_new_challenge(logger)
    time.sleep(0.5)
    handle_special_offer(logger)
    time.sleep(0.5)
    handle_card_mastery_notification()
    time.sleep(0.5)
    return None


def handle_new_challenge(logger):
    # Method to handle a new challenge notification obstructing the bot
    logger.change_status("Handling new challenge notification")
    click(376, 639)
    time.sleep(1)
    click(196, 633)
    time.sleep(1)
    if check_if_on_trophy_progession_rewards_page():
        logger.change_status(
            "Handling the possibility of trophy progession rewards page obstructing the bot."
        )
        click(212, 633)


def handle_special_offer(logger):
    # Method to handle a special offer notification obstructing the bot
    logger.change_status("Handling special offer notification")
    click(35, 633)
    time.sleep(1)
    click(242, 633)
    time.sleep(1)
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
    click(365, 108)
    time.sleep(1)
    print("Clicking party mode in the options list")
    click(263, 248)
    time.sleep(1)

    if find_and_click_2v2_quickmatch_button(logger) == "restart":
        logger.change_status("failed to find 2v2 quickmatch button")
        return "restart"

    check_for_reward_limit()
    return None


def open_chests(logger):
    logger.change_status("Opening chests")

    # check which chests exist
    existing_chests_array = check_for_chests()

    # identify locations of chests
    chest_coord_list = [
        [78, 554],
        [162, 549],
        [263, 541],
        [349, 551],
    ]

    # for each chest that exists
    # click current chest
    # check if unlock appears
    # if unlock appears unlock the chest
    # else click dead space 15 times to skip thru rewards
    # then close this chest menu.
    index = 0
    for chest in existing_chests_array:
        if chest:
            logger.change_status("Handling chest number: " + str(index + 1))
            # click chest
            chest_coord = chest_coord_list[index]
            click(chest_coord[0], chest_coord[1])
            time.sleep(1)

            if check_if_unlock_chest_button_exists():
                print("Unlocked a chest", index + 1)
                logger.add_chest_unlocked()
                click(210, 465)
            else:
                print("Skipping through rewards for chest index: ", index + 1)
                click(20, 556, clicks=15, interval=0.33)

            # close chest menu
            print("Closing chest index", index + 1)
            click(20, 556)

        index += 1

    logger.change_status("Done collecting chests.")


def check_for_chests():
    # returns an array of 4 bools each representing a chest slot
    # true means hsa chest, false means no chest
    return_bool_list = []

    # make a list of 4 pixels each representing a chest
    iar = numpy.asarray(screenshot())
    pix_list = [
        iar[572][92],
        iar[567][155],
        iar[568][269],
        iar[566][329],
    ]

    # print this pixel list
    # print_pix_list(pix_list)

    for pix in pix_list:
        if pixel_is_equal(pix, [27, 110, 146], tol=25):
            return_bool_list.append(False)
        else:
            return_bool_list.append(True)

    # print return_bool_list
    print("chest_exists_bool_list", return_bool_list)

    # return this list
    return return_bool_list


def find_and_click_2v2_quickmatch_button(logger):
    # method to find and click the 2v2 quickmatch button in the party mode menu
    # starts in the party mode
    # ends when loading a match
    # logger.change_status("Finding and clicking 2v2 quickmatch button")
    # repeatedly scroll down until we find coords for the 2v2 quickmatch button
    coords = None
    loops = 0
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
    click(coords[0], coords[1])
    logger.change_status("Done queueing a 2v2 quickmatch")


def wait_for_battle_start(logger):
    # Method to wait for a the loading sequence of a battle to finish

    logger.change_status("Waiting for battle start. . .")
    in_battle = False
    loops = 0

    while not in_battle:
        if check_if_in_battle_with_delay():
            in_battle = True
        click(100, 100)
        time.sleep(0.25)
        loops += 1
        logger.change_status(str(f"Waiting for battle start... {loops}"))
        if loops > 120:
            logger.change_status("Waited longer than 30 sec for a fight")
            return "restart"


def check_if_in_battle_with_delay():
    # Method to check if the bot is in a battle in the given moment

    for _ in range(5):
        references = ["1.png", "2.png", "3.png", "4.png", "5.png"]

        locations = find_references(
            screenshot=screenshot(),
            folder="check_if_in_battle",
            names=references,
            tolerance=0.97,
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


def handle_war_loot_menu():
    # open chest
    click(205, 410)
    time.sleep(1)
    # click dead space to skip thru chest
    for _ in range(15):
        click(20, 440)
        time.sleep(0.1)

    # click OK
    click(215, 550)
    time.sleep(0.5)

    scroll_down()


def handle_stuck_on_war_final_results_page():
    if check_if_stuck_on_war_final_results_page():
        click(215, 565)
        time.sleep(1)


# methods to sort
def verify_ssid_input(logger, inputted_ssid_max):
    logger.change_status("Verifying SSID input")
    # should be on main
    if not check_if_on_clash_main_menu():
        print("Not on clash main so cant run verify_ssid_input()")
        return "restart"

    # get to accounts list.
    #   If get_to_switch_accounts_tab fails then return "restart"
    #   If switch accounts button is not there, AND ssid_max is 1, then return "pass".
    #   If switch accounts button is not there, AND ssid_max is not 1, then return "failure".
    #   If switch accounts button is there, then continue.
    logger.change_status("Attempting to get to accounts list")
    get_to_accounts_list_return = get_to_switch_accounts_tab()
    if get_to_accounts_list_return == "restart":
        print("Failure with get_to_switch_accounts_tab()")
        return "restart"
    elif get_to_accounts_list_return == "no other accounts":
        if inputted_ssid_max == 1:
            print("No other accouts, but ssid_max is 1 so passing.")
            wait_for_clash_main_menu(logger)
            return "pass"
        else:
            print("No other accounts, but ssid_max is not 1 so failing.")
            wait_for_clash_main_menu(logger)
            return "failure"

    logger.change_status("Counting the amount of availbale accounts.")
    # once on accoutns list, count accounts
    account_count = count_ssid_accounts_on_switch_ssid_page()

    # check against inputted_ssid_max
    if account_count != inputted_ssid_max:
        logger.change_status(
            "The amount of SSIDs the bot counted is not the same as the inputted ssid_max."
        )
        # close menu
        click(390, 85)
        time.sleep(3)
        wait_for_clash_main_menu(logger)
        return "failure"
    else:
        logger.change_status(
            "The amount of SSIDs the bot counted is the same as the inputted ssid_max."
        )
        # close menu
        click(390, 85)
        time.sleep(3)
        wait_for_clash_main_menu(logger)
        return "pass"


def count_ssid_accounts_on_switch_ssid_page():
    # coord list of accounts icons
    account_coord_list = [
        [373, 336],
        [375, 422],
        [373, 503],
        [375, 590],
    ]

    positive_list = []
    # check which trophy symbols from which accounts are visible
    iar = numpy.asarray(screenshot())
    for index in range(4):
        this_coord = account_coord_list[index]
        this_pixel = iar[this_coord[1]][this_coord[0]]
        if pixel_is_equal(this_pixel, [255, 175, 90], tol=75):
            positive_list.append(True)
        else:
            positive_list.append(False)

    # if all 4 are true return 4
    if all(positive_list):
        return 4

    # if all 3 are true return 3
    if all(positive_list[0:3]):
        return 3

    # if all 2 are true return 2
    if all(positive_list[0:2]):
        return 2

    # if all 1 are true return 1
    if all(positive_list[0:1]):
        return 1

    # if none are true return 0
    return 0


def get_to_switch_accounts_tab():
    # if not on main then failure
    if not check_if_on_clash_main_menu():
        print("Not on main so cant count accounts.")
        return "restart"

    # click hamburger icon in top right on clash main for options
    click(365, 95)
    time.sleep(1)

    # IMPLEMENT CHECK IF SWITHC ACCOUTNS BUTTON IS THERE
    if find_switch_accouts_button() is None:
        print("No switch accoutns button")
        return "no other accounts"

    # click switch accounts button
    click(200, 455)
    time.sleep(3)


def find_switch_accouts_button():
    current_image = screenshot()
    reference_folder = "find_switch_accouts_button"

    references = make_reference_image_list(
        get_file_count(
            "find_switch_accouts_button",
        )
    )

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97,
    )

    coord = get_first_location(locations)
    return None if coord is None else [coord[1], coord[0]]


def handle_war_chest_obstruction(logger):
    if check_for_war_chest_obstruction():
        logger.change_status("Opening war chest.")
        open_war_chest(logger)


def check_for_war_chest_obstruction():
    current_image = screenshot()
    reference_folder = "check_for_war_chest_obstruction"

    references = make_reference_image_list(
        get_file_count(
            "check_for_war_chest_obstruction",
        )
    )

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97,
    )

    return check_for_location(locations)


def open_war_chest(logger):
    # click chset
    logger.change_status("Opening the war chest. . .")
    click(210, 440)
    time.sleep(1)

    # open it
    logger.change_status("Skipping through rewards. . .")
    for n in range(15):
        click(10, 220)
    time.sleep(3)

    # Click OK on war results page popup
    print("Clicking OK on war results page popup")
    click(205, 555)
    for n in range(5):
        print(
            "Manual wait time after closing war results page popup after opening war chest:",
            n,
        )
        time.sleep(1)

    # increment logger
    print("Incrementing war chest collection counter.")
    logger.add_war_chest_collection()


def get_to_clash_main_from_card_page(logger):
    # logger.change_status("Getting to Clash main menu from card page")

    # get to card page
    click(240, 627)
    time.sleep(3)

    loops = 0
    while not check_if_on_clash_main_menu():
        if loops > 15:
            logger.change_status("Couldn't get to Clash main menu from card page")
            return "restart"

        # if not on menu at this point cycle the screen off trophy progression page and back on
        click(212, 637)
        time.sleep(1)
