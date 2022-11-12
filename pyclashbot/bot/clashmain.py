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

ahk = AHK()


def wait_for_clash_main_menu(logger):
    logger.change_status("Waiting for clash main menu")
    waiting = not check_if_on_clash_main_menu()

    loops = 0
    while waiting:
        # loop count
        loops += 1
        if loops > 25:
            logger.change_status("Looped through getting to clash main too many times")
            return "restart"

        # wait 1 sec
        time.sleep(1)

        # click dead space
        click(32, 364)

        # check if stuck on trophy progression page
        if check_if_stuck_on_trophy_progression_page():
            time.sleep(1)
            click(210, 621)

        # check if still waiting
        waiting = not check_if_on_clash_main_menu()

    logger.change_status("Done waiting for clash main menu")


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


def get_to_card_page(logger):
    # Method to get to the card page on clash main from the clash main menu
    click(x=100, y=630)
    time.sleep(2)
    loops = 0
    while not check_if_on_first_card_page():
        # logger.change_status("Not elixer button. Moving pages")
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


def check_if_in_a_clan(logger):
    # Method to check if the current account has a clan

    # starts and ends on clash main
    logger.change_status("Checking if in a clan.")

    # click clan tab
    click(308, 627)

    # handle war chest popup
    if check_for_war_loot_menu():
        handle_war_loot_menu()

    # cycle through clan tab a few times
    for _ in range(10):
        click(280, 623)
        time.sleep(0.33)
        if check_for_war_loot_menu():
            handle_war_loot_menu()
    scroll_down()
    time.sleep(1)

    # get a pixel from this clan tab
    pixel_1 = numpy.array(screenshot())[118][206]

    # cycle tab again
    click(280, 623)
    time.sleep(1)

    # get second pixel
    pixel_2 = numpy.array(screenshot())[118][206]

    # if pixels aren't equal return True (in a clan because there are two
    # available pages instead of one)
    if not pixel_is_equal(pixel_1, pixel_2, tol=25):
        logger.change_status("You're in a clan")
        return True
    logger.change_status("Not in a clan.")
    return False


def get_to_clash_main_from_clan_page(logger):
    # Method to return to clash main menu from request page
    click(172, 612)
    time.sleep(1)
    on_main = check_for_gem_logo_on_main()
    loops = 0
    while not on_main:
        loops += 1
        if loops > 25:
            logger.change_status("Could not get to clash main from request page.")
            return "restart"
        click(208, 636)
        time.sleep(1)
        on_main = check_for_gem_logo_on_main()


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


def get_to_clan_page(logger):
    # method to get to clan chat page from clash main
    click(312, 629)
    on_clan_chat_page = check_if_on_clan_page()
    loops = 0
    while not on_clan_chat_page:
        # handle war chest popup
        if check_for_war_loot_menu():
            handle_war_loot_menu()

        # handling infinite loop
        loops += 1
        if loops > 25:
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


def get_to_account(logger, account_number):
    # Method to change account to the given account number using the supercell
    # ID login screen in the options menu in the clash main menu
    # Account number is ints 0-3 for the first 4 accounts

    time.sleep(2)

    logger.change_status(f"Switching accounts to account number {str(account_number)}")

    # open settings
    click(x=364, y=99)
    time.sleep(1)

    # click switch accounts
    click(200, 460)
    time.sleep(1)

    if account_number == 0:
        click(155, 350)
    if account_number == 1:
        click(190, 420)
    if account_number == 2:
        click(230, 510)
    if account_number == 3:
        click(230, 595)

    time.sleep(7)
    logger.add_account_switch()
    if wait_for_clash_main_menu(logger) == "restart":
        logger.change_status("Failed waiting for clash main")
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
    return None


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
        tolerance=0.97,
    )
    loc = get_first_location(locations)
    return loc is not None


def handle_gold_rush_event(logger):
    # Method to handle a gold rush event notification obstructing the bot

    logger.change_status(
        "Handling the possibility of a gold rush event notification obstructing the bot."
    )
    click(193, 465)
    time.sleep(0.1)
    click(193, 465)


def handle_new_challenge(logger):
    # Method to handle a new challenge notification obstructing the bot

    logger.change_status(
        "Handling the possibility of a new challenge notification obstructing the bot."
    )

    click(376, 639)

    click(196, 633)

    if check_if_on_trophy_progession_rewards_page():
        logger.change_status(
            "Handling the possibility of trophy progession rewards page obstructing the bot."
        )
        click(212, 633)


def handle_special_offer(logger):
    # Method to handle a special offer notification obstructing the bot

    logger.change_status(
        "Handling the possibility of special offer notification obstructing the bot."
    )

    click(35, 633)

    click(242, 633)

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
            logger.change_status(str(f"Unlocking chest {str(chest_index)}"))
            logger.add_chest_unlocked()
            click(210, 465)
        else:
            # logger.change_status("Handling possibility of rewards screen")
            for _ in range(10):
                ahk.click(20, 556)
                time.sleep(0.33)

        # close chest menu
        click(20, 556)


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


def start_2v2(logger):
    # Method to start a 2v2 quickmatch through the party mode through the
    # clash main menu
    logger.change_status("Initiating 2v2 match from main menu")

    # getting to party tab
    click(365, 108)
    time.sleep(1)
    click(263, 248)
    time.sleep(1)

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


def check_if_in_battle():
    references = ["1.png", "2.png", "3.png", "4.png", "5.png"]

    locations = find_references(
        screenshot=screenshot(),
        folder="check_if_in_battle",
        names=references,
        tolerance=0.97,
    )

    return bool(check_for_location(locations))


def handle_card_mastery_notification():

    # Method to handle the possibility of a card mastery notification
    # obstructing the bot
    click(107, 623)

    click(240, 630)


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


def handle_war_loot_menu():
    # open chest
    click(205, 410)

    # click dead space to skip thru chest
    for _ in range(15):
        click(20, 440)
        time.sleep(0.1)

    # click OK
    click(215, 550)
    time.sleep(0.5)

    scroll_down()
