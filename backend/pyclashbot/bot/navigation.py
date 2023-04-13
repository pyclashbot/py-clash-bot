import random
import time

import numpy

from pyclashbot.detection.image_rec import (
    check_for_location,
    find_references,
    get_first_location,
    pixel_is_equal,
)
from pyclashbot.memu.client import (
    click,
    get_file_count,
    make_reference_image_list,
    screenshot,
    scroll_down,
    scroll_up,
    scroll_up_fast,
    scroll_up_fast_on_left_side_of_screen,
)

"""methods that have to do with navigating the game's menus"""


####Main navigation methods
def get_to_card_page(logger):
    """main method for getting to the card page
    args:
        logger: logger object
    returns:
        restart state if failed, None if successful
    """

    # click card page
    logger.change_status("Getting to card collection tab...")
    click(105, 630)
    if wait_for_card_page(logger) == "fail":
        logger.change_status("failed waiting for card page")
        return "restart"

    # get to battle deck page
    logger.change_status("Getting to battle deck page...")
    if get_to_battle_deck_page(logger) == "restart":
        return "restart"


def get_to_war_page_from_main(logger):
    """main method for getting to the war page
    args:
        logger: logger object
    returns:
        restart state if failed, None if successful
    """
    logger.change_status("getting to war page from clash main.")
    if check_if_on_war_page():
        return None

    click(315, 635)
    time.sleep(3)

    loops = 0
    while not check_if_on_war_page():
        logger.change_status("still not on war page. Cycling.")
        handle_war_chest_obstruction(logger)

        # check if stuck on trophy progression page
        if check_if_stuck_on_trophy_progression_page():
            logger.change_status("Stuck on trophy progression page. Clicking out")
            click(210, 621)
            time.sleep(2)
            get_to_war_page_from_main(logger)

        loops += 1
        if loops > 20:
            logger.change_status(
                "failure getting to war page using get_to_war_page_from_main()"
            )
            return "restart"
        click(280, 620)

        if random.randint(1, 2) == 2:
            # origin = pyautogui.position()
            # pyautogui.moveTo(300, 300)
            time.sleep(1)
            scroll_up()
            # pyautogui.moveTo(origin[0], origin[1])

        time.sleep(1)
    return None


def get_to_clash_main_from_shop(logger):
    """main method for getting to the clash main from the shop page
    args:
        logger: logger object
    returns:
        restart state if failed, None if successful
    """

    logger.change_status("Getting to clash main from shop.")
    # click main
    click(240, 630)
    time.sleep(2)

    loops = 0
    while not check_if_on_clash_main_menu():
        loops += 1
        if loops > 20:
            logger.change_status(
                "Looped through get_to_clash_main_from_shop() too many times. Restarting"
            )
            return "restart"
        click(200, 620)
        time.sleep(2)

    logger.change_status("Made it to clash main from shop.")


def get_to_shop_page_from_main(logger):
    """main method for getting to the shop page
    args:
        logger: logger object
    returns:
        restart state if failed, None if successful
    """

    logger.change_status("Getting to shop from main.")

    # check if on main
    if not check_if_on_clash_main_menu():
        logger.change_status(
            "not no clash main so cant run get_to_shop_page_from_main()"
        )
        return "restart"

    # click shop icon
    click(35, 636)
    time.sleep(1)

    # check if on shop
    if not check_if_on_shop_page_with_delay(logger):
        logger.change_status("Failed to get to shop page.")
        return "restart"

    logger.change_status("Made it to shop from main.")


def get_to_clash_main_from_card_page(logger):
    """main method for getting to the clash main menu from the card page
    args:
        logger: logger object
    returns:
        restart state if failed, None if successful
    """

    logger.change_status("Getting to Clash main menu from card page")

    # get to card page
    click(240, 627)
    time.sleep(3)

    loops = 0
    while not check_if_on_clash_main_menu():
        loops += 1
        if loops > 15:
            logger.change_status("Couldn't get to Clash main menu from card page")
            return "restart"

        # if not on menu at this point cycle the screen off trophy progression page and back on
        click(212, 637)
        time.sleep(1)


