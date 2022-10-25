import time

import numpy

from pyclashbot.clashmain import check_if_on_clash_main_menu
from pyclashbot.client import click, screenshot, scroll_up_fast
from pyclashbot.image_rec import (check_for_location, find_references,
                                  get_first_location, pixel_is_equal)


def upgrade_card():
    # Method for upgrading a given card

    # Starts on the page of a card that you want to upgrade (after you
    # click upgrade in the card list on the card page on clash main menu)

    # Click upgrade for gold button
    click(238, 606)
    time.sleep(1)

    # Click second upgrade for gold button
    click(234, 536)
    time.sleep(1)

    # Click close to 'not enough gold' notification
    click(346, 252)
    time.sleep(1)

    # Click dead space to close card page
    for _ in range(5):
        click(26, 518)


def upgrade_current_cards(logger):
    # Method to upgrade the cards in your deck if they're available for
    # upgrade and you have the gold
    # Starts on the clash main card page looking at your main deck
    # Ends in the same spot

    # make list of coords of the 8 cards on display
    card_coord_list = [
        [86, 278],
        [174, 278],
        [260, 278],
        [328, 278],
        [86, 400],
        [174, 400],
        [260, 400],
        [328, 400]
    ]
    # make list of coords of where the upgrade button will possibly appear for
    # each 8 cards
    upgrade_button_coords = [
        [51, 338],
        [136, 338],
        [283, 338],
        [303, 337],
        [53, 464],
        [133, 464],
        [281, 465],
        [303, 466],
    ]

    for n in range(8):
        card_coord = card_coord_list[n]
        upgrade_button_coord = upgrade_button_coords[n]

        click(card_coord[0], card_coord[1])
        time.sleep(1)

        # check if upgrade button is there
        pix = numpy.asarray(screenshot())[
            upgrade_button_coord[1] + 10][upgrade_button_coord[0] + 10]
        # print(pix)
        if check_if_pixel_indicates_upgrade(pix):
            logger.change_status(f"Upgrading card: {str(n + 1)}")
            click(upgrade_button_coord[0], upgrade_button_coord[1])
            time.sleep(1)
            upgrade_card()
            logger.add_card_upgraded()


def check_if_pixel_indicates_upgrade(pixel):
    # Method to see if the given pixel color indicates an upgrade in that spot
    # on the card page
    positive_color_list = [
        [42, 172, 55], [96, 217, 110], [65, 224, 80], [34, 104, 42]
    ]
    return any(pixel_is_equal(pixel, color, tol=30)
               for color in positive_color_list)


def get_to_clash_main_from_card_page(logger):
    # Method to get to the clash royale main menu screen from the card page

    logger.change_status("Getting to clash main from card page")
    click(250, 630)
    loops = 0

    on_clash_main = check_if_on_clash_main_menu()
    while not (on_clash_main):
        loops += 1
        if loops > 15:
            logger.change_status("Couldn't get to clash main from card page")
            return "restart"
        click(212, 623)
        time.sleep(1)
        on_clash_main = check_if_on_clash_main_menu()


def get_to_card_page(logger):
    # Method to get to the card page on clash main from the clash main menu

    click(x=100, y=630)
    time.sleep(2)
    loops = 0
    while not check_if_on_first_card_page():
        logger.change_status("Not elixer button. Moving pages")
        time.sleep(1)
        click(x=100, y=630)
        loops = loops + 1
        if loops > 10:
            logger.change_status("Couldn't make it to card page")
            return "restart"
        time.sleep(0.2)
    scroll_up_fast()
    #logger.change_status("Made it to card page")
    time.sleep(1)


def check_if_on_first_card_page():
    # Method to check if the elixer icon of your deck's AVG elixer when on the
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
    ]

    locations = find_references(
        screenshot=screenshot(),
        folder="card_page_elixer_icon",
        names=references,
        tolerance=0.97
    )

    return get_first_location(locations)


def find_card_page_logo():
    # Method to find the card page logo in the icon list in the bottom of the
    # screen when on clash main
    references = [
        "1.png",
        "2.png",
        "3.png",
        "4.png",
    ]
    locations = find_references(
        screenshot=screenshot(),
        folder="card_page_logo",
        names=references,
        tolerance=0.97
    )
    return check_for_location(locations)


def select_second_deck(logger):
    # Method to select the second deck of this account

    #logger.change_status("Selecting deck number 2 for use.")
    # get to card page
    get_to_card_page(logger)
    time.sleep(1)

    # click number 2
    click(173, 190)
    time.sleep(1)

    # get to main menu from card page
    get_to_clash_main_from_card_page(logger)


def randomize_and_select_deck_2(logger):
    # Method to randomize deck number 2 of this account

    logger.change_status("Randomizing deck number 2")
    # get to card page
    get_to_card_page(logger)

    # select deck 2
    click(173, 190)
    time.sleep(1)

    # click deck options tab
    click(339, 165)
    time.sleep(1)

    # click randomize button
    click(253, 173)
    time.sleep(1)

    # click confirm
    click(261, 419)
    time.sleep(1)

    # return to clash main
    get_to_clash_main_from_card_page(logger)
