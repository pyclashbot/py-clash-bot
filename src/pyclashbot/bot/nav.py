import time
from typing import Any, Literal

import numpy

from pyclashbot.detection.image_rec import (
    check_line_for_color,
    pixel_is_equal,
    region_is_color,
)
from pyclashbot.memu.client import click, screenshot, scroll_up
from pyclashbot.utils.logger import Logger

CLAN_TAB_BUTTON_COORDS_FROM_MAIN: list[int] = [
    315,
    597,
]  # coords of clan tab icon on the bottom of the clash main menu, when on the clash main menu

PROFILE_PAGE_COORD: list[int] = [88, 93]
CLASH_MAIN_COORD_FROM_CLAN_PAGE: list[int] = [178, 593]

CLASH_MAIN_OPTIONS_BURGER_BUTTON: tuple[Literal[365], Literal[62]] = (365, 62)
BATTLE_LOG_BUTTON: tuple[Literal[241], Literal[43]] = (241, 43)


CARD_PAGE_ICON_FROM_CLASH_MAIN: tuple[Literal[108], Literal[598]] = (108, 598)
CARD_PAGE_ICON_FROM_CARD_PAGE: tuple[Literal[147], Literal[598]] = (147, 598)
CHALLENGES_TAB_ICON_FROM_CLASH_MAIN: tuple[Literal[380], Literal[598]] = (380, 598)

CLASH_MAIN_ICON_FROM_CARD_PAGE: tuple[Literal[247], Literal[601]] = (247, 601)

CARD_TAB_FROM_CLASH_MAIN: tuple[Literal[105], Literal[591]] = (105, 591)
SHOP_TAB_FROM_CARD_TAB: tuple[Literal[29], Literal[601]] = (29, 601)
CHALLENGES_TAB_FROM_SHOP_TAB: tuple[Literal[385], Literal[600]] = (385, 600)
CLASH_MAIN_TAB_FROM_CHALLENGES_TAB: tuple[Literal[173], Literal[591]] = (173, 591)
OK_BUTTON_COORDS_IN_TROPHY_REWARD_PAGE: tuple[Literal[209], Literal[599]] = (209, 599)


def get_to_main_from_challenges_tab(vm_index, logger, printmode=False):
    if printmode:
        logger.change_status(status="Getting to main from challenges tab")
    else:
        logger.log("Getting to main from challenges tab")

    click(
        vm_index,
        CLASH_MAIN_TAB_FROM_CHALLENGES_TAB[0],
        CLASH_MAIN_TAB_FROM_CHALLENGES_TAB[1],
    )

    if wait_for_clash_main_menu(vm_index, logger) == "restart":
        if printmode:
            logger.change_status(
                "Erorr 356325 Failed to get to main from challenges tab"
            )
        else:
            logger.log("Erorr 356325 Failed to get to main from challenges tab")
    return "good"


def get_to_clash_main_from_card_page(
    vm_index, logger, printmode=False
) -> Literal["restart", "good"]:
    if printmode:
        logger.change_status(status="Getting to clash main from card page")
    else:
        logger.log("Getting to clash main from card page")

    # click clash main icon
    click(
        vm_index, CLASH_MAIN_ICON_FROM_CARD_PAGE[0], CLASH_MAIN_ICON_FROM_CARD_PAGE[1]
    )
    if wait_for_clash_main_menu(vm_index, logger) == "restart":
        logger.change_status(
            status="error 08572380572308 Failure gettting to clash main from card page"
        )
        return "restart"
    return "good"


def get_to_card_page_from_clash_main(
    vm_index, logger, printmode=False
) -> Literal["restart", "good"]:
    start_time = time.time()

    if printmode:
        logger.change_status(status="Getting to card page from clash main")
    else:
        logger.log("Getting to card page from clash main")

    # click card page icon
    click(
        vm_index, CARD_PAGE_ICON_FROM_CLASH_MAIN[0], CARD_PAGE_ICON_FROM_CLASH_MAIN[1]
    )
    time.sleep(1)

    # while not on the card page, cycle the card page
    while not check_if_on_card_page(vm_index):
        time_taken = time.time() - start_time
        if time_taken > 60:
            return "restart"

        click(
            vm_index, CARD_PAGE_ICON_FROM_CARD_PAGE[0], CARD_PAGE_ICON_FROM_CARD_PAGE[1]
        )
        time.sleep(1)

    if printmode:
        logger.change_status(status="Made it to card page")
    else:
        logger.log("Made it to card page")
    return "good"


