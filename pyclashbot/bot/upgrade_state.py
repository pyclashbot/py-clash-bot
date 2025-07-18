import time
from typing import Any

from pyclashbot.bot.nav import (
    check_if_on_card_page,
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
    wait_for_clash_main_menu,
)
from pyclashbot.detection.image_rec import (
    check_line_for_color,
    pixel_is_equal,
    region_is_color,
)
from pyclashbot.memu.client import click, screenshot
from pyclashbot.utils.logger import Logger

CARD_COORDS: list[Any] = [
    (76, 227),
    (175, 224),
    (257, 230),
    (339, 230),
    (85, 370),
    (175, 370),
    (257, 370),
    (339, 370),
]

UPGRADE_PIXEL_COORDS: list[Any] = [
    (40, 280),
    (132, 280),
    (220, 280),
    (309, 280),
    (40, 423),
    (132, 423),
    (220, 423),
    (309, 423),
]


UPGRADE_BUTTON_COORDS = [
    (74, 280),
    (165, 280),
    (254, 280),
    (348, 280),
    (74, 423),
    (165, 423),
    (254, 423),
    (348, 423),
]

SECOND_UPGRADE_BUTTON_COORDS = (236, 574)

SECOND_UPGRADE_BUTTON_COORDS_CONDITION_1 = (239, 488)

CONFIRM_UPGRADE_BUTTON_COORDS = (232, 508)

CONFIRM_UPGRADE_BUTTON_COORDS_CONDITION_1 = (242, 413)

DEADSPACE_COORD = (10, 323)


CLOSE_CARD_PAGE_COORD = (355, 238)


def upgrade_cards_state(vm_index, logger: Logger, next_state):
    logger.change_status(status="Upgrade cards state")

    # if not on clash main, return restart
    print("Making sure on clash main before upgrading cards")
    clash_main_check = check_if_on_clash_main_menu(vm_index)
    if clash_main_check is not True:
        logger.change_status("Not on clash main at the start of upgrade_cards_state()")
        return "restart"

    # get to card page
    logger.change_status(status="Getting to card page")
    if get_to_card_page_from_clash_main(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 0751389 Failure getting to card page from clash main in Upgrade State",
        )
        return "restart"

    # do card upgrade
    if update_cards(vm_index, logger) is False:
        logger.change_status("Failed to update cards")
        return "restart"

    # get back to main when its done
    logger.change_status(status="Done upgrading cards")
    click(vm_index, 211, 607)
    time.sleep(1)

    # return to clash main
    print("Returning to clash main after upgrading")
    click(vm_index, 243, 600)
    time.sleep(3)

    # wait for main
    if wait_for_clash_main_menu(vm_index, logger, deadspace_click=False) is False:
        logger.change_status("Failed to wait for clash main after upgrading cards")
        return "restart"

    logger.update_time_of_last_card_upgrade(time.time())
    return next_state


def get_upgradable_cards(vm_index):
    def classify_color(color):
        # is white?
        if color[0] > 200 and color[1] > 200 and color[2] > 200:
            return "white"

        # if [ 75 250  33]
        if color[0] < 100 and color[2] < 100 and color[1] > 200:
            return "green"

        return "else"

    def get_region_pixels(region):
        pixels = []
        l, t, w, h = region  # noqa: E741

        for i, x in enumerate(range(w)):
            for j, y in enumerate(range(h)):
                if i % 2 == 0 or j % 2 == 0:
                    continue
                pixels.append(image[t + y][l + x])

        return pixels

    regions = [
        [46, 256, 64, 11],
        [133, 256, 64, 11],
        [220, 256, 64, 11],
        [307, 256, 64, 11],
        [46, 395, 64, 11],
        [133, 395, 64, 11],
        [220, 395, 64, 11],
        [307, 395, 64, 11],
    ]

    image = screenshot(vm_index)

    good_indicies = []

    for i, region in enumerate(regions):
        pixels = get_region_pixels(region)

        colors = [classify_color(pixel) for pixel in pixels]

        color2count = {}
        for color in colors:
            if color not in color2count:
                color2count[color] = 0
            color2count[color] += 1

        if "green" in color2count and color2count["green"] > 20:
            good_indicies.append(i)

    return good_indicies


