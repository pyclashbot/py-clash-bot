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
    scroll_up_fast,
)


def get_to_card_page(logger):
    # Method to get to the card page on clash main from the clash main menu
    print("get to card page")
    click(x=100, y=630)
    time.sleep(2)
    loops = 0
    while not check_if_on_first_card_page():
        print("Looping to get to card page")
        # logger.change_status("Not elixer button. Moving pages")
        time.sleep(1)
        click(x=100, y=630)
        time.sleep(1)
        loops = loops + 1
        if loops > 10:
            logger.change_status("Couldn't make it to card page")
            return "restart"
        time.sleep(0.2)
    scroll_up_fast()
    print("made it to card page")
    time.sleep(1)


def get_to_war_page_from_main(logger):
    print("getting to war page from clash main.")
    if check_if_on_war_page():
        return None

    click(315, 635)
    time.sleep(3)

    loops = 0
    while not check_if_on_war_page():
        print("still not on war page. Cycling.")
        handle_war_chest_obstruction(logger)
        loops += 1
        if loops > 20:
            logger.change_status(
                "failure getting to war page using get_to_war_page_from_main()"
            )
            return "restart"
        click(280, 620)
        time.sleep(1)
    return None


def get_to_clash_main_from_shop(logger):
    logger.change_status("Getting to clash main from shop.")
    # click main
    click(240, 630)
    time.sleep(2)

    loops = 0
    while not check_if_on_clash_main_menu():
        loops += 1
        if loops > 20:
            print(
                "Looped through get_to_clash_main_from_shop() too many times. Restarting"
            )
            return "restart"
        click(200, 620)
        time.sleep(2)

    logger.change_status("Made it to clash main from shop.")


def get_to_shop_page_from_main(logger):
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
    if not check_if_on_shop_page_with_delay():
        logger.change_status("Failed to get to shop page.")
        return "restart"

    logger.change_status("Made it to shop from main.")


def get_to_clash_main_from_card_page(logger):
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
    on_main = check_if_on_clash_main_menu()
    loops = 0
    while not on_main:
        print("Still not on main page. Cycling")
        loops += 1
        if loops > 7:
            logger.change_status("Could not get to clash main from request page.")
            return "restart"
        click(208, 636)
        time.sleep(1)
        on_main = check_if_on_clash_main_menu()
    print("made it to clash main.")
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

        # handle other war chest popup
        handle_war_loot_chest()

        # handle war chest popup
        if check_for_war_loot_menu():
            print("Found war loot. handling it.")
            handle_war_loot_menu()

        # handle final results popup
        if check_for_final_results_popup():
            handle_final_results_popup()

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


def handle_war_loot_chest():
    if check_for_war_loot_chest():
        print("Found a war chest in the way...")
        # click open chest
        print("Clicking open war chest..")
        click(205, 440)
        time.sleep(1)

        # skip thru chest
        print("Skipping thru war chest rewards...")
        click(20, 450, clicks=10, interval=0.33)
        time.sleep(1)

        print("Done handling war chest...")


def handle_card_mastery_notification():
    # Method to handle the possibility of a card mastery notification
    # obstructing the bot
    click(107, 623)
    time.sleep(1)

    click(240, 630)
    time.sleep(1)


def handle_war_loot_menu():
    # open chest
    print("Opening war chest")
    click(205, 420)
    time.sleep(1)

    # click dead space to skip thru chest
    print("Skipping thru war chest rewards")
    click(20, 440, clicks=20, interval=0.1)
    time.sleep(1)


def handle_stuck_on_war_final_results_page():
    if check_if_stuck_on_war_final_results_page():
        click(215, 565)
        time.sleep(1)


def check_if_stuck_on_war_final_results_page():
    iar = numpy.asarray(screenshot())
    pix_list = [
        iar[575][235],
        iar[567][245],
        iar[575][255],
    ]

    return all(pixel_is_equal([180, 96, 253], pix, tol=45) for pix in pix_list)


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


def check_if_on_war_page():
    iar = numpy.asarray(screenshot())
    pix_list = [
        iar[73][43],
        iar[83][43],
    ]
    color = [232, 225, 236]
    return all(pixel_is_equal(pix, color, tol=45) for pix in pix_list)


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


def check_for_war_loot_chest():
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
    iar = numpy.asarray(screenshot())

    pix_list = [
        iar[414][210],
        iar[418][217],
        iar[423][227],
        iar[427][237],
    ]
    color = [255, 190, 48]

    return all(pixel_is_equal(color, pix, tol=45) for pix in pix_list)


def check_for_final_results_popup():
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
    print("Final results popup detected.")
    return True


def check_if_on_shop_page_with_delay():
    start_time = time.time()
    while time.time() - start_time < 3:
        print("looping thru")
        if check_if_on_shop_page():
            print("made it")
            return True
        time.sleep(0.5)
    return False


def check_if_on_shop_page():
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


def handle_final_results_popup():
    print("Doing final results popup hanlding.")

    # click OK
    click(220, 555)
    time.sleep(5)


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