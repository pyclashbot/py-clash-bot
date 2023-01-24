import time

import numpy

from pyclashbot.detection import (
    check_for_location,
    find_references,
    get_first_location,
    pixel_is_equal,
)
from pyclashbot.memu import click, get_file_count, screenshot
from pyclashbot.memu.client import make_reference_image_list, scroll_up_fast


def check_for_upgradable_cards():
    card_coord_list = [
        [80, 270],
        [170, 270],
        [270, 270],
        [335, 270],
        [80, 400],
        [170, 400],
        [270, 400],
        [335, 400],
    ]
    upgrade_coord_list = [
        [113, 361],
        [198, 360],
        [288, 361],
        [375, 363],
        [115, 482],
        [204, 478],
        [292, 480],
        [378, 481],
    ]

    upgrade_card_bool_list = []

    scroll_up_fast()

    for card_index in range(8):
        this_card_coord = card_coord_list[card_index]
        this_upgrade_coord = upgrade_coord_list[card_index]

        # click the card
        click(this_card_coord[0], this_card_coord[1])
        time.sleep(1)

        # get the pixel surrounding the upgrade button
        this_pixel = numpy.asarray(screenshot())[this_upgrade_coord[1]][
            this_upgrade_coord[0]
        ]

        green_color = [56, 228, 72]

        if pixel_is_equal(this_pixel, green_color, tol=35):
            upgrade_card_bool_list.append(card_index)

    return upgrade_card_bool_list


def upgrade_current_cards(logger):
    logger.change_status("Checking for upgradable cards")
    upgradable_cards_list = check_for_upgradable_cards()

    card_coord_list = [
        [80, 270],
        [170, 270],
        [270, 270],
        [335, 270],
        [80, 400],
        [170, 400],
        [270, 400],
        [335, 400],
    ]

    upgrade_coord_list = [
        [77, 354],
        [166, 351],
        [250, 350],
        [335, 353],
        [77, 466],
        [164, 468],
        [250, 470],
        [340, 468],
    ]

    for index in upgradable_cards_list:
        this_card_coord = card_coord_list[index]
        this_upgrade_coord = upgrade_coord_list[index]
        upgrade_card(logger, this_card_coord, this_upgrade_coord)


def upgrade_card(logger, card_coord, upgrade_coord):
    # click the card in question
    print("clicking card to upgrade")
    click(card_coord[0], card_coord[1])
    time.sleep(1)

    # click the upgrade button
    print("clicking upgrade button")
    click(upgrade_coord[0], upgrade_coord[1])
    time.sleep(1)

    # locate+click the first upgrade button in the upgrade menu
    print("clicking first upgrade button")
    first_upgrade_button = find_first_upgrade_button_in_upgrade_menu()
    click(first_upgrade_button[0], first_upgrade_button[1])
    time.sleep(1)

    # if missing gold popup exists now then there isnt enough gold, so return
    if check_if_buy_missing_gold_popup_exists():
        logger.log("Not enough gold to upgrade this card")
        close_buy_missing_gold_popup()
        time.sleep(1)

        # click deadspace a little
        click(20, 440, clicks=5, interval=1)

        return

    # locate+click  the second upgrade button in the upgrade menu (aka the confirm button)
    print("clicking second upgrade button")
    second_upgrade_button = find_second_upgrade_button_in_upgrade_menu()
    click(second_upgrade_button[0], second_upgrade_button[1])
    time.sleep(1)

    logger.add_card_upgraded()

    # click deadspace
    click(20, 440, clicks=5, interval=1)


def find_first_upgrade_button_in_upgrade_menu():
    # method to find the 2v2 quickmatch button in the party mode menu
    current_image = screenshot()
    reference_folder = "find_first_upgrade_button_in_upgrade_menu"

    references = make_reference_image_list(
        get_file_count(
            "find_first_upgrade_button_in_upgrade_menu",
        )
    )

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97,
    )

    coord = get_first_location(locations)
    if coord is None:
        return None
    return [coord[1], coord[0]]


def find_second_upgrade_button_in_upgrade_menu():
    # method to find the 2v2 quickmatch button in the party mode menu
    current_image = screenshot()
    reference_folder = "find_second_upgrade_button_in_upgrade_menu"

    references = make_reference_image_list(
        get_file_count(
            "find_second_upgrade_button_in_upgrade_menu",
        )
    )

    locations = find_references(
        screenshot=current_image,
        folder=reference_folder,
        names=references,
        tolerance=0.97,
    )

    coord = get_first_location(locations)
    if coord is None:
        return None
    return [coord[1], coord[0]]


def check_if_buy_missing_gold_popup_exists():
    iar = numpy.asarray(screenshot())

    top_green_background_exists = False
    for x in range(180, 240):
        if pixel_is_equal(iar[409][x], [105, 235, 118], tol=35):
            top_green_background_exists = True

    bottom_green_background = False
    for x in range(180, 240):
        if pixel_is_equal(iar[437][x], [53, 225, 69], tol=35):
            bottom_green_background = True

    white_text_exists = False
    for x in range(180, 220):
        if pixel_is_equal(iar[424][x], [250, 250, 250], tol=35):
            white_text_exists = True

    if top_green_background_exists and bottom_green_background and white_text_exists:
        return True
    return False


def close_buy_missing_gold_popup():
    click(352, 239)