def check_if_on_card_page(vm_index) -> bool:
    if not region_is_color(vm_index, region=[75, 579, 31, 11], color=(73, 105, 139)):
        return False
    if not region_is_color(vm_index, region=[170, 577, 29, 10], color=(72, 105, 138)):
        return False

    lines = [
        check_line_for_color(
            vm_index, x_1=393, y_1=9, x_2=410, y_2=29, color=(66, 198, 24)
        ),
        check_line_for_color(
            vm_index, x_1=67, y_1=54, x_2=99, y_2=84, color=(96, 196, 255)
        ),
    ]

    return all(lines)


def wait_for_switch_accounts_page(
    vm_index, logger: Logger, printmode=False
) -> Literal["restart", "good"]:
    start_time: float = time.time()
    if printmode:
        logger.change_status(status="Waiting for switch accounts page")
    else:
        logger.log("Waiting for switch accounts page")
    while not check_for_switch_accounts_page(vm_index):
        time_taken = time.time() - start_time
        if time_taken > 20:
            logger.change_status(
                status="Error 368375367 Waited too long for switch accounts page"
            )
            return "restart"
    if printmode:
        logger.change_status(status="Done waiting for switch accounts page")
    else:
        logger.log("Done waiting for switch accounts page")
    return "good"


def check_for_switch_accounts_page(vm_index) -> bool:
    if not region_is_color(vm_index, region=[255, 108, 7, 5], color=(255, 255, 255)):
        return False

    if not check_line_for_color(
        vm_index, x_1=127, y_1=232, x_2=171, y_2=232, color=(47, 243, 198)
    ):
        return False

    if not check_line_for_color(
        vm_index, x_1=155, y_1=221, x_2=154, y_2=244, color=(47, 244, 199)
    ):
        return False

    if not check_line_for_color(
        vm_index, x_1=381, y_1=46, x_2=398, y_2=64, color=(255, 255, 255)
    ):
        return False

    if not check_line_for_color(
        vm_index, x_1=398, y_1=46, x_2=381, y_2=63, color=(255, 255, 255)
    ):
        return False

    return True


def get_to_challenges_tab_from_main(vm_index, logger) -> Literal["restart", "good"]:
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
    vm_index, logger: Logger, printmode=False
) -> Literal["restart", "good"]:
    start_time = time.time()

    # if not on clash main, return restart
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            status="Error 08725652389 Not on clash main menu for open chests state, restarting vm"
        )
        return "restart"

    # click card tab
    click(vm_index, CARD_TAB_FROM_CLASH_MAIN[0], CARD_TAB_FROM_CLASH_MAIN[1])
    if wait_for_clash_main_card_page(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 0675248 Waited too long for clash main card page, restarting vm"
        )
        return "restart"

    # click shop tab
    click(vm_index, SHOP_TAB_FROM_CARD_TAB[0], SHOP_TAB_FROM_CARD_TAB[1])
    if wait_for_clash_main_shop_page(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 086720845 Waited too long for clash main shop page, restarting vm"
        )
        return "restart"

    # click challenges tab
    click(vm_index, CHALLENGES_TAB_FROM_SHOP_TAB[0], CHALLENGES_TAB_FROM_SHOP_TAB[1])
    if wait_for_clash_main_challenges_tab(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 922225 Waited too long for clash main challenged tab page, restarting vm"
        )

        return "restart"

    # get back to main
    click(
        vm_index,
        CLASH_MAIN_TAB_FROM_CHALLENGES_TAB[0],
        CLASH_MAIN_TAB_FROM_CHALLENGES_TAB[1],
    )
    if wait_for_clash_main_menu(vm_index, logger, printmode=False) == "restart":
        logger.change_status(
            status="Error 358971935813 Waited too long for clash main menu, restarting vm"
        )
        return "restart"

    if printmode:
        logger.change_status(
            status=f"Handled clash main notifications in {str(time.time() - start_time)[:5]}s"
        )
    else:
        logger.log(
            f"Handled clash main notifications in {str(time.time() - start_time)[:5]}s"
        )
    time.sleep(3)
    return "good"


def wait_for_clash_main_challenges_tab(
    vm_index, logger: Logger, printmode=False
) -> Literal["restart", "good"]:
    start_time = time.time()

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
    if not region_is_color(vm_index, [380, 580, 30, 45], (76, 111, 145)):
        return False
    if not region_is_color(vm_index, [290, 610, 25, 15], (80, 118, 153)):
        return False

    return True