def get_to_clash_main_from_clan_page(logger):
    """main method for getting to the clash main menu from the clan page
    args:
        logger: logger object
    returns:
        restart state if failed, None if successful
    """

    logger.change_status("getting to main from clan page")
    # Method to return to clash main menu from request page
    click(172, 612)
    time.sleep(3)
    on_main = check_if_on_clash_main_menu()
    loops = 0
    while not on_main:
        logger.change_status("Still not on main page. Cycling")
        loops += 1
        if loops > 7:
            logger.change_status("Could not get to clash main from request page.")
            return "restart"
        click(208, 636)
        time.sleep(1)
        on_main = check_if_on_clash_main_menu()
    logger.change_status("made it to clash main.")
    time.sleep(3)


def get_to_clan_page(logger):
    """main method for getting to the clan page
    args:
        logger: logger object
    returns:
        restart state if failed, None if successful
    """
    # method to get to clan chat page from clash main
    logger.change_status("getting to clan chat page.")
    click(312, 629)
    time.sleep(3)
    on_clan_chat_page = check_if_on_clan_page()
    loops = 0
    while not on_clan_chat_page:
        logger.change_status("Still not on clan chat page.")

        # handle other war chest popup
        handle_war_loot_chest(logger)

        # handle war chest popup
        if check_for_war_loot_menu():
            logger.change_status("Found war loot. handling it.")
            handle_war_loot_menu(logger)

        # handle final results popup
        if check_for_final_results_popup(logger):
            handle_final_results_popup(logger)

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


def open_activity_log(logger):
    """main method for getting to the activity log menu
    args:
    """

    logger.change_status("Opening activity log")
    click(x=360, y=99)
    time.sleep(1)

    click(x=255, y=75)
    time.sleep(1)


def leave_end_battle_window(logger):
    """leave_end_battle_window checks which end screen case is (there are two),clicks the appropriate button to leave the end battle screen, then waits for clash main.
    args:
        logger: logger object from logger class initialized in main
    returns:
        "restart" if it fails to get to clash main, else None
    """
    logger.change_status("Leaving this 2v2 battle. . .")

    # if end screen condition 1 (exit in bottom left)
    if check_if_end_screen_is_exit_bottom_left():
        logger.change_status("Leaving end battle (condition 1)")
        click(79, 625)
        time.sleep(6)
        click(x=173, y=631)

        return None

    # if end screen condition 2 (OK in bottom middle)
    if check_if_end_screen_is_ok_bottom_middle():
        logger.change_status("Leaving end battle (condition 2)")
        click(206, 594)
        time.sleep(6)
        click(x=173, y=631)

        return None

    manual_wait_time = 10
    logger.change_status(f"Manual wait time of {manual_wait_time} seconds")
    time.sleep(manual_wait_time)

    # click clash main icon in bottom middle of page icon list
    logger.change_status("Returning to clash main from events page")
    click(183, 629)

    if wait_for_clash_main_menu(logger) == "restart":
        logger.change_status("Waited too long for clash main")
        return "restart"
    return None


def handle_war_loot_chest(logger):
    """method for handling the possbiility of a war loot chest in the way of the bot
    args:
        None
    returns:
        None
    """

    if check_for_war_loot_chest():
        logger.change_status("Found a war chest in the way...")
        # click open chest
        logger.change_status("Clicking open war chest..")
        click(205, 440)
        time.sleep(1)

        # skip thru chest
        logger.change_status("Skipping thru war chest rewards...")
        click(20, 450, clicks=20, interval=1)
        time.sleep(1)

        logger.change_status("Done handling war chest...")


