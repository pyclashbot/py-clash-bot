import time

from bot.navigation import (
    check_if_on_clash_main_menu,
    get_to_clan_tab_from_clash_main,
    get_to_profile_page,
    wait_for_clash_main_menu,
)
from detection.image_rec import (
    check_for_location,
    check_line_for_color,
    find_reference,
    find_references,
    get_file_count,
    get_first_location,
    make_reference_image_list,
    pixel_is_equal,
)
from memu.client import click, screenshot
from memu.client import scroll_up
from detection.image_rec import region_is_color
from detection.image_rec import line_is_color
from bot.navigation import get_to_clash_main_from_clan_page
from utils.logger import Logger
import numpy

import random

CARD_COORDS = [
    (143, 555),
    (211, 555),
    (269, 555),
    (343, 555),
]

CLAN_PAGE_ICON_COORD = (281, 586)
EDIT_WAR_DECK_BUTTON_COORD = (148, 413)
RANDOM_DECK_BUTTON_COORD = (265, 483)
CLOSE_WAR_DECK_EDITOR_PAGE_BUTTON = (211, 38)

START_WAR_BATTLE_BUTTON_COORD = (267, 410)

LEAVE_WAR_BATTLE_BUTTON_COORD = (204, 553)


WAR_PAGE_DEADSPACE_COORD = (15, 315)


def war_state(vm_index: int, logger: Logger, NEXT_STATE: str):
    logger.change_status("War state")

    # if not on clash main: return
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status("Error 4069852734098 Not on clash main to begin war state")
        return "restart"

    in_a_clan_check = war_state_check_if_in_a_clan(vm_index, logger)

    if in_a_clan_check == "restart":
        logger.change_status(
            "Error 502835 Failure while checking if in a clan before war battle"
        )
        return "restart"

    if not in_a_clan_check:
        logger.change_status("Not in a clan so skipping war...")

        return

    # get to clan page
    get_to_clan_tab_from_clash_main(vm_index, logger)

    # find battle icon
    find_and_click_war_battle_icon(vm_index, logger)

    # make deck if needed
    handle_make_deck(vm_index)

    if not check_if_deck_is_ready_for_this_battle(vm_index):
        logger.change_status("Exhausted war decks")
        # click deadspace a little to close war battle windows
        click(
            vm_index,
            WAR_PAGE_DEADSPACE_COORD[0],
            WAR_PAGE_DEADSPACE_COORD[1],
            clicks=5,
            interval=0.3,
        )
        time.sleep(0.3)

        get_to_clash_main_from_clan_page(vm_index, logger)

        if wait_for_clash_main_menu(vm_index, logger) == "restart":
            logger.change_status(
                "Erorr 77 84278 failed to get to clash main after exhausting war battle decks"
            )
            return "restart"

        return NEXT_STATE

    # start battle
    click(vm_index, START_WAR_BATTLE_BUTTON_COORD[0], START_WAR_BATTLE_BUTTON_COORD[1])
    time.sleep(3)

    # wait for battle start
    wait_for_war_battle_start(vm_index, logger)

    # do fight
    if do_war_battle(vm_index, logger) == "restart":
        logger.change_status("Error 58734 Failed doing war battle")
        return "restart"
    logger.change_status("Done with war battle. Waiting 10s")
    time.sleep(10)

    # when battle end, leave battle
    click(vm_index, LEAVE_WAR_BATTLE_BUTTON_COORD[0], LEAVE_WAR_BATTLE_BUTTON_COORD[1])

    if wait_for_war_page(vm_index, logger) == "restart":
        logger.change_status("Error 5135 Waited too long for war page")
        return "restart"

    if get_to_clash_main_from_clan_page(vm_index, logger) == "restart":
        logger.change_status(
            "Error 116135 Failed return to clash main after war battle"
        )
        return "restart"

    return NEXT_STATE


def wait_for_war_page(vm_index, logger):
    logger.change_status("Waiting for war page")
    start_time = time.time()
    while not check_if_on_war_page(vm_index):
        time_taken = time.time() - start_time
        if time_taken > 45:
            logger.change_status(
                "Error 1109572435 WAited too long for war page after leaving war battle"
            )
            return "restart"
    logger.log("Done waiting for war page")


def do_war_battle(vm_index, logger):
    start_time = time.time()
    logger.change_status("Starting war fighting")
    while check_if_in_war_battle(vm_index):
        time_taken = time.time() - start_time
        if time_taken > 120:
            logger.change_status("Error 658725 Ran war fight loop too long")
            return "restart"

        # click a random card
        logger.change_status("Doing a random war play")

        logger.log("Clicking random card")
        random_card_coord = random.choice(CARD_COORDS)
        click(vm_index, random_card_coord[0], random_card_coord[1])
        time.sleep(1)

        # click a random play coord
        logger.log("Clicking random play coord")
        random_play_coord = (random.randint(63, 205), random.randint(55, 455))
        click(vm_index, random_play_coord[0], random_play_coord[1])
        time.sleep(2.4)


