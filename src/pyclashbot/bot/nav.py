import random
import time
from typing import Literal

import numpy

from pyclashbot.detection.image_rec import (
    check_line_for_color,
    pixel_is_equal,
    region_is_color,
)
from pyclashbot.memu.client import click, screenshot, scroll_up
from pyclashbot.utils.logger import Logger
from pyclashbot.detection.image_rec import (
    make_reference_image_list,
    get_file_count,
    find_references,
    get_first_location,
)

_2V2_START_WAIT_TIMEOUT = 120  # s
CLAN_TAB_BUTTON_COORDS_FROM_MAIN = [315, 597]
PROFILE_PAGE_COORD = [88, 93]
CLASH_MAIN_COORD_FROM_CLAN_PAGE = [178, 593]
CLASH_MAIN_OPTIONS_BURGER_BUTTON = (390, 62)
BATTLE_LOG_BUTTON = (241, 43)
CARD_PAGE_ICON_FROM_CLASH_MAIN = (108, 598)
CARD_PAGE_ICON_FROM_CARD_PAGE = (147, 598)
CHALLENGES_TAB_ICON_FROM_CLASH_MAIN = (380, 598)
CLASH_MAIN_ICON_FROM_CARD_PAGE = (247, 601)
CARD_TAB_FROM_CLASH_MAIN = (105, 591)
SHOP_TAB_FROM_CARD_TAB = (29, 601)
CHALLENGES_TAB_FROM_SHOP_TAB = (385, 600)
CLASH_MAIN_TAB_FROM_CHALLENGES_TAB = (173, 591)
OK_BUTTON_COORDS_IN_TROPHY_REWARD_PAGE = (209, 599)
CLAN_PAGE_FROM_MAIN_TIMEOUT = 120  # seconds
CLAN_PAGE_FROM_MAIN_NAV_TIMEOUT = 240  # seconds
CLASH_MAIN_MENU_WAIT_TIMEOUT = 160  # seconds
CLASH_MAIN_MENU_DEADSPACE_COORD = (32, 364)
OPEN_WAR_CHEST_BUTTON_COORD = (188, 415)
OPENING_WAR_CHEST_DEADZONE_COORD = (5, 298)
CLASH_MAIN_WAIT_TIMEOUT = 240  # s
SHOP_PAGE_BUTTON: tuple[Literal[33], Literal[603]] = (33, 603)


def get_to_shop_page_from_clash_main(vm_index, logger):
    click(vm_index, SHOP_PAGE_BUTTON[0], SHOP_PAGE_BUTTON[1])
    if wait_for_clash_main_shop_page(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 085708235 Failure waiting for clash main shop page "
        )
        return False
    return True


def wait_for_end_battle_screen(
    vm_index, logger: Logger, printmode=False
) -> Literal["restart", "good"]:
    """
    Waits for the end battle screen to appear.

    Args:
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object.
        printmode (bool, optional): Whether to print status messages. Defaults to False.

    Returns:
        Literal["restart", "good"]: "restart" if the screen
        did not appear in time, "good" otherwise.
    """
    start_time: float = time.time()
    if printmode:
        logger.change_status(status="waiting for end 1v1 battle screen")
    else:
        logger.log(message="waiting for end 1v1 battle screen")
    while (
        (not check_for_end_1v1_battle_screen(vm_index=vm_index))
        and not (check_for_end_2v2_battle_screen(vm_index=vm_index))
        and not (check_for_end_2v2_battle_screen_2(vm_index))
    ):
        time_taken: float = time.time() - start_time
        if time_taken > 20:
            logger.change_status(
                status="Error 8734572456 Waiting too long for end battle screen"
            )
            return "restart"

    if printmode:
        logger.change_status(status="done waiting for end 1v1 battle screen")
    else:
        logger.log(message="done waiting for end 1v1 battle screen")
    return "good"


def check_for_end_2v2_battle_screen_2(vm_index) -> bool:
    """
    Checks if the virtual machine is on the end 2v2 battle screen.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if the virtual machine is on the end 2v2 battle screen, False otherwise.
    """
    if not check_line_for_color(vm_index, 46, 587, 46, 609, (76, 175, 255)):
        return False
    if not check_line_for_color(vm_index, 58, 591, 96, 608, (255, 255, 255)):
        return False
    if not check_line_for_color(vm_index, 106, 589, 105, 611, (76, 173, 255)):
        return False
    if not check_line_for_color(vm_index, 391, 26, 406, 26, (156, 20, 20)):
        return False

    return True


def wait_for_2v2_battle_start(vm_index, logger: Logger) -> Literal["restart", "good"]:
    """
    Waits for the 2v2 battle to start.

    Args:
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object.
        printmode (bool, optional): Whether to print the status. Defaults to False.

    Returns:
        Literal["restart", "good"]: "restart" if the function
        needs to be restarted, "good" otherwise.
    """

    _2v2_start_wait_start_time = time.time()

    while time.time() - _2v2_start_wait_start_time < _2V2_START_WAIT_TIMEOUT:
        time_taken = str(time.time() - _2v2_start_wait_start_time)[:4]
        logger.change_status(
            status=f"Waiting for 2v2 battle to start for {time_taken}s"
        )

        if check_if_in_battle(vm_index=vm_index):
            logger.change_status("Detected an ongoing 2v2 battle!")
            return True

        if random.randint(0, 2) == 1:
            click(vm_index=vm_index, x_coord=20, y_coord=200)

    return False