def handle_card_mastery_notification():
    """Method to handle the possibility of a card mastery notification obstructing the bot
    args:
        None
    returns:
        None
    """
    # Method to handle the possibility of a card mastery notification
    # obstructing the bot
    click(107, 623)
    time.sleep(1)

    click(240, 630)
    time.sleep(0.33)


def handle_war_loot_menu(logger):
    """Method to handle the possibility of a war_loot_menu page obstructing the bot
    args:
        None
    returns:
        None
    """
    # open chest
    logger.change_status("Opening war chest")
    click(205, 420)
    time.sleep(1)

    # click dead space to skip thru chest
    logger.change_status("Skipping thru war chest rewards")
    click(20, 440, clicks=20, interval=0.1)
    time.sleep(1)


def handle_stuck_on_war_final_results_page():
    """handling the possiblity of the bot getting stuck on the war final results page
    args:
        None
    returns:
        None
    """

    if check_if_stuck_on_war_final_results_page():
        click(215, 565)
        time.sleep(1)


def handle_final_results_popup(logger):
    """method for handling the final results popup
    args:
        None
    returns:
        None
    """

    logger.change_status("Doing final results popup hanlding.")

    # click OK
    click(220, 555)
    time.sleep(5)


def open_war_chest(logger):
    """method for opening a war chest that is obstructing the bot
    args:
        logger: logger object from logger class initialized in main
    returns:
        None
    """

    # click chest
    logger.change_status("Opening the war chest. . .")
    click(210, 440)
    time.sleep(1)

    # open it
    logger.change_status("Skipping through rewards. . .")
    click(10, 220, clicks=20, interval=1)
    time.sleep(3)

    # Click OK on war results page popup
    logger.change_status("Clicking OK on war results page popup")
    click(205, 555)
    for n in range(5):
        logger.change_status(
            "Manual wait time after closing war results page popup after opening war chest:",
            n,
        )
        time.sleep(1)

    # increment logger
    logger.change_status("Incrementing war chest collection counter.")
    logger.add_war_chest_collection()


def handle_war_chest_obstruction(logger):
    """method for handling the possiblity of a war chest obstructing the bot
    args:
        logger: logger object from logger class initialized in main
    returns:
        None
    """
    if check_for_war_chest_obstruction():
        logger.change_status("Opening war chest.")
        open_war_chest(logger)


def check_if_stuck_on_war_final_results_page():
    """method for scanning for pixels that indicate the bot is stuck on the war final results page
    args:
        None
    returns:
        bool,True if stuck on war final results page, else False
    """

    iar = numpy.asarray(screenshot())
    pix_list = [
        iar[575][235],
        iar[567][245],
        iar[575][255],
    ]

    return all(pixel_is_equal([180, 96, 253], pix, tol=45) for pix in pix_list)


def check_if_on_first_card_page():
    """method for checking if the bot is on the first card page
    args:
        None
    returns:
        bool, True if on first card page, else False
    """

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


def check_if_on_clash_main_menu():
    """method for checking if the bot is on the clash main menu
    args:
        None
    returns:
        bool, True if on clash main menu, else False
    """

    if not check_for_gem_logo_on_main():
        return False

    if not check_for_friends_logo_on_main():
        return False

    if not check_for_gold_logo_on_main():
        return False
    return True


def check_if_on_war_page():
    """method for scanning for pixels that indicate the bot is on the war page
    args:
        None
    returns:
        bool, True if on war page, else False
    """

    iar = numpy.asarray(screenshot())
    pix_list = [
        iar[73][43],
        iar[83][43],
    ]
    color = [232, 225, 236]
    return all(pixel_is_equal(pix, color, tol=45) for pix in pix_list)


def check_for_gem_logo_on_main():
    """method for scanning for pixels that indicate the bot is on the clash main menu by checking for the gem logo
    args:
        None
    returns:
        bool, True if on gem logo exists, else False
    """

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
    """method for scanning for pixels that indicate the bot is on the clash main menu by checking for the blue backgound
    args:
        None
    returns:
        bool, True if on blue background exists, else False
    """

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
    """method for scanning for pixels that indicate the bot is on the clash main menu by checking for the gold logo
    args:
        None
    returns:
        bool, True if on gold logo exists, else False
    """
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
    """method for scanning for pixels that indicate the bot is on the clash main menu by checking for the friends logo
    args:
        None
    returns:
        bool, True if on gem friends exists, else False
    """

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


