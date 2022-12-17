import time

import numpy

from pyclashbot.bot.clashmain import check_if_on_clash_main_menu
from pyclashbot.bot.navigation import get_to_card_page, get_to_clash_main_from_card_page
from pyclashbot.detection import pixel_is_equal
from pyclashbot.detection.image_rec import check_for_location, find_references
from pyclashbot.memu import click, screenshot
from pyclashbot.memu.client import get_file_count, make_reference_image_list


def collect_card_mastery_rewards(logger):
    # starts on clash main, collects mastery rewards, returns to clash main

    reward_coords = [
        [210, 360],
        [190, 450],
        [210, 520],
        [205, 480],
    ]

    # if no mastery rewards to collect return
    logger.change_status("Checking if there are card mastery rewards to collect")

    # check if there are rewards to collect
    # check_if_can_collect_card_mastery_rewards starts and ends on clashmain
    has_rewards = check_if_can_collect_card_mastery_rewards(logger)

    # if reward to collect check fails return restart
    if has_rewards == "restart":
        logger.change_status("Failed when checking if has card mastery rewards")
        return "restart"

    # if there are no rewards then return
    if not has_rewards:
        logger.change_status(
            "No card mastery rewards to collect. Returning to clash main."
        )
        return None

    # otherwise there are rewards to collect so continue
    logger.change_status("There are card mastery rewards to collect!")

    # if made it to here, increment mastery reward collection counter
    logger.add_card_mastery_reward_collection()

    # get to card page
    if get_to_card_page(logger) == "restart":
        logger.change_status(
            "Failed to get to card page while collecting card mastery rewards"
        )
        return "restart"

    logger.change_status("Collecting a card mastery reward. . .")
    # click mastery reward button
    print("Clicking mastery button")
    click(257, 505)
    time.sleep(1)

    # click topleft most card in card mastery reward list
    print("Clicking first card in mastery reward table")
    click(104, 224)
    time.sleep(1)

    # click all reward regions
    print("Clicking various reward locations")
    for coord in reward_coords:
        handle_banner_box_popup()
        click(coord[0], coord[1])
        time.sleep(1)

    # click dead space
    print("Clicking dead space to exit mastery tabs")
    click(20, 400, clicks=20, interval=0.1)

    # get back to clash main
    if get_to_clash_main_from_card_page(logger) == "restart":
        logger.change_status(
            "failed getting back to clash main from card page after collecting card mastery rewards"
        )
        return "restart"

    return None


def check_if_can_collect_card_mastery_rewards(logger):
    # starts clash main , checks if there are mastery rewards, then returns to clash main

    # get to card page
    if get_to_card_page(logger) == "restart":
        logger.change_status(
            "Failed to get to card page while collecting card mastery rewards"
        )
        return "restart"

    start_time = time.time()
    has_rewards = False
    while time.time() - start_time < 3:
        pixel = numpy.asarray(screenshot())[499][239]
        # print(pixel)
        if bool(pixel_is_equal(pixel, [255, 166, 13], tol=45)):
            has_rewards = True

    # return to cash main
    if get_to_clash_main_from_card_page(logger) == "restart":
        logger.change_status(
            "Failed to get to main from card page while collecting card mastery rewards"
        )
        return "restart"

    return has_rewards


def check_for_banner_box_popup():
    current_image = screenshot()
    reference_folder = "check_for_banner_box_popup"

    references = make_reference_image_list(
        get_file_count(
            "check_for_banner_box_popup",
        )
    )

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97,
    )

    return check_for_location(locations)


def handle_banner_box_popup():
    if check_for_banner_box_popup():
        print("Found banner box popup")

        # click go to bannerbox
        print("click go to bannerbox")
        click(205, 450)
        time.sleep(1)

        # click '100 tickets' button in bottom right
        print("click '100 tickets' button in bottom right")
        click(330, 610)
        time.sleep(1)

        # click '100 tickets' button in the middle of the screen to open the chest
        print(
            "click '100 tickets' button in the middle of the screen to open the chest"
        )
        click(215, 505)
        time.sleep(3)

        # click deadspace
        print("Clicking dead space to skip through rewards")
        click(20, 440, clicks=10, interval=0.1)

        # close banner box
        print("Closing banner box first time")
        click(99, 999)
        time.sleep(1)

        # close banner box
        print("Closing banner box second time")
        click(355, 65)
        time.sleep(1)

        # close mastery tabs
        print("Clicking dead space to get to card page main.")
        click(20, 440, clicks=10, interval=0.1)