def wait_for_1v1_battle_start(
    vm_index, logger: Logger, printmode=False
) -> Literal["restart", "good"]:
    """
    Waits for the 1v1 battle to start.

    Args:
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object.
        printmode (bool, optional): Whether to print the status. Defaults to False.

    Returns:
        Literal["restart", "good"]: "restart" if the function
        needs to be restarted, "good" otherwise.
    """
    start_time: float = time.time()
    if printmode:
        logger.change_status(status="Waiting for 1v1 battle to start")
    else:
        logger.log(message="Waiting for 1v1 battle to start")
    while not check_if_in_battle(vm_index=vm_index):
        time_taken: float = time.time() - start_time
        if time_taken > 60:
            logger.change_status(
                status="Error 8734572456 Waiting too long for 1v1 battle to start"
            )
            return "restart"
        print("Waiting for 1v1 start")
        if random.randint(1, 3) == 3:
            click(vm_index=vm_index, x_coord=200, y_coord=200)

    if printmode:
        logger.change_status(status="Done waiting for 1v1 battle to start")
    else:
        logger.log(message="Done waiting for 1v1 battle to star")
    return "good"


def check_for_in_battle_with_delay(vm_index):
    """
    Checks if the virtual machine is in a 2v2 battle with a delay.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if the virtual machine is in a 2v2 battle, False otherwise.
    """
    timeout = 3  # s
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_if_in_battle(vm_index):
            return True
    return False


def check_if_in_battle(vm_index) -> bool:
    """
    Checks if the virtual machine is in a 2v2 battle.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if the virtual machine is in a 2v2 battle, False otherwise.
    """
    iar = numpy.asarray(screenshot(vm_index))

    pixels = [
        iar[517][56],
        iar[533][67],
        iar[616][115],
    ]

    colors = [
        [255, 255, 255],
        [255, 255, 255],
        [236, 91, 252],
    ]

    for index, pixel in enumerate(pixels):
        if not pixel_is_equal(pixel, colors[index], tol=55):
            return False

    return True


def get_to_clash_main_from_clan_page(
    vm_index, logger: Logger, printmode=False
) -> Literal["restart", "good"]:
    """
    Navigates to the clash main page from the clan page.

    Args:
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object.
        printmode (bool, optional): Whether to print the status. Defaults to False.

    Returns:
        Literal["restart", "good"]: "restart" if the function
        needs to be restarted, "good" otherwise.
    """
    if printmode:
        logger.change_status(status="Getting to clash main from clan page")
    else:
        logger.log(message="Getting to clash main from clan page")

    # click clash main coord
    if printmode:
        logger.change_status(status="Clicking clash main icon")
    else:
        logger.log(message="Clicking clash main icon")
    click(
        vm_index, CLASH_MAIN_COORD_FROM_CLAN_PAGE[0], CLASH_MAIN_COORD_FROM_CLAN_PAGE[1]
    )

    # wait for clash main menu
    if printmode:
        logger.change_status(status="Waiting for clash main")
    else:
        logger.log("Waiting for clash main")
    if wait_for_clash_main_menu(vm_index, logger) is False:
        logger.change_status(status="Error 3253, failure waiting for clash main")
        return "restart"
    return "good"


def open_war_chest_obstruction(vm_index, logger):
    """
    Opens a war chest obstruction if found on the way to getting to the clan page.

    Args:
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object.
    """
    logger.log("Found a war chest on the way to getting to the clan page.")
    logger.log("Opening this chest real quick")
    click(vm_index, OPEN_WAR_CHEST_BUTTON_COORD[0], OPEN_WAR_CHEST_BUTTON_COORD[1])
    time.sleep(2)
    click(
        vm_index,
        OPENING_WAR_CHEST_DEADZONE_COORD[0],
        OPENING_WAR_CHEST_DEADZONE_COORD[1],
        clicks=15,
        interval=1,
    )
    time.sleep(2)
    logger.log("Done opening this war chest")


def check_for_war_chest_obstruction(vm_index):
    """
    Checks if there is a war chest obstruction on the way to getting to the clan page.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if there is a war chest obstruction, False otherwise.
    """
    if not check_line_for_color(vm_index, 213, 409, 218, 423, (252, 195, 63)):
        return False
    if not check_line_for_color(vm_index, 156, 416, 164, 414, (255, 255, 255)):
        return False

    if not region_is_color(vm_index, [147, 410, 10, 17], (255, 188, 44)):
        return False
    return True


def collect_boot_reward(vm_index):
    # click boot reward location
    print("Opening boot reward")
    click(vm_index, 197, 370)

    # click deadspace a bunch
    print("Clicking deadspace to collect boot rewards")
    click(vm_index, 5, 200, clicks=20, interval=0.5)


def check_for_boot_reward(vm_index):
    """method to find the elixer price icon in a cropped image"""

    folder = "collect_war_boot"

    names = make_reference_image_list(get_file_count(folder))

    locations: list[list[int] | None] = find_references(
        screenshot(vm_index),
        folder,
        names,
        tolerance=0.52,
    )

    coord = get_first_location(locations)

    if coord is None:
        return None

    return [coord[1], coord[0]]