def check_for_war_loot_chest():
    """method for scanning for images that indicate a war_loot_chest is on screen
    args:
        None
    returns:
        bool, True if on gem logo exists, else False
    """
    current_image = screenshot()
    reference_folder = "check_for_war_loot_chest"

    references = make_reference_image_list(
        get_file_count(
            "check_for_war_loot_chest",
        )
    )

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97,
    )

    return check_for_location(locations)


def check_if_on_clan_page():
    """method for scanning pixels to check if they indicate the bot is on the clan page
    args:
        None
    returns:
        bool, True if on clan page, else False"""

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


def check_for_war_loot_menu():
    """method for scanning pixels that indicate if the war loot menu is on screen
    args:
        None
    returns:
        bool, True if on war loot menu, else False
    """

    iar = numpy.asarray(screenshot())

    pix_list = [
        iar[414][210],
        iar[418][217],
        iar[423][227],
        iar[427][237],
    ]
    color = [255, 190, 48]

    return all(pixel_is_equal(color, pix, tol=45) for pix in pix_list)


def check_for_final_results_popup(logger):
    """method for scanning pixels that indicate if the final results popup is on screen
    args:
        None
    returns:
        bool, True if on final results popup, else False
    """

    iar = numpy.asarray(screenshot())
    pix_list = [
        iar[555][170],
        iar[565][180],
        iar[569][187],
        iar[575][195],
    ]
    for pix in pix_list:
        if not pixel_is_equal(pix, [181, 96, 253], tol=45):
            return False
    logger.change_status("Final results popup detected.")
    return True


def check_if_on_shop_page_with_delay(logger):
    """method for checking if the bot is on the shop page with a delay
    args:
        None
    returns:
        bool, True if on shop page, else False
    """
    start_time = time.time()
    while time.time() - start_time < 3:
        logger.change_status("looping thru")
        if check_if_on_shop_page():
            logger.change_status("made it")
            return True
        time.sleep(0.5)
    return False


def check_if_on_shop_page():
    """method for checking if the bot is on the shop page
    args:
        None
    returns:
        bool, True if on shop page, else False
    """
    iar = numpy.asarray(screenshot())

    pix_list = [
        iar[624][71],
        iar[636][55],
        iar[623][85],
        iar[625][71],
    ]
    color_list = [
        [103, 234, 56],
        [56, 85, 101],
        [247, 194, 75],
        [103, 236, 56],
    ]
    for n in range(4):
        this_pixel = pix_list[n]
        this_color = color_list[n]
        if not pixel_is_equal(this_pixel, this_color, tol=35):
            return False
    return True


def find_switch_accouts_button():
    """method to locate the coordinates of the switch accounts button
    args:
        None
    returns:
        list, coordinates of the switch accounts button
    """

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


def check_for_war_chest_obstruction():
    """method for scanning for images that indicate a war_chest_obstruction is on screen
    args:
        None
    returns:
        bool, True if on gem logo exists, else False
    """
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


def check_if_end_screen_is_ok_bottom_middle():
    """check_if_end_screen_is_ok_bottom_middle checks for one of the end of battle screen cases (OK in bottom middle)
    returns:
        bool: True if pixels indicate this is the case, else False
    """

    iar = numpy.array(screenshot())
    # (210,589)
    pix_list = [
        iar[591][234],
        iar[595][178],
        iar[588][192],
        iar[591][233],
    ]
    color = [78, 175, 255]
    return all((pixel_is_equal(pix, color, tol=45)) for pix in pix_list)