def wait_for_clash_main_card_page(
    vm_index, logger: Logger, printmode=False
) -> Literal["restart", "good"]:
    start_time = time.time()

    if printmode:
        logger.change_status(status="Waiting for clash main card page")
    else:
        logger.log("Waiting for clash main card page")
    while not check_if_on_clash_main_card_page(vm_index):
        time_taken = time.time() - start_time
        if time_taken > 20:
            logger.change_status(
                status="Error 23958623975 Waiting too long for clash main card page"
            )
            return "restart"

    if printmode:
        logger.change_status(status="Done waiting for clash main card page")
    else:
        logger.log("Done waiting for clash main card page")
    return "good"


def check_if_on_clash_main_card_page(vm_index) -> bool:
    if not region_is_color(vm_index, region=[14, 45, 20, 20], color=(13, 56, 105)):
        return False

    if not region_is_color(vm_index, region=[80, 575, 25, 13], color=(71, 105, 138)):
        return False

    lines = [
        check_line_for_color(
            vm_index, x_1=388, y_1=16, x_2=415, y_2=17, color=(60, 189, 21)
        ),
        check_line_for_color(
            vm_index, x_1=4, y_1=5, x_2=28, y_2=26, color=(25, 177, 255)
        ),
    ]
    return all(lines)


def check_if_on_clash_main_shop_page(vm_index) -> bool:
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
    vm_index, logger: Logger, printmode=False
) -> Literal["restart", "good"]:
    start_time = time.time()
    if printmode:
        logger.change_status(status="Waiting for clash main shop page")
    else:
        logger.log("Waiting for clash main shop page")
    while not check_if_on_clash_main_shop_page(vm_index):
        time_taken = time.time() - start_time
        if time_taken > 20:
            logger.change_status(
                status="Error 764527546 Waiting too long for clash main shop page"
            )
            return "restart"
    if printmode:
        logger.change_status(status="Done waiting for clash main shop page")
    else:
        logger.log("Done waiting for clash main shop page")
    return "good"


def get_to_activity_log(
    vm_index, logger: Logger, printmode=False
) -> Literal["restart", "good"]:
    if printmode:
        logger.change_status(status="Getting to activity log")
    else:
        logger.log("Getting to activity log")

    # if not on main return restart
    if not check_if_on_clash_main_menu(vm_index):
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
    wait_for_battle_log_page(vm_index, logger)

    return "good"


def wait_for_battle_log_page(
    vm_index, logger: Logger, printmode=False
) -> Literal["restart", "good"]:
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
    if (
        check_line_for_color(
            vm_index, x_1=182, y_1=78, x_2=208, y_2=101, color=(208, 144, 43)
        )
        and check_line_for_color(
            vm_index, x_1=184, y_1=196, x_2=206, y_2=215, color=(255, 255, 255)
        )
        and check_line_for_color(
            vm_index, x_1=182, y_1=360, x_2=210, y_2=384, color=(255, 255, 255)
        )
        and check_line_for_color(
            vm_index, x_1=182, y_1=128, x_2=208, y_2=151, color=(192, 135, 80)
        )
    ):
        return True
    return False