def get_to_clan_tab_from_clash_main(
    vm_index: int, logger: Logger
) -> Literal["restart", "good"]:
    """
    Navigates from the Clash Main page to the Clan Tab page.

    Args:
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object.

    Returns:
        Literal["restart", "good"]: "restart" if there is an error, "good" otherwise.
    """
    start_time = time.time()
    while 1:
        # timeout check
        time_taken = time.time() - start_time
        if time_taken > CLAN_PAGE_FROM_MAIN_NAV_TIMEOUT:
            logger.change_status(
                "Error 89572985 took too long to get to clan tab from clash main"
            )
            return "restart"

        # if boot exists, collect boot
        if check_for_boot_reward(vm_index):
            collect_boot_reward(vm_index)
            logger.add_war_chest_collect()
            print(f"Incremented war chest collects to {logger.war_chest_collects}")

        # check for a war chest obstructing the nav
        if check_for_war_chest_obstruction(vm_index):
            open_war_chest_obstruction(vm_index, logger)
            logger.add_war_chest_collect()
            print(f"Incremented war chest collects to {logger.war_chest_collects}")

        # if on the clan tab chat page, return
        if check_if_on_clan_chat_page(vm_index):
            break

        # if on clash main, click the clan tab button
        handle_clash_main_page_for_clan_page_navigation(vm_index)

        # if on final results page, click OK
        handle_final_results_page(vm_index, logger)

        # handle daily defenses rank page
        handle_war_popup_pages(vm_index, logger)

        if random.randint(0, 1) == 1:
            if random.randint(1, 3) == 1:
                scroll_up(vm_index)
                time.sleep(2)
                continue

        else:
            if random.randint(1, 3) == 1:
                click(
                    vm_index,
                    CLAN_TAB_BUTTON_COORDS_FROM_MAIN[0],
                    CLAN_TAB_BUTTON_COORDS_FROM_MAIN[1],
                )
                time.sleep(2)
                continue
        time.sleep(1)

    # if here, then done
    logger.log("Made it to the clan page from clash main")
    return "good"


def handle_war_popup_pages(vm_index, logger):
    timeout = 4
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_for_battle_day_results_page(vm_index):
            print("Found battle_day_results page")
            click(vm_index, 233, 196)
            time.sleep(1)
            return True

        if (
            check_for_daily_defenses_rank_page(vm_index)
            or check_for_daily_defenses_rank_page_2(vm_index)
            or check_for_daily_defenses_rank_page_3(vm_index)
            or check_for_daily_defenses_rank_page_4(vm_index)
        ):
            print("Found daily_defenses page")
            click(vm_index, 150, 260)
            time.sleep(2)
            logger.change_status("Handled daily defenses rank page")
            return True

        if check_for_war_chest_obstruction(vm_index):
            print("Found war chest obstruction")
            open_war_chest_obstruction(vm_index, logger)
            logger.add_war_chest_collect()
            print(f"Incremented war chest collects to {logger.war_chest_collects}")
            time.sleep(1)
            return True

    return False


def check_for_battle_day_results_page(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[189][48],
        iar[193][125],
        iar[194][236],
        iar[314][191],
        iar[206][203],
    ]

    colors = [
        [253, 79, 140],
        [255, 250, 253],
        [253, 251, 255],
        [204, 200, 196],
        [253, 79, 140],
    ]

    for i, p in enumerate(pixels):
        # print(p)
        if not pixel_is_equal(p, colors[i], tol=25):
            return False
    return True


def check_for_daily_defenses_rank_page_3(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[202][102],
        iar[203][139],
        iar[204][189],
        iar[203][230],
        iar[203][278],
        iar[262][209],
        iar[273][208],
    ]
    colors = [
        [251, 252, 251],
        [237, 236, 238],
        [253, 248, 249],
        [253, 251, 253],
        [248, 246, 242],
        [65, 214, 255],
        [38, 188, 250],
    ]

    for i, p in enumerate(pixels):
        # print(p)
        if not pixel_is_equal(p, colors[i], tol=15):
            return False
    return True


def check_for_daily_defenses_rank_page_4(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[201][101],
        iar[201][109],
        iar[201][176],
        iar[203][188],
    ]
    colors = [
        [254, 254, 254],
        [255, 255, 255],
        [255, 255, 255],
        [255, 255, 255],
    ]

    for i, p in enumerate(pixels):
        # print(p)
        if not pixel_is_equal(p, colors[i], tol=15):
            return False
    return True


def check_for_daily_defenses_rank_page_2(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[259][160],
        iar[273][144],
        iar[258][131],
        iar[258][285],
        iar[272][271],
        iar[258][256],
        iar[247][260],
    ]
    colors = [
        [61, 168, 233],
        [22, 119, 220],
        [39, 159, 229],
        [71, 168, 243],
        [37, 127, 222],
        [56, 173, 237],
        [67, 165, 238],
    ]

    for i, p in enumerate(pixels):
        # print(p)
        if not pixel_is_equal(p, colors[i], tol=25):
            return False
    return True


def check_for_daily_defenses_rank_page(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[523][81],
        iar[548][167],
        iar[549][237],
        iar[549][275],
        iar[548][200],
    ]
    colors = [
        [47, 29, 0],
        [88, 77, 40],
        [130, 117, 87],
        [50, 30, 0],
        [89, 74, 43],
    ]

    for i, p in enumerate(pixels):
        # print(p)
        if not pixel_is_equal(p, colors[i], tol=15):
            return False
    return True


def handle_clash_main_page_for_clan_page_navigation(vm_index) -> None:
    """
    Handles navigation from the Clash Main page to the Clan page.

    Args:
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object.

    Returns:
        None
    """
    if check_if_on_clash_main_menu(vm_index):
        click(
            vm_index,
            CLAN_TAB_BUTTON_COORDS_FROM_MAIN[0],
            CLAN_TAB_BUTTON_COORDS_FROM_MAIN[1],
        )


