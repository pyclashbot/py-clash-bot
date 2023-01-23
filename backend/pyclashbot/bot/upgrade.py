import time

import numpy

from pyclashbot.detection import (
    check_for_location,
    find_references,
    get_first_location,
    pixel_is_equal,
)
from pyclashbot.memu import click, get_file_count, screenshot
from pyclashbot.memu.client import make_reference_image_list


def check_if_card_is_upgradable(card_coord=None, upgrade_coord=None):
    # null checks
    if card_coord is None:
        card_coord = []
    if upgrade_coord is None:
        upgrade_coord = []

    # click card
    click(card_coord[0], card_coord[1])
    time.sleep(1)

    # check upgrade coord
    upgrade_color = [56, 228, 72]
    pixel = numpy.asarray(screenshot())[upgrade_coord[1]][upgrade_coord[0]]

    return bool(pixel_is_equal(pixel, upgrade_color, tol=35))


def check_for_upgradable_cards():
    card_coord_list = [
        [94, 277],
        [179, 277],
        [255, 277],
        [338, 277],
        [94, 406],
        [179, 406],
        [255, 406],
        [338, 406],
    ]
    upgrade_coord_list = [
        [47, 338],
        [133, 338],
        [221, 338],
        [307, 337],
        [47, 471],
        [133, 471],
        [221, 470],
        [309, 471],
    ]

    card_upgrade_list = []
    for card_index in range(8):
        card_coord = card_coord_list[card_index]
        upgrade_coord = upgrade_coord_list[card_index]
        if check_if_card_is_upgradable(
            card_coord=card_coord, upgrade_coord=upgrade_coord
        ):
            card_upgrade_list.append("Upgrade")
        else:
            card_upgrade_list.append("No upgrade")
            time.sleep(0.5)
    return card_upgrade_list


def upgrade_card(logger, card_index):
    card_coord_list = [
        [81, 337],
        [169, 339],
        [253, 338],
        [330, 337],
        [81, 464],
        [164, 468],
        [248, 466],
        [334, 468],
    ]

    # Click the given card
    card_coord = card_coord_list[card_index]
    click(card_coord[0], card_coord[1])

    # Click the upgrade button below the card
    click(card_coord[0], card_coord[1])
    time.sleep(1)

    # Click upgrade for gold button
    upgrade_for_gold_button = find_first_upgrade_for_gold_button()
    if upgrade_for_gold_button is not None:
        click(upgrade_for_gold_button[1], upgrade_for_gold_button[0])
        time.sleep(1)

    # Check for second upgrade for gold button
    if check_for_final_upgrade_button():
        logger.add_card_upgraded()

    # Click confirm upgrade for gold button
    confirm_upgrade_button = find_confirm_upgrade_for_gold_button()
    if confirm_upgrade_button is not None:
        click(confirm_upgrade_button[1], confirm_upgrade_button[0])

    # Click close to 'not enough gold' notification
    click(346, 252)

    # Click dead space to close card page
    for _ in range(5):
        click(26, 518)
        time.sleep(0.33)


def find_first_upgrade_for_gold_button():
    # Method to find the first upgrade for gold button in the card page
    references = make_reference_image_list(
        get_file_count(
            "card_collection_icon",
        )
    )

    locations = find_references(
        screenshot=screenshot(),
        folder="find_first_upgrade_for_gold_button",
        names=references,
        tolerance=0.97,
    )
    return get_first_location(locations)


def find_confirm_upgrade_for_gold_button():
    # Method to find the first upgrade for gold button in the card page
    references = make_reference_image_list(
        get_file_count(
            "card_collection_icon",
        )
    )

    locations = find_references(
        screenshot=screenshot(),
        folder="find_confirm_upgrade_for_gold_button",
        names=references,
        tolerance=0.97,
    )
    return get_first_location(locations)


def check_for_final_upgrade_button() -> bool:
    iar = numpy.asarray(screenshot())
    color = [56, 228, 72]
    pix_list = [
        iar[540][200],
        iar[547][204],
        iar[555][208],
        iar[560][212],
    ]
    check_1 = True
    for pix in pix_list:
        if not pixel_is_equal(pix, color, tol=45):
            check_1 = False
    if check_1:
        return True

    pix_list = [
        iar[435][206],
        iar[445][204],
        iar[455][203],
        iar[465][201],
    ]
    check_2 = True
    for pix in pix_list:
        if not pixel_is_equal(pix, color, tol=45):
            check_2 = False
    return bool(check_2)


def upgrade_current_cards(logger):
    logger.change_status("Checking for upgradable cards. . .")
    upgradable_cards_list = check_for_upgradable_cards()

    logger.change_status("Upgrading your current deck...")
    for index, card in enumerate(upgradable_cards_list):
        if card == "Upgrade":
            upgrade_card(logger, index)