def wait_for_clash_main_burger_button_options_menu(
    vm_index, logger: Logger, printmode=False
):
    start_time = time.time()

    if printmode:
        logger.change_status(status="Waiting for clash main optinos menu to appear")
    else:
        logger.log("Waiting for clash main optinos menu to appear")
    while not check_if_on_clash_main_burger_button_options_menu(vm_index):
        time_taken = time.time() - start_time
        if time_taken > 20:
            logger.change_status(
                status="Error 57245645362 Waiting too long for clash main optinos menu to appear"
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
    if not region_is_color(vm_index, [44, 590, 5, 6], (104, 188, 255)):
        return False
    if not region_is_color(vm_index, [355, 600, 17, 5], (76, 176, 255)):
        return False
    return True


def wait_for_end_battle_screen(
    vm_index, logger: Logger, printmode=False
) -> Literal["restart", "good"]:
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
    if not check_line_for_color(vm_index, 46, 587, 46, 609, (76, 175, 255)):
        return False
    if not check_line_for_color(vm_index, 58, 591, 96, 608, (255, 255, 255)):
        return False
    if not check_line_for_color(vm_index, 106, 589, 105, 611, (76, 173, 255)):
        return False
    if not check_line_for_color(vm_index, 391, 26, 406, 26, (156, 20, 20)):
        return False

    return True


def wait_for_2v2_battle_start(
    vm_index, logger: Logger, printmode=False
) -> Literal["restart", "good"]:
    start_time: float = time.time()
    if printmode:
        logger.change_status(status="Waiting for 2v2 battle to start")
    else:
        logger.log(message="Waiting for 2v2 battle to start")
    while not check_for_in_2v2_battle(vm_index=vm_index):
        time_taken: float = time.time() - start_time
        if time_taken > 60:
            logger.change_status(
                status="Error 88884572456 Waiting too long for 1v1 battle to start"
            )
            return "restart"

        click(vm_index=vm_index, x_coord=200, y_coord=200)
        time.sleep(1)

    if printmode:
        logger.change_status(status="Done waiting for 2v2 battle to start")
    else:
        logger.log(message="Done waiting for 2v2 battle to star")
    return "good"


def wait_for_1v1_battle_start(
    vm_index, logger: Logger, printmode=False
) -> Literal["restart", "good"]:
    start_time: float = time.time()
    if printmode:
        logger.change_status(status="Waiting for 1v1 battle to start")
    else:
        logger.log(message="Waiting for 1v1 battle to start")
    while not check_for_in_1v1_battle(vm_index=vm_index):
        time_taken: float = time.time() - start_time
        if time_taken > 60:
            logger.change_status(
                status="Error 8734572456 Waiting too long for 1v1 battle to start"
            )
            return "restart"

        click(vm_index=vm_index, x_coord=200, y_coord=200)
        time.sleep(1)

    if printmode:
        logger.change_status(status="Done waiting for 1v1 battle to start")
    else:
        logger.log(message="Done waiting for 1v1 battle to star")
    return "good"


def check_for_in_2v2_battle(vm_index) -> bool:
    if not check_line_for_color(
        vm_index=vm_index, x_1=104, y_1=605, x_2=122, y_2=624, color=(249, 88, 235)
    ):
        return False
    if not check_line_for_color(
        vm_index=vm_index, x_1=57, y_1=515, x_2=76, y_2=519, color=(255, 255, 255)
    ):
        return False
    if not check_line_for_color(
        vm_index=vm_index, x_1=108, y_1=620, x_2=122, y_2=613, color=(248, 80, 236)
    ):
        return False
    return True


def check_for_in_1v1_battle(vm_index) -> bool:
    # look for red enemy name
    red_enemy_name_exists: bool = check_line_for_color(
        vm_index=vm_index, x_1=30, y_1=7, x_2=80, y_2=21, color=(255, 51, 153)
    )

    # look for purple elixer thing
    purple_exlier_icon_exists: bool = check_line_for_color(
        vm_index=vm_index, x_1=30, y_1=7, x_2=80, y_2=21, color=(255, 51, 153)
    )

    # look for white chat bubble
    white_chat_bubble_exists: bool = check_line_for_color(
        vm_index=vm_index, x_1=30, y_1=7, x_2=80, y_2=21, color=(255, 51, 153)
    )

    # look for tan time left text
    tan_time_left_text_exists: bool = check_line_for_color(
        vm_index=vm_index, x_1=30, y_1=7, x_2=80, y_2=21, color=(255, 51, 153)
    )

    if (
        tan_time_left_text_exists
        and white_chat_bubble_exists
        and red_enemy_name_exists
        and purple_exlier_icon_exists
    ):
        return True

    return False


def get_to_clash_main_from_clan_page(
    vm_index, logger: Logger, printmode=False
) -> Literal["restart", "good"]:
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
    if wait_for_clash_main_menu(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 23422464342342, failure waiting for clash main"
        )
        return "restart"
    return "good"


def get_to_clan_tab_from_clash_main(
    vm_index, logger: Logger, printmode=False
) -> Literal["restart", "good"]:
    if printmode:
        logger.change_status(status="Getting to clan tab from clash main menu")
    else:
        logger.log("Getting to clan tab from clash main menu")

    # if not on main, restart
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            status="ERROR 7346722 Not on clash main menu, returning to start state"
        )
        return "restart"

    # click clan tab button
    click(
        vm_index,
        CLAN_TAB_BUTTON_COORDS_FROM_MAIN[0],
        CLAN_TAB_BUTTON_COORDS_FROM_MAIN[1],
    )

    while not check_if_on_clan_chat_page(vm_index):
        if printmode:
            logger.change_status(status="Cycling to clan tab")
        else:
            logger.log("Cycling to clan tab")
        click(
            vm_index,
            CLAN_TAB_BUTTON_COORDS_FROM_MAIN[0],
            CLAN_TAB_BUTTON_COORDS_FROM_MAIN[1],
        )

        scroll_up(vm_index)

        time.sleep(3)

    if printmode:
        logger.change_status(status="Made it to clan chat page")
    else:
        logger.log("Made it to clan chat page")
    return "good"