def handle_final_results_page(vm_index, logger) -> None:
    """
    Handles the final results page.

    Args:
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object.

    Returns:
        None
    """
    if check_for_final_results_page(vm_index):
        click(vm_index, 211, 524)
        logger.log("On final_results_page so clicking OK button")


def check_for_final_results_page(vm_index) -> bool:
    """
    Checks if the final results page is displayed on the screen.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if the final results page is displayed, False otherwise.
    """
    if not region_is_color(vm_index, [170, 527, 20, 18], (181, 96, 253)):
        return False
    if not region_is_color(vm_index, [227, 514, 18, 6], (192, 120, 252)):
        return False

    if not check_line_for_color(vm_index, 201, 518, 209, 528, (255, 255, 255)):
        return False
    if not check_line_for_color(vm_index, 213, 517, 215, 527, (255, 255, 255)):
        return False

    return True


def check_if_on_clan_chat_page(vm_index) -> bool:
    """
    Checks if the bot is on the clan chat page.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if the bot is on the clan chat page, False otherwise.
    """
    if not region_is_color(vm_index, [204, 537, 10, 8], (183, 96, 252)):
        return False
    if not region_is_color(vm_index, [352, 536, 16, 10], (76, 175, 255)):
        return False
    if not region_is_color(vm_index, [310, 612, 25, 12], (80, 118, 153)):
        return False
    return True


def check_if_on_profile_page(vm_index) -> bool:
    """
    Checks if the bot is on the profile page.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if the bot is on the profile page, False otherwise.
    """
    if not check_line_for_color(
        vm_index, x_1=329, y_1=188, x_2=339, y_2=195, color=(4, 244, 88)
    ):
        return False
    if not check_line_for_color(
        vm_index, x_1=169, y_1=50, x_2=189, y_2=50, color=(255, 222, 0)
    ):
        return False
    if not check_line_for_color(
        vm_index, x_1=369, y_1=63, x_2=351, y_2=71, color=(228, 36, 36)
    ):
        return False
    return True


def wait_for_profile_page(
    vm_index: int, logger: Logger, printmode: bool = False
) -> Literal["restart", "good"]:
    """
    Waits for the profile page to load.

    Args:
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object.
        printmode (bool, optional): Whether to print status messages. Defaults to False.

    Returns:
        Literal["restart", "good"]: "restart" if an error occurred, "good" otherwise.
    """
    if printmode:
        logger.change_status(status="Waiting for profile page")
    else:
        logger.log("Waiting for profile page")
    start_time = time.time()

    while not check_if_on_profile_page(vm_index):
        time_taken = time.time() - start_time
        if time_taken > 20:
            logger.change_status(
                status="Error 8734572456 Waiting too long for profile page"
            )
            return "restart"

    if printmode:
        logger.change_status(status="Done waiting for profile page")
    else:
        logger.log("Done waiting for profile page")
    return "good"


def get_to_profile_page(vm_index: int, logger: Logger) -> Literal["restart", "good"]:
    """
    Navigates to the profile page.

    Args:
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object.

    Returns:
        Literal["restart", "good"]: "restart" if an error occurred, "good" otherwise.
    """
    # if not on clash main, return
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(
            status="ERROR 732457256 Not on clash main menu, returning to start state"
        )
        return "restart"

    # click profile button
    click(vm_index, PROFILE_PAGE_COORD[0], PROFILE_PAGE_COORD[1])

    # wait for profile page
    if wait_for_profile_page(vm_index, logger, printmode=False) == "restart":
        logger.change_status(
            status="Error 0573085 Waited too long for clash profile page"
        )
        return "restart"
    return "good"


def check_for_trophy_reward_menu(vm_index) -> bool:
    """
    Checks if the user is on the trophy reward menu.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if on the trophy reward menu, False otherwise.
    """
    if not region_is_color(vm_index, region=[172, 599, 22, 12], color=(78, 175, 255)):
        return False
    if not region_is_color(vm_index, region=[226, 601, 18, 10], color=(78, 175, 255)):
        return False

    lines = [
        check_line_for_color(
            vm_index, x_1=199, y_1=590, x_2=206, y_2=609, color=(255, 255, 255)
        ),
        check_line_for_color(
            vm_index, x_1=211, y_1=590, x_2=220, y_2=609, color=(255, 255, 255)
        ),
    ]

    return all(lines)


def handle_trophy_reward_menu(
    vm_index, logger: Logger, printmode=False
) -> Literal["good"]:
    """
    Handles the trophy reward menu.

    Args:
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object.
        printmode (bool, optional): Whether to print status messages. Defaults to False.

    Returns:
        Literal["good"]: "good" if successful.
    """
    if printmode:
        logger.change_status(status="Handling trophy reward menu")
    else:
        logger.log("Handling trophy reward menu")
    click(
        vm_index,
        OK_BUTTON_COORDS_IN_TROPHY_REWARD_PAGE[0],
        OK_BUTTON_COORDS_IN_TROPHY_REWARD_PAGE[1],
    )
    time.sleep(1)

    return "good"