def check_if_end_screen_is_exit_bottom_left():
    """check_if_end_screen_is_exit_bottom_left checks for one of the end of battle screen cases (OK in bottom left)
    returns:
        bool: True if pixels indicate this is the case, else False
    """

    iar = numpy.array(screenshot())
    pix_list = [
        iar[638][57],
        iar[640][110],
        iar[622][59],
        iar[621][110],
    ]
    color = [87, 186, 255]
    return all((pixel_is_equal(pix, color, tol=45)) for pix in pix_list)


def check_if_stuck_on_trophy_progression_page():
    """method to scan for pixels that indicate the bot is stuck on the trophy progression page
    args:
        None
    returns:
        bool, True if stuck on trophy progression page, else False
    """

    iar = numpy.asarray(screenshot())
    color = [85, 177, 255]
    pix_list = [
        # iar[620][225],
        iar[625][230],
        iar[630][238],
        iar[635][245],
    ]

    return all(pixel_is_equal(pix, color, tol=45) for pix in pix_list)


def wait_for_clash_main_menu(logger):
    """method to wait for the clash main menu to appear
    args:
        logger: logger object
    returns:
        restart state if waited too long, else None
    """

    logger.change_status("Waiting for clash main menu")
    waiting = not check_if_on_clash_main_menu()

    start_time = time.time()

    loops = 0
    while waiting:
        logger.change_status("Still waiting for clash main")
        # loop count
        loops += 1

        wait_time = 60

        if time.time() - start_time > wait_time:
            logger.change_status(
                f"Waited more than {wait_time} sec for clashmain. restarting"
            )
            return "restart"

        # click dead space
        if loops % 5 == 0:
            click(32, 364)

        # check if stuck on trophy progression page
        if check_if_stuck_on_trophy_progression_page():
            logger.change_status("Stuck on trophy progression page. Clicking out")
            click(210, 621)
            time.sleep(1)

        # check if still waiting
        waiting = not check_if_on_clash_main_menu()

    logger.change_status("Done waiting for clash main menu")


#### TO SORT


def get_to_clash_main_settings_page():
    """method to get to the clash main settings page
    args:
        None
    returns:
        None
    """

    click(x=364, y=99)
    wait_for_clash_main_settings_page()


def check_if_on_clash_main_settings_page():
    """method to check if the bot is on the clash main settings page by scanning relevant pixels
    args:
        None
    returns:
        bool, True if on the clash main settings page, else False
    """

    iar = numpy.asarray(screenshot())

    battle_log_text_exists = False
    for x_coord in range(230, 250):
        this_pixel = iar[75][x_coord]
        if pixel_is_equal(this_pixel, [255, 255, 255], tol=35):
            battle_log_text_exists = True

    tournaments_button_exists = False
    for x_coord in range(185, 210):
        this_pixel = iar[287][x_coord]
        if pixel_is_equal(this_pixel, [95, 141, 51], tol=35):
            tournaments_button_exists = True

    if battle_log_text_exists and tournaments_button_exists:
        return True
    return False


def wait_for_clash_main_settings_page():
    """method for waiting for the calsh main settings page to appear
    args:
        None
    returns:
        None
    """
    while not check_if_on_clash_main_settings_page():
        pass


def wait_for_ssid_switch_page():
    """method for waiting for the ssid switch page to appear
    args:
        None
    returns:
        None
    """
    while not check_for_ssid_switch_page():
        pass


def get_to_ssid_switch_page():
    """method for getting to the ssid switch page (accounts switch page)
    args:
        None
    returns:
        None
    """

    click(200, 405)
    wait_for_ssid_switch_page()