def check_if_on_clan_chat_page(vm_index) -> bool:
    iar = numpy.asarray(screenshot(vm_index))

    friend_battle_button_exists = False
    for x_coord in range(140, 157):
        this_pixel = iar[541][x_coord]
        if pixel_is_equal([183, 96, 252], this_pixel, tol=35):
            friend_battle_button_exists = True
            break

    blue_chat_button_exists = False
    for x_coord in range(300, 320):
        this_pixel = iar[539][x_coord]
        if pixel_is_equal([76, 174, 255], this_pixel, tol=35):
            blue_chat_button_exists = True

    red_x_button_exists = False
    for x_coord in range(343, 348):
        this_pixel = iar[44][x_coord]
        if pixel_is_equal([228, 28, 28], this_pixel, tol=35):
            red_x_button_exists = True
            break

    if friend_battle_button_exists and blue_chat_button_exists and red_x_button_exists:
        return True
    return False


def check_if_on_profile_page(vm_index) -> bool:
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
    vm_index, logger: Logger, printmode=False
) -> Literal["restart", "good"]:
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


def get_to_profile_page(vm_index, logger: Logger) -> Literal["restart", "good"]:
    # if not on clash main, return
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            status="ERROR 732457256 Not on clash main menu, returning to start state"
        )
        return "restart"

    # click profile button
    click(vm_index, PROFILE_PAGE_COORD[0], PROFILE_PAGE_COORD[1])

    # wait for profile page
    if wait_for_profile_page(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 0573085 Waited too long for clash profile page"
        )
        return "restart"
    return "good"


def check_for_trophy_reward_menu(vm_index) -> bool:
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


def wait_for_clash_main_menu(
    vm_index, logger: Logger, printmode=False
) -> Literal["restart", "good"]:
    if printmode:
        logger.change_status(status="Waiting for clash main menu")
    else:
        logger.log("Waiting for clash main menu")

    start_time: float = time.time()
    while not check_if_on_clash_main_menu(vm_index):
        # loop count

        if check_for_trophy_reward_menu(vm_index):
            handle_trophy_reward_menu(vm_index, logger)

        if time.time() - start_time > 60:
            logger.change_status(
                status="Looped through getting to clash main too many times"
            )
            logger.change_status(
                status="wait_for_clash_main_menu() took too long waiting for clash main."
            )
            return "restart"

        # click dead space
        click(vm_index, 32, 364)

        # wait 1 sec
        time.sleep(1)

    if printmode:
        logger.change_status(status="Done waiting for clash main menu")
    else:
        logger.log("Done waiting for clash main menu")

    return "good"


def check_if_on_clash_main_menu(vm_index) -> bool:
    if not check_for_gem_logo_on_main(vm_index):
        return False

    if not check_for_friends_logo_on_main(vm_index):
        return False

    if not check_for_gold_logo_on_main(vm_index):
        return False
    return True


def check_for_gem_logo_on_main(vm_index) -> bool:
    # Method to check if the clash main menu is on screen
    iar: numpy.ndarray[Any, numpy.dtype[Any]] = numpy.array(screenshot(vm_index))

    for x_index in range(390, 410):
        this_pixel = iar[16][x_index]
        if pixel_is_equal([65, 198, 24], this_pixel, tol=35):
            return True
    return False


def check_for_friends_logo_on_main(vm_index) -> bool:
    # Method to check if the clash main menu is on screen
    iar = numpy.array(screenshot(vm_index))

    for x_coord in range(250, 290):
        this_pixel = iar[69][x_coord]
        if pixel_is_equal([228, 244, 255], this_pixel, tol=35):
            return True
    return False


def check_for_gold_logo_on_main(vm_index) -> bool:
    # Method to check if the clash main menu is on screen
    iar = numpy.array(screenshot(vm_index))

    for x_index in range(290, 310):
        this_pixel = iar[17][x_index]
        if pixel_is_equal([224, 180, 56], this_pixel, tol=35):
            return True
    return False


if __name__ == "__main__":
    pass