def update_cards(vm_index, logger: Logger) -> bool:
    # starts and ends on card page

    # if not on card page, return false
    if not check_if_on_card_page(vm_index):
        logger.log("Not on card page to start update_cards(). Returning false")
        return False

    # click a topleft card to open edit deck mode
    click(vm_index, 73, 201)
    time.sleep(0.3)

    # click deadspace
    click(vm_index, 14, 300)
    time.sleep(0.3)

    upgradable_indicies = get_upgradable_cards(vm_index)

    for index in upgradable_indicies:
        if upgrade_card(vm_index, logger, index) is True:
            logger.log("Upgraded a card!")
        else:
            logger.log("Can't upgraded this card yet")

    return True


def check_for_second_upgrade_button_condition_1(vm_index) -> bool:
    """Check if the second upgrade button condition 1 is met.

    Args:
    ----
        vm_index (int): The index of the virtual machine.

    Returns:
    -------
        bool: True if the condition is met, False otherwise.

    """
    if not check_line_for_color(vm_index, 201, 473, 203, 503, (56, 228, 72)):
        return False
    if not check_line_for_color(vm_index, 275, 477, 276, 501, (56, 228, 72)):
        return False
    if not check_line_for_color(vm_index, 348, 153, 361, 153, (229, 36, 36)):
        return False

    return True


def check_for_confirm_upgrade_button_condition_1(vm_index) -> bool:
    """Check if the confirm upgrade button condition 1 is met.

    Args:
    ----
        vm_index (int): The index of the virtual machine.

    Returns:
    -------
        bool: True if the condition is met, False otherwise.

    """
    if not check_line_for_color(vm_index, 201, 401, 201, 432, (56, 228, 72)):
        return False
    if not check_line_for_color(vm_index, 277, 399, 277, 431, (56, 228, 72)):
        return False
    if not check_line_for_color(vm_index, 347, 153, 361, 154, (111, 22, 29)):
        return False

    return True


def card_is_open(vm_index, index):
    """
    clicking a card opens a menu
    this method checks that menu is open for each coordiante the menu
    can appear in, according to the card index that is being opened
    """
    # specify coords of pixels that indicate an open menu
    card_index_to_coord = {
        0: (43, 326),
        1: (131, 326),
        2: (218, 326),
        3: (302, 326),
        4: (41, 461),
        5: (131, 461),
        6: (218, 461),
        7: (302, 461),
    }

    # get an image
    image = screenshot(vm_index)

    # get the pixels for each card
    card_index_to_pixel = {}
    for card_index, coord in card_index_to_coord.items():
        pixel = image[coord[1]][coord[0]]
        card_index_to_pixel[card_index] = pixel

    # get the colors of each card's pixel
    card_index_to_is_red = {}
    red = [75, 75, 252]  # bgr red
    for card_index, pixel in card_index_to_pixel.items():
        is_red = pixel_is_equal(pixel, red, tol=45)
        card_index_to_is_red[card_index] = is_red

    return card_index_to_is_red[index]