def wait_for_war_battle_start(vm_index, logger):
    logger.change_status("Waiting for war battle start")

    start_time = time.time()

    while not check_if_in_war_battle(vm_index):
        time.sleep(3)

        time_taken = time.time() - start_time

        if time_taken > 45:
            logger.change_status("Error 98246572 Failure waiting for war battle start")
            return "restart"

    logger.log("Waiting for war battle start")


def check_if_in_war_battle(vm_index):
    if not check_line_for_color(
        vm_index, x1=104, y1=606, x2=123, y2=626, color=(224, 28, 215)
    ):
        return False
    if not line_is_color(vm_index, x1=51, y1=515, x2=68, y2=520, color=(255, 255, 255)):
        return False

    return True


def check_if_deck_is_ready_for_this_battle(vm_index):
    r2 = region_is_color(vm_index, [289, 400, 10, 5], (201, 201, 201))
    r3 = region_is_color(vm_index, [116, 398, 36, 6], (76, 172, 255))

    if r2 and r3:
        return False
    return True


def handle_make_deck(vm_index):
    # if the deck is ready to go, just return
    if check_if_deck_is_ready_for_this_battle(vm_index):
        return

    # click edit deck button
    click(vm_index, EDIT_WAR_DECK_BUTTON_COORD[0], EDIT_WAR_DECK_BUTTON_COORD[1])
    time.sleep(3)

    # click random deck button
    click(vm_index, RANDOM_DECK_BUTTON_COORD[0], RANDOM_DECK_BUTTON_COORD[1])
    time.sleep(3)

    # close deck editor
    click(
        vm_index,
        CLOSE_WAR_DECK_EDITOR_PAGE_BUTTON[0],
        CLOSE_WAR_DECK_EDITOR_PAGE_BUTTON[1],
    )
    time.sleep(3)


def find_and_click_war_battle_icon(vm_index, logger):
    start_time = time.time()

    coord = None
    while coord is None:
        time_taken = time.time() - start_time
        if time_taken > 30:
            logger.log("Erorr 9528753 Failure findign a war battle icon")
            return "restart"

        click(vm_index, CLAN_PAGE_ICON_COORD[0], CLAN_PAGE_ICON_COORD[1])
        time.sleep(1)
        scroll_up(vm_index)

        coord = find_war_battle_icon_coords(vm_index)

    click(vm_index, coord[0], coord[1])


def find_war_battle_icon_coords(vm_index):
    coord = find_battle_from_pix_list(get_war_battle_pix_list(vm_index))
    return coord


def find_battle_from_pix_list(pix_list):
    TOLERANCE = 15

    index_of_last_bad = 0
    index = 0
    result_coord = None

    for datum in pix_list:
        color = datum["color"]
        coord = datum["coord"]

        bool_datum = {
            "coord": coord,
            "bool": pixel_is_equal(color, [0, 180, 255], tol=30),
        }
        pix_list[index] = bool_datum

        if bool_datum["bool"]:
            pass
        else:
            index_of_last_bad = index

        if index - index_of_last_bad > TOLERANCE:
            result_coord = bool_datum["coord"]
            break

        index += 1

    return result_coord


def get_war_battle_pix_list(vm_index):
    data = []

    if not check_if_on_war_page(vm_index):
        return data

    iar = numpy.asarray(screenshot(vm_index))

    for y in range(182, 480):
        data.append(
            {
                "coord": (325, y),
                "color": iar[y][325],
            }
        )

    return data


def check_if_on_war_page(vm_index):
    if not check_line_for_color(
        vm_index, x1=19, y1=16, x2=59, y2=59, color=(144, 108, 255)
    ):
        return False
    if not check_line_for_color(
        vm_index, x1=61, y1=18, x2=51, y2=58, color=(144, 107, 255)
    ):
        return False
    if not check_line_for_color(
        vm_index, x1=31, y1=43, x2=51, y2=45, color=(226, 219, 228)
    ):
        return False

    if not region_is_color(vm_index, [225, 610, 25, 10], (80, 118, 153)):
        return False
    if not region_is_color(vm_index, [300, 610, 30, 14], (80, 118, 153)):
        return False

    return True


def war_state_check_if_in_a_clan(vm_index, logger: Logger):
    # if not on clash main, reutnr
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(f"ERROR 385423562623 Not on clash main menu")
        return "restart"

    # get to profile page
    if get_to_profile_page(vm_index, logger) == "restart":
        logger.change_status("Error 90723563485 Failure with get_to_profile_page")
        return "restart"

    # check pixels for in a clan
    in_a_clan = war_state_check_pixels_for_clan_flag(vm_index)

    # click deadspace to leave
    click(vm_index, 15, 300)
    if wait_for_clash_main_menu(vm_index, logger) == "restart":
        logger.change_status("Error 872356739 Failure with wait_for_clash_main_menu")
        return "restart"

    return in_a_clan


def war_state_check_pixels_for_clan_flag(vm_index):
    iar = numpy.asarray(screenshot(vm_index))

    for x in range(78, 97):
        this_pixel = iar[446][x]
        if not (pixel_is_equal([51, 51, 51], this_pixel, tol=25)):
            return True

    for y in range(437, 455):
        this_pixel = iar[y][87]
        if not (pixel_is_equal([51, 51, 51], this_pixel, tol=25)):
            return True

    return False


if __name__ == "__main__":
    pass