def check_for_ssid_switch_page():
    """Method for scanning pixels that indicate whether or not the bot is on the ssid switch page
    args:
        None
    returns:
        bool, True if on the ssid switch page, else False
    """

    iar = numpy.asarray(screenshot())

    blue_background_color_exists = False
    for x_coord in range(30, 70):
        this_pixel = iar[110][x_coord]
        if pixel_is_equal(this_pixel, [50, 118, 182], tol=35):
            blue_background_color_exists = True

    switch_accounts_logo_exists = False
    for x_coord in range(150, 165):
        this_pixel = iar[265][x_coord]
        if pixel_is_equal(this_pixel, [47, 243, 198], tol=35):
            switch_accounts_logo_exists = True

    if switch_accounts_logo_exists and blue_background_color_exists:
        return True
    return False


def get_to_battlepass_rewards_page(logger):
    """method for getting the to battlepass rewards page
    args:
        None
    returns:
        None
    """

    click(315, 165)

    wait_for_battlepass_rewards_page(logger)


def check_for_battlepass_rewards_page():
    """method for checking if the bot is on the battlepass rewards page
    args:
        None
    returns:
        bool, True if on the battlepass rewards page, else False
    """

    iar = numpy.asarray(screenshot())

    boot_camp_text_exists = False
    for x_coord in range(150, 160):
        this_pixel = iar[72][x_coord]
        if pixel_is_equal(this_pixel, [255, 255, 255], tol=35):
            boot_camp_text_exists = True

    ok_button_exists = False
    for x_coord in range(177, 197):
        this_pixel = iar[638][x_coord]
        if pixel_is_equal(this_pixel, [78, 175, 255], tol=35):
            ok_button_exists = True

    if ok_button_exists and boot_camp_text_exists:
        return True
    return False


def wait_for_battlepass_rewards_page(logger):
    """method for waiting for the battlepass rewards page to appear
    args:
        None
    returns:
        None
    """

    while not check_for_battlepass_rewards_page():
        if random.randint(0, 1) == 1:
            click(20, 630)
        else:
            click(171, 333)
        if check_for_bonus_bank_popup_in_battlepass_page(logger):
            handle_bonus_bank_popup_in_battlepass_page(logger)


def check_for_card_mastery_page():
    """method to check if the bot is on the card mastery page by scanning relevant pixels
    args:
        None
    returns:
        bool, True if on the card mastery page, else False
    """

    iar = numpy.asarray(screenshot())

    card_masteries_text_exists = False
    for x_coord in range(150, 275):
        this_pixel = iar[135][x_coord]
        if pixel_is_equal(this_pixel, [255, 255, 255], tol=35):
            card_masteries_text_exists = True

    close_button_exists = False
    for x_coord in range(345, 365):
        this_pixel = iar[145][x_coord]
        if pixel_is_equal(this_pixel, [228, 24, 24], tol=35):
            close_button_exists = True

    if close_button_exists and card_masteries_text_exists:
        return True
    return False


def wait_card_mastery_page():
    """method for waiting for the card mastery page to appear
    args:
        None
    returns:
        None
    """
    while not check_for_card_mastery_page():
        pass


def get_to_card_mastery_page():
    """method for getting to the card mastery page
    args:
        None
    returns:
        None
    """
    click(257, 505)
    wait_card_mastery_page()


def check_if_profile_page_is_open():
    """method for checking for pixels that indicate whether or not the profile page is open
    args:
        None
    returns:
        bool, True if the profile page is open, else False
    """

    iar = numpy.asarray(screenshot())

    profile_page_crown_logo_exists = False
    for x_coord in range(180, 240):
        this_pixel = iar[80][x_coord]
        if pixel_is_equal(this_pixel, [255, 220, 0], tol=35):
            profile_page_crown_logo_exists = True

    close_button_exists = False
    for x_coord in range(350, 370):
        this_pixel = iar[90][x_coord]
        if pixel_is_equal(this_pixel, [253, 132, 133], tol=35):
            close_button_exists = True

    if profile_page_crown_logo_exists and close_button_exists:
        return True
    return False


def open_profile_page():
    """method for opening the profile page from the clash main menu
    args:
        None
    returns:
        None
    """
    click(100, 130)
    wait_for_profile_page()