def wait_for_clash_main_menu(vm_index, logger: Logger, deadspace_click=True) -> bool:
    """
    Waits for the user to be on the clash main menu.
    Returns True if on main menu, prints the pixels if False then return False
    """
    start_time: float = time.time()
    while check_if_on_clash_main_menu(vm_index) is not True:
        # timeout check
        if time.time() - start_time > CLASH_MAIN_WAIT_TIMEOUT:
            logger.change_status("Timed out waiting for clash main")
            break

        # handle geting stuck on trophy road screen
        if check_for_trophy_reward_menu(vm_index):
            print("Handling trophy reward menu")
            handle_trophy_reward_menu(vm_index, logger)
            time.sleep(2)
            continue

        # click deadspace
        if deadspace_click and random.randint(0, 1) == 0:
            click(
                vm_index,
                CLASH_MAIN_MENU_DEADSPACE_COORD[0],
                CLASH_MAIN_MENU_DEADSPACE_COORD[1],
            )
        time.sleep(1)

    time.sleep(1)
    out = check_if_on_clash_main_menu(vm_index)
    if out is not True:
        print("Failed to get to clash main! Saw these pixels before restarting:")
        for pixel in out:
            print(pixel)
        print("\n")
        return False

    return True


def check_if_on_clash_main_menu3(vm_index):
    """A patch job for check_if_on_clash_main_menu()"""
    iar = numpy.asarray(screenshot(vm_index))

    # get raw pixels from image array
    pixels = [
        iar[26][209],
        iar[9][204],
        iar[10][216],
        iar[14][210],
        iar[9][319],
        iar[9][330],
        iar[25][319],
        iar[25][329],
        iar[14][324],
    ]

    # sentinel color list
    colors = [
        [37, 143, 18],
        [144, 232, 132],
        [132, 235, 130],
        [252, 253, 248],
        [140, 231, 137],
        [136, 235, 129],
        [36, 156, 16],
        [38, 155, 17],
        [255, 250, 249],
    ]

    # if any pixel doesnt match the sentinel, then we're not on clash main
    for i, pixel in enumerate(pixels):
        # print(pixel)
        if not pixel_is_equal(pixel, colors[i], tol=35):
            return pixels

    # if all pixels are good, we're on clash main
    return True


def check_if_on_clash_main_menu2(vm_index):
    """A patch job for check_if_on_clash_main_menu()"""
    iar = numpy.asarray(screenshot(vm_index))

    # get raw pixels from image array
    pixels = [
        iar[603][60],
        iar[622][167],
        iar[624][252],
        iar[587][339],
        iar[621][361],
        iar[598][302],
        iar[598][322],
    ]

    # sentinel color list
    colors = [
        [102, 81, 67],
        [154, 119, 80],
        [154, 119, 80],
        [108, 87, 73],
        [95, 76, 63],
        [241, 122, 19],
        [126, 77, 248],
    ]

    # if any pixel doesnt match the sentinel, then we're not on clash main
    for i, pixel in enumerate(pixels):
        # print(pixel)
        if not pixel_is_equal(pixel, colors[i], tol=35):
            return pixels

    # if all pixels are good, we're on clash main
    return True


def check_if_on_clash_main_menu(vm_index):
    """
    Checks if the user is on the clash main menu.
    Returns True if on main menu, False if not.
    """

    iar = numpy.asarray(screenshot(vm_index))

    # get raw pixels from image array
    pixels = [
        iar[15][298],
        iar[20][299],
        iar[16][401],
        iar[585][166],
        iar[622][165],
        iar[581][264],
        iar[71][269],
        iar[74][262],
    ]

    # sentinel color list
    colors = [
        [56, 162, 214],
        [49, 207, 238],
        [21, 189, 60],
        [139, 106, 73],
        [155, 121, 82],
        [138, 105, 71],
        [104, 75, 19],
        [105, 74, 19],
    ]

    # if any pixel doesnt match the sentinel, then we're not on clash main
    for i, pixel in enumerate(pixels):
        if not pixel_is_equal(pixel, colors[i], tol=35):
            return pixels

    # if all pixels are good, we're on clash main
    return True


def get_to_clash_main_from_card_page(
    vm_index, logger, printmode=False
) -> Literal["restart", "good"]:
    """
    Clicks on the Clash Main icon from the card page and waits for the Clash Main menu to appear.

    Args:
        vm_index (int): The index of the virtual machine to perform the action on.
        logger (Logger): The logger object to log messages to.
        printmode (bool, optional): Whether to print messages to the console. Defaults to False.

    Returns:
        Literal["restart", "good"]: Returns "restart" if there was an error, otherwise "good".
    """
    if printmode:
        logger.change_status(status="Getting to clash main from card page")
    else:
        logger.log("Getting to clash main from card page")

    # click clash main icon
    click(
        vm_index, CLASH_MAIN_ICON_FROM_CARD_PAGE[0], CLASH_MAIN_ICON_FROM_CARD_PAGE[1]
    )
    if wait_for_clash_main_menu(vm_index, logger) is False:
        logger.change_status(
            status="error 08572380572308 Failure gettting to clash main from card page"
        )
        return "restart"
    return "good"


