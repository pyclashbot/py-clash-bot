import time

import numpy

from pyclashbot.bot.navigation import (
    check_if_on_clash_main_menu,
    get_to_challenges_tab,
    get_to_clash_main_settings_page,
    get_to_ssid_switch_page,
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
from pyclashbot.memu import click, screenshot
from pyclashbot.memu.client import (
    get_file_count,
    make_reference_image_list,
    scroll_down,
)


def check_if_on_trophy_progession_rewards_page():
    """Method to check if the bot is on the trophy progression
    rewards page which obstructs the clash main menu
    args:
        None
    returns:
        True if on trophy progression rewards page, False if not
    """
    iar = numpy.array(screenshot())
    pix_list = [
        iar[629][240],
        iar[631][185],
        iar[621][232],
    ]
    color = [78, 175, 255]

    return all((pixel_is_equal(pix, color, tol=35)) for pix in pix_list)


def check_for_reward_limit():
    """Method to check for the reward limit popup
    args:
        None
    returns:
        True if reward limit popup is present, False if not
    """
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
    """Method to scan for images that indicate the bot is in a battle
    args:
        None
    returns:
        True if in battle, False if not
    """
    references = ["1.png", "2.png", "3.png", "4.png", "5.png"]

    locations = find_references(
        screenshot=screenshot(),
        folder="check_if_in_battle",
        names=references,
        tolerance=0.97,
    )

    return bool(check_for_location(locations))


def check_if_in_a_clan(logger):
    """Method to check if the bot's current account is in a clan
    args:
        Logger: logger object
    returns:
        True if in a clan, False if not
    """
    # starts and ends on clash main
    logger.change_status("Checking if in a clan")

    # should be on main
    if not check_if_on_clash_main_menu():
        logger.change_status("Not on main menu so cant run check_if_in_a_clan()")
        return "restart"

    # click profile
    if open_profile_page() == "restart":
        return "restart"

    time.sleep(3)

    # get image array of flag where clan flag should be.
    is_in_a_clan = False
    iar = numpy.asarray(screenshot())
    for x_coord in range(81, 96):
        this_pixel = iar[480][x_coord]
        if pixel_is_equal(this_pixel, [50, 50, 50], tol=20):
            continue
        is_in_a_clan = True
        break

    # return to main after getting this information
    logger.change_status("Returning to main menu")
    click(363, 93)
    wait_for_clash_main_menu(logger)

    return is_in_a_clan


def get_to_account(logger, account_number):
    # pylint: disable=too-many-branches
    """method to get to the given account number represetned as a
    number 0-8 pertaining to which suppercell account to use
    args:
        Logger: logger object
        int: account number to switch to
    returns:
        restart state if failure, None if success
    """

    # Method to change account to the given account number using the supercell
    # ID login screen in the options menu in the clash main menu
    # Account number is ints 0-3 for the first 4 accounts
    logger.change_status(f"Switching accounts to account number {str(account_number)}")

    # open settings
    logger.change_status(
        "Opening settings tab from clash main to get to account switch"
    )
    if get_to_clash_main_settings_page(logger) == "restart":
        return "restart"

    # click switch accounts
    logger.change_status("Clicking the switch accounts button.")
    if get_to_ssid_switch_page() == "restart":
        return "restart"

    logger.change_status("getting to then clicking the appropriate account")

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
        scroll_down()
        click(170, 640)

    elif account_number == 5:
        # scroll then click
        for _ in range(4):
            scroll_down()
            time.sleep(0.5)
        click(230, 585)

    elif account_number == 6:
        # scroll then click
        for _ in range(7):
            scroll_down()
            time.sleep(0.5)
        click(240, 550)

    elif account_number == 7:
        # scroll then click
        for _ in range(7):
            scroll_down()
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
    """method to handle a new challenge notification obstructing the bot
    args:
        Logger: logger object
    returns:
        None
    """
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
    """Method to handle the special offer notification obstructing the bot
    args:
        Logger: logger object
    returns:
        None
    """

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
    """method for starting a 2v2quick match from the clash main menu
    args:
        Logger: logger object
    returns:
        restart state if failure, None if success
    """

    # Method to start a 2v2 quickmatch through the party mode through the
    # clash main menu
    logger.change_status("Initiating 2v2 match from main menu")

    # if not on clash main at this point then this failed
    if not check_if_on_clash_main_menu():
        logger.change_status("Not on clash main so cant run start_2v2()")
        print("#4589234985 Fail")
        return "restart"

    # get to challenges tab
    get_to_challenges_tab(logger)

    # click 2v2 mode
    two_v_two_match_icon_coord = find_2v2_match_icon()
    if two_v_two_match_icon_coord is None:
        logger.change_status("Could not find 2v2 match icon")
        return "restart"
    click(two_v_two_match_icon_coord[0], two_v_two_match_icon_coord[1])
    time.sleep(1)

    # click classic
    click(285, 213)
    time.sleep(1)

    # click battle
    click(x=210, y=450)
    time.sleep(1)

    # click quickmatch
    click(x=284, y=387)
    time.sleep(5)

    check_for_reward_limit()
    return None


def find_2v2_match_icon():
    """method to scan for images that indicate the coordinates
    of the 2v2 match icon in the challenges tab
    returns:
        coordinates of the 2v2 match icon in the challenges tab button if found, None if not found
    """

    current_image = screenshot()
    reference_folder = "2v2_match_icon"

    references = make_reference_image_list(
        get_file_count(
            reference_folder,
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


def wait_for_battle_start(logger):
    """Method to wait for the loading sequence of a battle to finish
    args:
        Logger: logger object
    returns:
        restart state if waited too long, None if success
    """

    # Method to wait for a the loading sequence of a battle to finish

    logger.change_status("Waiting for battle start. . .")

    start_time = time.time()

    wait_time = 300

    while not check_if_in_battle_with_delay():
        if time.time() - start_time > wait_time:
            logger.change_status(f"Waited longer than {wait_time} sec for a fight")
            return "restart"
    return "continue"


def check_if_pixels_indicate_in_battle():
    """Method to scan for images that inidcate the bot is in a battle
    args:
        None
    returns:
        True if in battle, False if not"""

    # make a screenshot that ignores the elixer icon in the loading screen

    references = ["1.png", "2.png", "3.png", "4.png", "5.png"]

    locations = find_references(
        screenshot=screenshot(region=[0, 600, 500, 200]),
        folder="check_if_in_battle",
        names=references,
        tolerance=0.97,
    )

    return check_for_location(locations)


def check_if_in_battle_with_delay():
    """Method to check if the bot is in a battle across a 3 second period
    args:
        None
    returns:
        True if in battle, False if not
    """

    start_time = time.time()
    while time.time() - start_time < 3:
        if check_if_pixels_indicate_in_battle():
            return True
    return False