def wait_for_profile_page():
    """method for waiting for the bot to arrive on the profile page
    args:
        None
    returns:
        None
    """
    while not check_if_profile_page_is_open():
        pass


def check_if_on_party_mode_page():
    """method to scan for pixels that indicate the bot is on the party mode page
    args:
        None
    returns:
        bool, True if on the party mode page, else False
    """

    iar = numpy.asarray(screenshot())

    party_title_text_exists = False
    for x_coord in range(180, 240):
        this_pixel = iar[140][x_coord]
        if pixel_is_equal(this_pixel, [255, 255, 255], tol=35):
            party_title_text_exists = True

    close_button_exists = False
    for x_coord in range(340, 365):
        this_pixel = iar[130][x_coord]
        if pixel_is_equal(this_pixel, [253, 132, 133], tol=35):
            close_button_exists = True

    if close_button_exists and party_title_text_exists:
        return True
    return False


def wait_for_party_mode_page():
    """method for waiting for the party mode page to load
    args:
        None
    returns:
        None
    """
    while not check_if_on_party_mode_page():
        pass


def get_to_party_mode_page_from_settings_page():
    """methbod to get to the party mode page from the settings page
    args:
        None
    returns:
        None
    """

    click(263, 248)
    wait_for_party_mode_page()


def wait_for_card_page(logger):
    """method for waiting for the bot to arrive on the card page
    args:
        None
    returns:
        fail if the bot times out waiting for the card page, else None
    """

    start_time = time.time()
    while not check_if_on_card_page():
        if time.time() - start_time > 10:
            logger.change_status("timed out waiting for card page")
            return "fail"


def check_if_on_card_page():
    """method to scan for pixels that indicate the bot is on the card page
    args:
        None
    returns:
        bool, True if on the card page, else False
    """

    iar = numpy.asarray(screenshot())

    left_arrow_exists = False
    for x_coord in range(85, 95):
        this_pixel = iar[635][x_coord]
        if pixel_is_equal(this_pixel, [137, 224, 255], tol=35):
            left_arrow_exists = True

    right_arrow_exists = False
    for x_coord in range(185, 195):
        this_pixel = iar[635][x_coord]
        if pixel_is_equal(this_pixel, [137, 224, 255], tol=35):
            right_arrow_exists = True

    collection_text_exists = False
    for x_coord in range(110, 170):
        this_pixel = iar[655][x_coord]
        if pixel_is_equal(this_pixel, [253, 253, 253], tol=35):
            collection_text_exists = True

    if collection_text_exists and right_arrow_exists and left_arrow_exists:
        return True
    return False


def check_if_on_battle_deck_page():
    """method scans for pixels that indicate the bot is on the battle deck page
    args:
        None
    returns:
        bool, True if on the battle deck page, else False
    """
    iar = numpy.asarray(screenshot())

    battle_deck_text_exists = False
    for x_coord in range(180, 240):
        this_pixel = iar[140][x_coord]
        if pixel_is_equal(this_pixel, [248, 250, 253], tol=35):
            battle_deck_text_exists = True

    elixer_icon_exists = False
    for x_coord in range(40, 60):
        this_pixel = iar[500][x_coord]
        if pixel_is_equal(this_pixel, [237, 53, 225], tol=35):
            elixer_icon_exists = True

    if battle_deck_text_exists and elixer_icon_exists:
        return True
    return False


def get_to_battle_deck_page(logger):
    """method for getting to the battle deck page from the main menu
    args:
        None
    returns:
        None
    """
    loops = 0
    while not check_if_on_battle_deck_page():
        loops += 1
        if loops > 25:
            logger.change_status("failure with get_to_battle_deck_page()")
            return "restart"

        click(140, 620)
        time.sleep(1)


def get_to_bannerbox_from_daily_reward_collection_popup():
    """method for getting to the bannerbox page from the daily reward collection popup
    args:
        None
    returns:
        None
    """
    click(200, 450)
    wait_for_bannerbox_page()