def upgrade_card(vm_index, logger: Logger, card_index) -> bool:
    """Upgrades a card if it is upgradable.

    Args:
    ----
        vm_index (int): The index of the virtual machine to perform the upgrade on.
        logger (Logger): The logger object to use for logging.
        index (int): The index of the card to upgrade.
        upgrade_list (list[bool]): A list of bool values indicating whether each card is upgradable.

    Returns:
    -------
        None

    """
    print("\n")
    upgraded_a_card = False
    logger.change_status(status=f"Upgrading card index: {card_index}")

    # click the card
    while not card_is_open(vm_index, card_index):
        print(f"Opening this card options: {card_index}")
        click(vm_index, CARD_COORDS[card_index][0], CARD_COORDS[card_index][1])
        time.sleep(1)

    # click the upgrade button
    logger.change_status(status="Clicking the upgrade button for this card")
    coord = UPGRADE_BUTTON_COORDS[card_index]
    click(vm_index, coord[0], coord[1])
    time.sleep(1)

    # click second upgrade button
    logger.change_status(status="Clicking the second upgrade button")
    if check_for_second_upgrade_button_condition_1(vm_index):
        click(
            vm_index,
            SECOND_UPGRADE_BUTTON_COORDS_CONDITION_1[0],
            SECOND_UPGRADE_BUTTON_COORDS_CONDITION_1[1],
        )
    else:
        click(
            vm_index,
            SECOND_UPGRADE_BUTTON_COORDS[0],
            SECOND_UPGRADE_BUTTON_COORDS[1],
        )
    time.sleep(2)

    # if gold popup doesnt exists: add to logger's upgrade stat
    if not check_for_missing_gold_popup(vm_index):
        upgraded_a_card = True
        prev_card_upgrades = logger.get_card_upgrades()
        logger.add_card_upgraded()

        card_upgrades = logger.get_card_upgrades()
        logger.log(
            f"Incremented cards upgraded from {prev_card_upgrades} to {card_upgrades}",
        )
        # click confirm upgrade button
        logger.change_status(status="Clicking the confirm upgrade button")
        if check_for_confirm_upgrade_button_condition_1(vm_index):
            click(
                vm_index,
                CONFIRM_UPGRADE_BUTTON_COORDS_CONDITION_1[0],
                CONFIRM_UPGRADE_BUTTON_COORDS_CONDITION_1[1],
            )
        else:
            click(
                vm_index,
                CONFIRM_UPGRADE_BUTTON_COORDS[0],
                CONFIRM_UPGRADE_BUTTON_COORDS[1],
            )
        time.sleep(2)

        # close card page
        click(vm_index, CLOSE_CARD_PAGE_COORD[0], CLOSE_CARD_PAGE_COORD[1])
        time.sleep(2)

        logger.change_status("Upgraded this card")
    else:
        logger.log("Missing gold popup exists. Skipping this upgradable card.")
        upgraded_a_card = False

    # click deadspace
    logger.change_status(
        status="Clicking deadspace after attemping upgrading this card",
    )
    for _ in range(6):
        click(vm_index, DEADSPACE_COORD[0], DEADSPACE_COORD[1])
        time.sleep(1)

    return upgraded_a_card


def check_if_pixel_indicates_upgradable_card(pixel) -> bool:
    # print(f'Pixel is: {pixel}')

    r = pixel[0]
    g = pixel[1]
    b = pixel[2]

    # if more than 90 red, return False
    if r > 90:
        return False

    # if g is less than 200, return False
    if g < 200:
        return False

    # if more than 80 blue, return False
    if b > 80:
        return False

    return True


def check_for_missing_gold_popup(vm_index):
    if not check_line_for_color(
        vm_index,
        x_1=338,
        y_1=215,
        x_2=361,
        y_2=221,
        color=(153, 20, 17),
    ):
        return False
    if not check_line_for_color(
        vm_index,
        x_1=124,
        y_1=201,
        x_2=135,
        y_2=212,
        color=(255, 255, 255),
    ):
        return False

    if not check_line_for_color(vm_index, 224, 368, 236, 416, (56, 228, 72)):
        return False

    if not region_is_color(vm_index, [70, 330, 60, 70], (227, 238, 243)):
        return False

    return True


# def check_if_card_is_upgradable(vm_index, logger: Logger, card_index):
#     logger.change_status(status=f"Checking if {card_index} is upgradable")

#     # click the selected card
#     card_coord = CARD_COORDS[card_index]
#     print(f"Clicking the #{card_index} card")
#     click(vm_index, card_coord[0], card_coord[1])
#     time.sleep(0.66)

#     # see if green uprgade button exists in card context menu
#     card_is_upgradable = False
#     upgrade_coord = UPGRADE_PIXEL_COORDS[card_index]
#     if check_if_pixel_indicates_upgradable_card(
#         numpy.asarray(screenshot(vm_index))[upgrade_coord[1]][upgrade_coord[0]],
#     ):
#         card_is_upgradable = True

#     # deadspace click
#     # click(vm_index, 14, 286)

#     print(f"Card #{card_index} is upgradable: {card_is_upgradable}")
#     return card_is_upgradable


if __name__ == "__main__":
    card_index = 5
    logger = Logger(None, None)
    print(update_cards(1, logger))
    upgrade_card(1, logger, card_index)

    # while 1:
    #     print(card_is_open(1,-1))
    #     time.sleep(2)
    #     print('\n\n\n\n\n')
