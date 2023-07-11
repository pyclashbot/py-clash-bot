import random
import time
from typing import Literal

import numpy

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_clan_tab_from_clash_main,
    get_to_clash_main_from_clan_page,
    get_to_profile_page,
    wait_for_clash_main_menu,
)
from pyclashbot.detection.image_rec import (
    check_line_for_color,
    find_references,
    get_file_count,
    get_first_location,
    line_is_color,
    make_reference_image_list,
    pixel_is_equal,
    region_is_color,
)
from pyclashbot.memu.client import click, screenshot, scroll_up
from pyclashbot.utils.logger import Logger

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
POST_WAR_FIGHT_WAIT = 10  # seconds
WAR_BATTLE_TIMEOUT = 240


def find_war_battle_icon(vm_index):
    folder_name = "war_battle_icon"
    size = get_file_count(folder_name)
    names = make_reference_image_list(size)
    locations = find_references(
        screenshot(vm_index),
        folder_name,
        names,
        0.9,
    )
    coord = get_first_location(locations)
    if coord is None:
        return None
    return [coord[1], coord[0]]


def war_state(vm_index: int, logger: Logger, next_state: str):
    logger.change_status(status="War state")

    # if not on clash main: return
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            status="Error 4069852734098 Not on clash main to begin war state"
        )
        return "restart"

    logger.change_status(status="Making sure in a clan before war battle")
    in_a_clan_check = war_state_check_if_in_a_clan(vm_index, logger)

    if in_a_clan_check == "restart":
        logger.change_status(
            status="Error 502835 Failure while checking if in a clan before war battle"
        )
        return "restart"

    if not in_a_clan_check:
        logger.change_status(status="Not in a clan so skipping war...")

        return "no clan"

    # get to clan page
    logger.change_status(status="Starting a war battle")

    logger.log("Getting to clan tab")
    get_to_clan_tab_from_clash_main(vm_index, logger)

    # find battle icon
    logger.log("Finding a battle icon")
    find_and_click_war_battle_icon(vm_index, logger)
    time.sleep(3)

    # make deck if needed

    handle_make_deck(vm_index, logger)
    time.sleep(3)

    if not check_if_deck_is_ready_for_this_battle(vm_index):
        logger.change_status(status="No more war decks for today!")
        # click deadspace a little to close war battle windows
        click(
            vm_index,
            WAR_PAGE_DEADSPACE_COORD[0],
            WAR_PAGE_DEADSPACE_COORD[1],
            clicks=5,
            interval=0.3,
        )
        time.sleep(0.3)

        logger.change_status(status="Getting back to clash main")
        get_to_clash_main_from_clan_page(vm_index, logger)

        if wait_for_clash_main_menu(vm_index, logger) == "restart":
            logger.change_status(
                status="Erorr 7784278 failed to get to clash main after exhausting war battle decks"
            )
            return "restart"

        return next_state

    # start battle
    logger.change_status(status="Starting a war battle")
    click(vm_index, START_WAR_BATTLE_BUTTON_COORD[0], START_WAR_BATTLE_BUTTON_COORD[1])
    time.sleep(3)
    logger.add_war_fight()

    # wait for battle start
    wait_for_war_battle_start(vm_index, logger)

    # do fight
    if do_war_battle(vm_index, logger) == "restart":
        logger.change_status(status="Error 58734 Failed doing war battle")
        return "restart"
    logger.change_status(status=f"Done with war battle. Waiting {POST_WAR_FIGHT_WAIT}s")
    time.sleep(POST_WAR_FIGHT_WAIT)

    # when battle end, leave battle
    click(vm_index, LEAVE_WAR_BATTLE_BUTTON_COORD[0], LEAVE_WAR_BATTLE_BUTTON_COORD[1])

    if wait_for_war_page(vm_index, logger) == "restart":
        logger.change_status(status="Error 5135 Waited too long for war page")
        return "restart"

    if get_to_clash_main_from_clan_page(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 116135 Failed return to clash main after war battle"
        )
        return "restart"

    return next_state


def wait_for_war_page(vm_index, logger) -> Literal["restart", "good"]:
    logger.change_status(status="Waiting for war page")
    start_time: float = time.time()
    while not check_if_on_war_page(vm_index):
        time_taken: float = time.time() - start_time
        if time_taken > 45:
            logger.change_status(
                status="Error 1109572435 WAited too long for war page after leaving war battle"
            )
            return "restart"
    logger.log("Done waiting for war page")
    return "good"


def do_war_battle(vm_index, logger) -> Literal["restart", "good"]:
    start_time = time.time()
    logger.change_status(status="Starting war fighting")
    while check_if_in_war_battle(vm_index):
        time_taken = time.time() - start_time
        if time_taken > WAR_BATTLE_TIMEOUT:
            logger.change_status(status="Error 658725 Ran war fight loop too long")
            return "restart"

        # click a random card
        logger.change_status(status="Doing a random war play")

        random_card_coord = random.choice(CARD_COORDS)
        click(vm_index, random_card_coord[0], random_card_coord[1])
        time.sleep(1)

        # click a random play coord
        random_play_coord = (random.randint(63, 205), random.randint(55, 455))
        click(vm_index, random_play_coord[0], random_play_coord[1])
        time.sleep(2.4)
    logger.change_status(status="Done with this war fight")
    return "good"