def check_if_on_bannerbox_page():
    """method for scanning for pixels that indicate the bot is on the bannerbox page
    args:
        None
    returns:
        bool, True if on the bannerbox page, else False
    """
    iar = numpy.asarray(screenshot())

    bannerbox_title_text_exists = False
    for x_coord in range(160, 280):
        this_pixel = iar[140][x_coord]
        if pixel_is_equal(this_pixel, [255, 255, 255], tol=35):
            bannerbox_title_text_exists = True

    info_button_exists = False
    for x_coord in range(70, 90):
        this_pixel = iar[612][x_coord]
        if pixel_is_equal(this_pixel, [76, 172, 255], tol=35):
            info_button_exists = True

    if bannerbox_title_text_exists and info_button_exists:
        return True
    return False


def wait_for_bannerbox_page():
    """method for waiting for the bannerbox page to appear
    args:
        None
    returns:
        None
    """
    while not check_if_on_bannerbox_page():
        click(20, 440)
        pass


def get_to_bannerbox(logger):
    """method for gettign to the bannerbox page to appear
    args:
        None
    returns:
        None
    """
    click(355, 230)
    wait_for_bannerbox_page()
    logger.change_status("made it to bannerbox page")


def check_for_bonus_bank_popup_in_battlepass_page(logger):
    """method for scanning for pixels that indicate the bonus bank popup is on the screen
    args:
        None
    returns:
        bool, True if the bonus bank popup is on the screen, else False
    """
    iar = numpy.asarray(screenshot())

    yellow_background_exists = False
    for x_coord in range(90, 100):
        this_pixel = iar[265][x_coord]
        if pixel_is_equal(this_pixel, [253, 204, 52], tol=35):
            yellow_background_exists = True

    green_collect_button_exists = False
    for x_coord in range(200, 220):
        this_pixel = iar[450][x_coord]
        if pixel_is_equal(this_pixel, [86, 228, 100], tol=35):
            green_collect_button_exists = True

    grey_background_exists = False
    for x_coord in range(320, 330):
        this_pixel = iar[470][x_coord]
        if pixel_is_equal(this_pixel, [80, 81, 110], tol=35):
            grey_background_exists = True

    if (
        yellow_background_exists
        and green_collect_button_exists
        and grey_background_exists
    ):
        logger.change_status("found bonus bank popup")
        return True
    return False


def handle_bonus_bank_popup_in_battlepass_page(logger):
    """method for handling the possiblity of the bonus bank popup appearing on the battlepass page
    args:
        None
    returns:
        None
    """
    logger.change_status("handling bonus bank popup")
    # click collect
    click(216, 466)
    time.sleep(3)


def get_to_challenges_tab(logger):
    """method for getting to the challenges tab
    args:
        None
    returns:
        None
    """
    click(x=394, y=634)
    time.sleep(3)

    # check if the user is in a tournament
    if check_if_account_is_already_in_a_challenge(logger):
        # click back button
        click(32, 56)
        time.sleep(5)

    logger.change_status(
        "Scrolling up in the challenges tab to assure the bot is at the top of the page"
    )
    for _ in range(5):
        scroll_up_fast_on_left_side_of_screen()
    time.sleep(1)
    logger.change_status("done")


def check_if_account_is_already_in_a_challenge(logger):
    iar = numpy.asarray(screenshot())

    # look for purple background of win count in this challenge
    purple_background_exists = False
    for x in range(100, 200):
        this_pixel = iar[280][x]
        if pixel_is_equal(this_pixel, [101, 56, 188], tol=35):
            purple_background_exists = True

    # look for yellow back button in top left
    yellow_back_button_exists = False
    for x in range(10, 40):
        this_pixel = iar[60][x]
        if pixel_is_equal(this_pixel, [255, 186, 37], tol=35):
            yellow_back_button_exists = True

    if purple_background_exists and yellow_back_button_exists:
        logger.change_status("account is already in a challenge")
        return True
    return False