def get_to_card_page_from_clash_main(
    vm_index: int, logger: Logger, printmode: bool = False
) -> Literal["restart", "good"]:
    """
    Clicks on the card page icon from the clash main screen and waits until the card page is loaded.
    If the card page is not loaded within 60 seconds, returns "restart".
    If the card page is loaded within 60 seconds, returns "good".

    Args:
    - vm_index (int): The index of the virtual machine to perform the action on.
    - logger (Logger): The logger object to log the action.
    - printmode (bool, optional): If True, changes the logger status instead of logging.

    Returns:
    - Literal["restart", "good"]: Returns "restart" if the card page is not loaded
    within 60 seconds, "good" otherwise.
    """
    start_time = time.time()

    if printmode:
        logger.change_status(status="Getting to card page from clash main")
    else:
        logger.log("Getting to card page from clash main")

    # click card page icon
    click(
        vm_index, CARD_PAGE_ICON_FROM_CLASH_MAIN[0], CARD_PAGE_ICON_FROM_CLASH_MAIN[1]
    )
    time.sleep(2.5)

    # while not on the card page, cycle the card page
    while not check_if_on_card_page(vm_index):
        time_taken = time.time() - start_time
        if time_taken > 60:
            return "restart"

        click(
            vm_index, CARD_PAGE_ICON_FROM_CARD_PAGE[0], CARD_PAGE_ICON_FROM_CARD_PAGE[1]
        )
        time.sleep(2)

    if printmode:
        logger.change_status(status="Made it to card page")
    else:
        logger.log("Made it to card page")
    return "good"


def check_if_on_card_page2(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[115][158],
        iar[117][245],
        iar[120][207],
        iar[476][57],
    ]

    colors = [
        [129, 78, 32],
        [225, 200, 177],
        [189, 179, 179],
        [235, 1, 240],
    ]

    for i, p in enumerate(pixels):
        # print(p)
        if not pixel_is_equal(p, colors[i], tol=15):
            return False
    return True


def check_if_on_card_page3(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[477][57],
        iar[126][35],
        iar[126][329],
    ]

    colors = [
        [237, 0, 245],
        [201, 81, 1],
        [201, 82, 0],
    ]

    for i, p in enumerate(pixels):
        # print(p)
        if not pixel_is_equal(p, colors[i], tol=15):
            return False
    return True