def wait_for_war_battle_start(vm_index, logger) -> Literal["restart", "good"]:
    logger.change_status(status="Waiting for war battle start")

    start_time = time.time()

    while not check_if_in_war_battle(vm_index):
        time.sleep(3)

        time_taken = time.time() - start_time

        if time_taken > 45:
            logger.change_status(
                status="Error 98246572 Failure waiting for war battle start"
            )
            return "restart"

    logger.log("Waiting for war battle start")
    return "good"


def check_if_in_war_battle(vm_index) -> bool:
    if not check_line_for_color(
        vm_index, x_1=104, y_1=606, x_2=123, y_2=626, color=(224, 28, 215)
    ):
        return False
    if not line_is_color(
        vm_index, x_1=51, y_1=515, x_2=68, y_2=520, color=(255, 255, 255)
    ):
        return False

    return True


def check_if_deck_is_ready_for_this_battle(vm_index) -> bool:
    if not region_is_color(vm_index, [230, 398, 17, 6], (255, 200, 79)):
        return False
    if not region_is_color(vm_index, [240, 427, 30, 5], (255, 188, 43)):
        return False

    if not check_line_for_color(vm_index, 340, 161, 354, 162, (229, 36, 36)):
        return False
    return True


def handle_make_deck(vm_index, logger: Logger) -> Literal["good deck", "made deck"]:
    # if the deck is ready to go, just return
    if check_if_deck_is_ready_for_this_battle(vm_index):
        logger.log("Deck is good to go. No need to make a new one")

        return "good deck"

    logger.change_status(status="Setting up a deck for this war match")
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
    return "made deck"


def find_and_click_war_battle_icon(vm_index, logger):
    start_time = time.time()

    coord = None
    while coord is None:
        time_taken = time.time() - start_time
        if time_taken > 30:
            logger.log("Erorr 9528753 Failure findign a war battle icon")
            return "restart"

        click(vm_index, CLAN_PAGE_ICON_COORD[0], CLAN_PAGE_ICON_COORD[1])
        time.sleep(1.5)
        scroll_up(vm_index)
        time.sleep(1.5)

        coord = find_war_battle_icon(vm_index)

    click(vm_index, coord[0], coord[1])
    return "good"


def find_war_battle_icon_coords(vm_index):
    coord = find_battle_from_pix_list(get_war_battle_pix_list(vm_index))
    return coord


def find_battle_from_pix_list(pix_list):
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

        if index - index_of_last_bad > 15:
            result_coord = bool_datum["coord"]
            break

        index += 1

    return result_coord


def get_war_battle_pix_list(vm_index):
    data = []

    if not check_if_on_war_page(vm_index):
        return data

    iar = numpy.asarray(screenshot(vm_index))

    for y_index in range(182, 480):
        data.append(
            {
                "coord": (325, y_index),
                "color": iar[y_index][325],
            }
        )

    return data


def check_if_on_war_page(vm_index):
    if not check_line_for_color(
        vm_index, x_1=19, y_1=16, x_2=59, y_2=59, color=(144, 108, 255)
    ):
        return False
    if not check_line_for_color(
        vm_index, x_1=61, y_1=18, x_2=51, y_2=58, color=(144, 107, 255)
    ):
        return False
    if not check_line_for_color(
        vm_index, x_1=31, y_1=43, x_2=51, y_2=45, color=(226, 219, 228)
    ):
        return False

    if not region_is_color(vm_index, [225, 610, 25, 10], (80, 118, 153)):
        return False
    if not region_is_color(vm_index, [300, 610, 30, 14], (80, 118, 153)):
        return False

    return True


def war_state_check_if_in_a_clan(vm_index, logger: Logger):
    # get to profile page
    if get_to_profile_page(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 90723563485 Failure with get_to_profile_page"
        )
        return "restart"

    # check pixels for in a clan
    in_a_clan = war_state_check_pixels_for_clan_flag(vm_index)

    # click deadspace to leave
    click(vm_index, 15, 300)
    if wait_for_clash_main_menu(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 872356739 Failure with wait_for_clash_main_menu"
        )
        return "restart"

    return in_a_clan


def war_state_check_pixels_for_clan_flag(vm_index):
    iar = numpy.asarray(screenshot(vm_index))

    for x_index in range(78, 97):
        this_pixel = iar[446][x_index]
        if not pixel_is_equal([51, 51, 51], this_pixel, tol=25):
            return True

    for y_index in range(437, 455):
        this_pixel = iar[y_index][87]
        if not pixel_is_equal([51, 51, 51], this_pixel, tol=25):
            return True

    return False


if __name__ == "__main__":
    pass