def check_if_on_card_page(vm_index) -> bool:
    """
    Checks if the bot is currently on the card page by looking for
    specific colors in certain regions of the screen.

    Args:
        vm_index (int): The index of the virtual machine to check.

    Returns:
        bool: True if the bot is on the card page, False otherwise.
    """

    # some pixel checks for card pages of newer accounts
    if check_if_on_card_page2(vm_index):
        return True

    if check_if_on_card_page3(vm_index):
        return True

    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[110][294],
        iar[137][317],
        iar[117][310],
        iar[479][56],
        iar[485][56],
    ]

    colors = [
        [150, 62, 4],
        [165, 75, 2],
        [255, 238, 230],
        [232, 0, 248],
        [214, 2, 226],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(colors[i], p, tol=15):
            return False

    return True


def get_to_challenges_tab_from_main(vm_index, logger) -> Literal["restart", "good"]:
    """
    Clicks on the challenges tab in the Clash Main menu to navigate to the challenges tab.

    Args:
        vm_index (int): The index of the virtual machine to perform the clicks on.
        logger (Logger): The logger object to log messages to.

    Returns:
        Literal["restart", "good"]: "restart" if an error occurred and the VM needs to be restarted,
        "good" otherwise.
    """
    click(
        vm_index,
        CHALLENGES_TAB_ICON_FROM_CLASH_MAIN[0],
        CHALLENGES_TAB_ICON_FROM_CLASH_MAIN[1],
    )
    if wait_for_clash_main_challenges_tab(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 892572938 waited for challenges tab too long, restarting vm"
        )
        return "restart"
    return "good"


def handle_clash_main_tab_notifications(
    vm_index, logger: Logger
) -> Literal["restart", "good"]:
    """
    Clicks on the card, shop, and challenges tabs in the Clash Main menu to handle notifications.

    Args:
        vm_index (int): The index of the virtual machine to perform the clicks on.
        logger (Logger): The logger object to log messages to.

    Returns:
        Literal["restart", "good"]: "restart" if an error occurred and the VM needs to be restarted,
        "good" otherwise.
    """
    start_time: float = time.time()

    # wait for clash main to appear
    if wait_for_clash_main_menu(vm_index, logger) is False:
        logger.change_status(
            status="Error 246246 Waited too long for clash main menu, restarting vm"
        )
        return False

    # click card tab from main
    print("Clicked card tab")
    click(vm_index, 103, 598)
    time.sleep(3)

    # click shop tab from card tab
    print("Clicked shop tab")
    click(vm_index, 9, 594, clicks=3, interval=0.33)
    time.sleep(2)

    # click clan tab from shop tab
    print("Clicked clan tab")
    click(vm_index, 315, 594)
    time.sleep(5)



    # click events tab from clan tab
    print("Getting to events tab...")
    while not check_for_events_page(vm_index):
        print("Still not on events page...")
        handle_war_popup_pages(vm_index, logger)

        print('Trying to get to events page...')
        click(vm_index, 408, 600)
        time.sleep(1.77)

    print("On events page")

    time.sleep(2)

    # spam click shop page at the leftmost location, wait a little bit
    print("Clicked shop page")
    click(vm_index, 9, 594, clicks=3, interval=0.33)
    time.sleep(3)

    # click clash main from shop page
    print("Clicked clash main")
    click(vm_index, 240, 600)
    time.sleep(3)

    # handle possibility of trophy road obstructing clash main
    if check_for_trophy_reward_menu(vm_index):
        handle_trophy_reward_menu(vm_index, logger)
        time.sleep(2)

    # wait for clash main to appear
    if wait_for_clash_main_menu(vm_index, logger) is False:
        logger.change_status(
            status="Error 47 Waited too long for clash main menu, restarting vm"
        )
        return False

    logger.change_status(
        status=f"Handled clash main notifications in {str(time.time() - start_time)[:5]}s"
    )

    return True


def check_for_events_page(vm_index):
    iar = numpy.asarray(screenshot(vm_index))

    pixels = [
        iar[578][415],
        iar[585][415],
        iar[595][415],
        iar[605][415],
        iar[621][415],
        iar[578][310],
        iar[585][310],
        iar[590][310],
        iar[600][310],
        iar[610][310],
        iar[622][310],
    ]

    colors = [
        [136, 103, 70],
        [136, 103, 70],
        [140, 107, 74],
        [142, 110, 75],
        [149, 117, 77],
        [139, 101, 69],
        [138, 103, 70],
        [141, 106, 73],
        [142, 108, 73],
        [147, 114, 76],
        [154, 119, 80],
    ]

    # for p in pixels:print(p)

    for i, p in enumerate(pixels):
        # print(p)
        if not pixel_is_equal(colors[i], p, tol=15):
            return False
    return True


def wait_for_clash_main_challenges_tab(
    vm_index, logger: Logger, printmode=False
) -> Literal["restart", "good"]:
    """
    Waits for the Clash Main menu to be on the challenges tab.

    Args:
        vm_index (int): The index of the virtual machine to check the menu on.
        logger (Logger): The logger object to log messages to.
        printmode (bool, optional): Whether to print status messages to the logger. Defaults to
        False.

    Returns:
        Literal["restart", "good"]: "restart" if an error occurred and the VM needs to be restarted,
        "good" otherwise.
    """
    start_time: float = time.time()

    if printmode:
        logger.change_status(status="Waiting for clash main challenges tab")
    else:
        logger.log("Waiting for clash main challenges tab")
    while not check_if_on_clash_main_challenges_tab(vm_index):
        if time.time() - start_time > 10:
            logger.change_status(
                status="Error 8884613 Waited too long for clash main challenges tab"
            )
            return "restart"

    if printmode:
        logger.change_status(status="Done waiting for clash main challenges tab")
    else:
        logger.log("Done waiting for clash main challenges tab")
    return "good"


def check_if_on_clash_main_challenges_tab(vm_index) -> bool:
    """
    Checks if the Clash Main menu is on the challenges tab.

    Args:
        vm_index (int): The index of the virtual machine to check the menu on.

    Returns:
        bool: True if the menu is on the challenges tab, False otherwise.
    """
    if not region_is_color(vm_index, [380, 580, 30, 45], (76, 111, 145)):
        return False
    if not region_is_color(vm_index, [290, 610, 25, 15], (80, 118, 153)):
        return False

    return True


def check_if_on_clash_main_shop_page(vm_index) -> bool:
    """
    Check if the bot is currently on the main shop page in the Clash of Clans game.

    Args:
        vm_index (int): The index of the virtual machine to use for image recognition.

    Returns:
        bool: True if the bot is on the main shop page, False otherwise.
    """
    if not region_is_color(vm_index, region=[9, 580, 30, 45], color=(76, 112, 146)):
        return False

    if not region_is_color(vm_index, region=[90, 580, 18, 40], color=(75, 111, 146)):
        return False

    lines = [
        check_line_for_color(
            vm_index, x_1=393, y_1=7, x_2=414, y_2=29, color=(44, 144, 21)
        ),
        check_line_for_color(
            vm_index, x_1=48, y_1=593, x_2=83, y_2=594, color=(102, 236, 56)
        ),
    ]

    return all(lines)


def wait_for_clash_main_shop_page(
    vm_index, logger: Logger
) -> Literal["restart", "good"]:
    """
    Wait for the bot to navigate to the main shop page in the Clash of Clans game.

    Args:
        vm_index (int): The index of the virtual machine to use for image recognition.
        logger (Logger): The logger object to use for logging messages.
        printmode (bool, optional): Whether to print status
        messages to the console. Defaults to False.

    Returns:
        Literal["restart", "good"]: "restart" if the bot needs to be restarted, "good" otherwise.
    """
    start_time = time.time()
    while not check_if_on_clash_main_shop_page(vm_index):
        time_taken = time.time() - start_time
        if time_taken > 20:
            logger.change_status(
                status="Error 764527546 Waiting too long for clash main shop page"
            )
            return "restart"

    return "good"


def get_to_activity_log(
    vm_index: int, logger: Logger, printmode: bool = False
) -> Literal["restart", "good"]:
    """
    Navigates to the activity log page in the Clash of Clans game.

    Args:
        vm_index (int): The index of the virtual machine to use.
        logger (Logger): The logger object to use for logging.
        printmode (bool, optional): Whether to print status messages. Defaults to False.

    Returns:
        Literal["restart", "good"]: Returns "restart" if there was an
        error and the VM needs to be restarted, otherwise returns "good".
    """
    if printmode:
        logger.change_status(status="Getting to activity log")
    else:
        logger.log("Getting to activity log")

    # if not on main return restart
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(
            status="Eror 08752389 Not on clash main menu, restarting vm"
        )
        return "restart"

    # click clash main burger options button
    if printmode:
        logger.change_status(status="Opening clash main options menu")
    else:
        logger.log("Opening clash main options menu")
    click(
        vm_index,
        CLASH_MAIN_OPTIONS_BURGER_BUTTON[0],
        CLASH_MAIN_OPTIONS_BURGER_BUTTON[1],
    )
    if wait_for_clash_main_burger_button_options_menu(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 99993 Waited too long for calsh main options menu, restarting vm"
        )
        return "restart"

    # click battle log button
    if printmode:
        logger.change_status(status="Clicking activity log button")
    else:
        logger.log("Clicking activity log button")
    click(vm_index, BATTLE_LOG_BUTTON[0], BATTLE_LOG_BUTTON[1])
    wait_for_battle_log_page(vm_index, logger, printmode)

    return "good"


def wait_for_battle_log_page(
    vm_index, logger: Logger, printmode=False
) -> Literal["restart", "good"]:
    """
    Waits for the battle log page to appear.

    Args:
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object.
        printmode (bool, optional): Whether to print status messages. Defaults to False.

    Returns:
        Literal["restart", "good"]: "restart" if the page did
        not appear within 20 seconds, "good" otherwise.
    """
    start_time = time.time()
    if printmode:
        logger.change_status(status="Waiting for battle log page to appear")
    else:
        logger.log("Waiting for battle log page to appear")
    while not check_if_on_battle_log_page(vm_index):
        time_taken = time.time() - start_time
        if time_taken > 20:
            logger.change_status(
                status="Error 2457245645 Waiting too long for battle log page"
            )
            return "restart"

    if printmode:
        logger.change_status(status="Done waiting for battle log page to appear")
    else:
        logger.log("Done waiting for battle log page to appear")

    return "good"


def check_if_on_battle_log_page(vm_index) -> bool:
    """
    Checks if the virtual machine is on the battle log page.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if the virtual machine is on the battle log page, False otherwise.
    """
    line1 = check_line_for_color(
        vm_index, x_1=353, y_1=62, x_2=376, y_2=83, color=(231, 28, 28)
    )
    line2 = check_line_for_color(
        vm_index, x_1=154, y_1=64, x_2=173, y_2=83, color=(255, 255, 255)
    )
    line3 = check_line_for_color(
        vm_index, x_1=248, y_1=67, x_2=262, y_2=83, color=(255, 255, 255)
    )
    line4 = check_line_for_color(
        vm_index, x_1=9, y_1=208, x_2=27, y_2=277, color=(11, 45, 67)
    )

    if line1 and line2 and line3 and line4:
        return True
    return False


def check_if_on_clash_main_burger_button_options_menu(vm_index) -> bool:
    """
    Checks if the virtual machine is on the clash main burger button options menu.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if the virtual machine is on the clash main burger
        button options menu, False otherwise.
    """
    if (
        check_line_for_color(
            vm_index, x_1=182, y_1=78, x_2=208, y_2=101, color=(46, 152, 252)
        )
        and check_line_for_color(
            vm_index, x_1=184, y_1=196, x_2=206, y_2=215, color=(46, 152, 252)
        )
        and check_line_for_color(
            vm_index, x_1=182, y_1=360, x_2=210, y_2=384, color=(24, 144, 252)
        )
        and check_line_for_color(
            vm_index, x_1=182, y_1=128, x_2=208, y_2=151, color=(45, 151, 252)
        )
    ):
        return True
    return False


def wait_for_clash_main_burger_button_options_menu(
    vm_index: int, logger: Logger, printmode: bool = False
) -> Literal["restart", "good"]:
    """
    Waits for the virtual machine to be on the clash main burger button options menu.

    Args:
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object to use for logging.
        printmode (bool, optional): Whether to print status messages. Defaults to False.

    Returns:
        Literal["restart", "good"]: "restart" if the function timed
        out and needs to be restarted, "good" otherwise.
    """
    start_time = time.time()

    if printmode:
        logger.change_status(status="Waiting for clash main options menu to appear")
    else:
        logger.log("Waiting for clash main options menu to appear")
    while not check_if_on_clash_main_burger_button_options_menu(vm_index):
        time_taken = time.time() - start_time
        if time_taken > 20:
            logger.change_status(
                status="Error 57245645362 Waiting too long for clash main options menu to appear"
            )
            return "restart"
    if printmode:
        logger.change_status(
            status="Done waiting for clash main options menu to appear"
        )
    else:
        logger.log("Done waiting for clash main options menu to appear")
    return "good"


def check_for_end_1v1_battle_screen(vm_index) -> bool:
    """
    Checks if the virtual machine is on the end 1v1 battle screen.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if the virtual machine is on the end 1v1 battle screen, False otherwise.
    """
    line1 = check_line_for_color(
        vm_index, x_1=52, y_1=515, x_2=78, y_2=532, color=(255, 255, 255)
    )
    line2 = check_line_for_color(
        vm_index, x_1=173, y_1=555, x_2=194, y_2=564, color=(78, 175, 255)
    )
    line3 = check_line_for_color(
        vm_index, x_1=198, y_1=545, x_2=222, y_2=562, color=(255, 255, 255)
    )

    if line1 and line2 and line3:
        return True
    return False


def check_for_end_2v2_battle_screen(vm_index) -> bool:
    """
    Checks if the virtual machine is on the end 2v2 battle screen.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if the virtual machine is on the end 2v2 battle screen, False otherwise.
    """
    if not region_is_color(vm_index, [44, 590, 5, 6], (104, 188, 255)):
        return False
    if not region_is_color(vm_index, [355, 600, 17, 5], (76, 176, 255)):
        return False
    return True


if __name__ == "__main__":
    handle_war_popup_pages(12, Logger(None, None))
