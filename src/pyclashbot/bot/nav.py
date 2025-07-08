import random
import time
from typing import Literal

from pyclashbot.detection.image_rec import (
    check_line_for_color,
    pixels_match_colors,
    pixel_is_equal,
    region_is_color,
)
from pyclashbot.memu.client import (
    click,
    custom_swipe,
    screenshot,
)
from pyclashbot.utils.logger import Logger

_2V2_START_WAIT_TIMEOUT = 180  # s
CLAN_TAB_BUTTON_COORDS_FROM_MAIN = [315, 597]
PROFILE_PAGE_COORD = [88, 93]
CLASH_MAIN_COORD_FROM_CLAN_PAGE = [178, 593]
CLASH_MAIN_OPTIONS_BURGER_BUTTON = (390, 62)
BATTLE_LOG_BUTTON = (241, 43)
CARD_PAGE_ICON_FROM_CLASH_MAIN = (108, 598)
CARD_PAGE_ICON_FROM_CARD_PAGE = (147, 598)
CHALLENGES_TAB_ICON_FROM_CLASH_MAIN = (380, 598)
OK_BUTTON_COORDS_IN_TROPHY_REWARD_PAGE = (209, 599)
CLAN_PAGE_FROM_MAIN_NAV_TIMEOUT = 240  # seconds
CLASH_MAIN_MENU_DEADSPACE_COORD = (32, 520)
OPEN_WAR_CHEST_BUTTON_COORD = (188, 415)
OPENING_WAR_CHEST_DEADZONE_COORD = (5, 298)
CLASH_MAIN_WAIT_TIMEOUT = 240  # s
SHOP_PAGE_BUTTON: tuple[Literal[33], Literal[603]] = (33, 603)


def get_to_shop_page_from_clash_main(vm_index, logger) -> bool:
    click(vm_index, SHOP_PAGE_BUTTON[0], SHOP_PAGE_BUTTON[1])
    if wait_for_clash_main_shop_page(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 085708235 Failure waiting for clash main shop page ",
        )
        return False
    return True


def wait_for_2v2_battle_start(vm_index, logger: Logger)  -> bool:
    """Waits for the 2v2 battle to start.

    Args:
    ----
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object.
        printmode (bool, optional): Whether to print the status. Defaults to False.

    Returns:
    -------
        Literal["restart", "good"]: "restart" if the function
        needs to be restarted, "good" otherwise.

    """
    _2v2_start_wait_start_time = time.time()

    while time.time() - _2v2_start_wait_start_time < _2V2_START_WAIT_TIMEOUT:
        time_taken = str(time.time() - _2v2_start_wait_start_time)[:4]
        logger.change_status(
            status=f"Waiting for 2v2 battle to start for {time_taken}s",
        )

        if check_if_in_battle(vm_index) == "2v2":
            logger.change_status("Detected an ongoing 2v2 battle!")
            return True

        click(vm_index=vm_index, x_coord=20, y_coord=200)

    return False


def wait_for_1v1_battle_start(
    vm_index,
    logger: Logger,
    printmode=False,
)  -> bool:
    """Waits for the 1v1 battle to start.

    Args:
    ----
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object.
        printmode (bool, optional): Whether to print the status. Defaults to False.

    Returns:
    -------
        bool - success status

    """
    start_time: float = time.time()
    if printmode:
        logger.change_status(status="Waiting for 1v1 battle to start")
    else:
        logger.log(message="Waiting for 1v1 battle to start")
    while check_if_in_battle(vm_index) != "1v1":
        time_taken: float = time.time() - start_time
        if time_taken > 60:
            logger.change_status(
                status="Error 8734572456 Waiting too long for 1v1 battle to start",
            )
            return False
        print("Waiting for 1v1 start")
        click(vm_index=vm_index, x_coord=200, y_coord=200)

    if printmode:
        logger.change_status(status="Done waiting for 1v1 battle to start")
    else:
        logger.log(message="Done waiting for 1v1 battle to star")
    return True


def check_for_in_battle_with_delay(vm_index) -> bool:
    """Checks if the virtual machine is in a 2v2 battle with a delay.

    Args:
    ----
        vm_index (int): The index of the virtual machine.

    Returns:
    -------
        bool: True if the virtual machine is in a 2v2 battle, False otherwise.

    """
    timeout = 3  # s
    start_time = time.time()
    while time.time() - start_time < timeout:
        if check_if_in_battle(vm_index) != "None":
            return True
    return False


def check_if_in_battle(vm_index) -> Literal["2v2"] | Literal["1v1"] | Literal["None"]:
    """Checks if the virtual machine is in a 1v1 or 2v2 battle.

    Args:
    ----
        vm_index (int): The index of the virtual machine.

    Returns:
    -------
        str: '2v2' if the battle is in 2v2, '1v1' if the battle is in 1v1, 'None' otherwise.

    """
    iar = screenshot(vm_index)

    # Pixels to check for any type of battle
    pixels = [
        iar[517][56],
        iar[533][67],
        iar[616][115],
    ]

    # Expected colors for the above pixels
    colors = [
        [255, 255, 255],
        [255, 255, 255],
        [236, 91, 252],
    ]

    # Check if all the pixels match for an ongoing battle
    if all(
        pixel_is_equal(pixels[index], colors[index], tol=55)
        for index in range(len(pixels))
    ):
        # Specific check for 2v2 battle
        combat_2v2_pixel = iar[506][135]
        combat_2v2_color = [169, 29, 172]

        if pixel_is_equal(combat_2v2_pixel, combat_2v2_color, tol=50):
            return "2v2"
        return "1v1"
    return "None"


def check_if_in_battle_at_start(vm_index, logger):
    """Checks if the game is currently in a battle at startup and handles it accordingly.
    Also checks if the game is on the end-of-battle screen and returns to the main menu.

    Args:
    ----
        vm_index (int): Index of the virtual machine.
        logger (Logger): Logger instance for logging messages.

    """
    # Local imports to avoid circular imports
    from pyclashbot.bot.do_fight_state import (
        do_1v1_fight_state,
        do_2v2_fight_state,
        get_to_main_after_fight,
    )

    battle_status = check_if_in_battle(vm_index)
    if battle_status == "1v1":
        logger.log("Detected in battle status: 1v1. Engaging in battle.")
        fight_result = do_1v1_fight_state(
            vm_index,
            logger,
            "next_state",
            False,
            "none",
            True,
        )
    elif battle_status == "2v2":
        logger.log("Detected in battle status: 2v2. Engaging in battle.")
        fight_result = do_2v2_fight_state(vm_index, logger, "next_state", False, True)
    else:
        # If not currently in a battle, check if it's the end-of-battle screen
        if check_end_of_battle_screen(vm_index):
            logger.log("Detected end of battle screen.")
            if not get_to_main_after_fight(vm_index, logger):
                logger.log("Failed to return to Clash Main Menu after fight.")
                return "restart"
            logger.log("Successfully returned to Clash Main Menu after fight.")
            return "good"  # Indicate successful handling after the end of the battle
        return "no"  # Indicate no battle detected or no end-of-battle screen

    # Attempt to return to the main menu after the battle, if a fight was detected
    if fight_result not in ["restart", None]:
        if not get_to_main_after_fight(vm_index, logger):
            logger.log("Failed to return to Clash Main Menu after fight.")
            return "restart"
        logger.log("Successfully returned to Clash Main Menu after fight.")
        return "good"  # Indicate successful return to main menu after fight

    return "restart"  # Default case if fight_result is 'restart' or None


def check_end_of_battle_screen(vm_index):
    """Checks if the current screen is the end-of-battle screen for either 1v1 or 2v2 battles.

    Args:
    ----
        vm_index (int): Index of the virtual machine.

    Returns:
    -------
        bool: True if on the end-of-battle screen, False otherwise.

    """
    iar = screenshot(vm_index)

    # Pixels to check for 1v1 battle end screen
    pixels_1v1 = [
        ((74, 179), (64, 12, 150)),
        ((129, 206), (71, 14, 159)),
        ((337, 179), (57, 23, 129)),
        ((349, 179), (46, 10, 109)),
        ((349, 367), (120, 65, 25)),
        ((337, 367), (153, 86, 33)),
        ((129, 393), (187, 102, 40)),
        ((74, 367), (171, 93, 35)),
        ((180, 547), (255, 187, 104)),  # OK Button
        ((214, 555), (255, 255, 255)),
        ((244, 565), (255, 175, 78)),
        ((59, 518), (255, 255, 255)),  # Emote bubble
        ((73, 518), (255, 255, 255)),
        ((59, 528), (0, 0, 0)),
        ((74, 528), (0, 0, 0)),
    ]

    # Pixels to check for 2v2 battle end screen
    pixels_2v2 = [
        ((40, 11), (255, 153, 51)),
        ((209, 35), (255, 203, 51)),
        ((400, 35), (255, 153, 51)),
        ((392, 15), (135, 134, 253)),
        ((400, 17), (255, 255, 255)),
        ((408, 23), (60, 60, 253)),
        ((16, 600), (83, 66, 52)),  # Bottom bar
        ((408, 600), (83, 66, 52)),
        ((53, 593), (255, 187, 105)),
        ((109, 612), (255, 175, 78)),
        ((77, 600), (255, 255, 255)),
        ((340, 593), (255, 255, 255)),
    ]

    # Check for 1v1 end screen
    is_1v1_end = all(
        pixel_is_equal(iar[y][x], expected_color, tol=30)
        for (x, y), expected_color in pixels_1v1
    )

    # Check for 2v2 end screen
    is_2v2_end = all(
        pixel_is_equal(iar[y][x], expected_color, tol=30)
        for (x, y), expected_color in pixels_2v2
    )

    return is_1v1_end or is_2v2_end


def get_to_clash_main_from_clan_page(
    vm_index,
    logger: Logger,
    printmode=False,
) -> Literal["restart", "good"]:
    """Navigates to the clash main page from the clan page.

    Args:
    ----
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object.
        printmode (bool, optional): Whether to print the status. Defaults to False.

    Returns:
    -------
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
        vm_index,
        CLASH_MAIN_COORD_FROM_CLAN_PAGE[0],
        CLASH_MAIN_COORD_FROM_CLAN_PAGE[1],
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
    """Opens a war chest obstruction if found on the way to getting to the clan page.

    Args:
    ----
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
    # dont use check_line_for_color in the future. its slow
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


def check_for_boot_reward(iar):
    pixels = [
        iar[350][150],
        iar[377][174],
        iar[379][198],
        iar[378][210],
        iar[390][250],
        iar[355][273],
        iar[395][146],
    ]
    colors = [
        [39, 189, 255],
        [255, 255, 255],
        [255, 255, 255],
        [43, 190, 255],
        [89, 135, 208],
        [62, 199, 255],
        [43, 190, 255],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=25):
            return False

    return True


def get_to_clan_tab_from_clash_main(
    vm_index: int,
    logger: Logger,
):

    # just try it raw real quick in case it works first try
    click(
        vm_index,
        CLAN_TAB_BUTTON_COORDS_FROM_MAIN[0],
        CLAN_TAB_BUTTON_COORDS_FROM_MAIN[1],
    )
    time.sleep(2)
    if check_if_on_clan_chat_page(screenshot(vm_index)):
        return True

    start_time = time.time()
    while time.time() - start_time < CLAN_PAGE_FROM_MAIN_NAV_TIMEOUT:
        iar = screenshot(vm_index)

        # if boot exists, collect boot
        if check_for_boot_reward(iar):
            collect_boot_reward(vm_index)
            logger.add_war_chest_collect()
            print(f"Incremented war chest collects to {logger.war_chest_collects}")

        # check for a war chest obstructing the nav
        elif check_for_war_chest_obstruction(vm_index):
            open_war_chest_obstruction(vm_index, logger)
            logger.add_war_chest_collect()
            print(f"Incremented war chest collects to {logger.war_chest_collects}")

        # if on the clan tab chat page, return
        elif check_if_on_clan_chat_page(iar):
            return True

        # if on clash main, click the clan tab button
        elif check_if_on_clash_main_menu(vm_index):
            click(
                vm_index,
                CLAN_TAB_BUTTON_COORDS_FROM_MAIN[0],
                CLAN_TAB_BUTTON_COORDS_FROM_MAIN[1],
            )

        # if on final results page, click OK
        elif check_for_final_results_page(vm_index):
            logger.log("On final_results_page so clicking OK button")
            click(vm_index, 211, 524)

        # handle daily defenses rank page
        handle_war_popup_pages(vm_index, logger)

        # scroll_up(vm_index)
        # scroll_down(vm_index)
        custom_swipe(vm_index, 206, 313, 204, 417)
        custom_swipe(vm_index, 204, 417, 206, 313)
        click(
            vm_index,
            CLAN_TAB_BUTTON_COORDS_FROM_MAIN[0],
            CLAN_TAB_BUTTON_COORDS_FROM_MAIN[1],
        )
        time.sleep(2)

    # if here, then done
    logger.log("Made it to the clan page from clash main")
    return True


def handle_war_popup_pages(vm_index, logger):
    timeout = 2
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
            logger.change_status("Handled daily defenses rank page")
            return True

        if check_for_war_chest_obstruction(vm_index):
            print("Found war chest obstruction")
            open_war_chest_obstruction(vm_index, logger)
            logger.add_war_chest_collect()
            print(f"Incremented war chest collects to {logger.war_chest_collects}")
            return True

    return False


def check_for_battle_day_results_page(vm_index):
    iar = screenshot(vm_index)
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
        if not pixel_is_equal(p, colors[i], tol=25):
            return False
    return True


def check_for_daily_defenses_rank_page_3(vm_index):
    iar = screenshot(vm_index)
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
        if not pixel_is_equal(p, colors[i], tol=15):
            return False
    return True


def check_for_daily_defenses_rank_page_4(vm_index):
    iar = screenshot(vm_index)
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
        if not pixel_is_equal(p, colors[i], tol=15):
            return False
    return True


def check_for_daily_defenses_rank_page_2(vm_index):
    iar = screenshot(vm_index)
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
        if not pixel_is_equal(p, colors[i], tol=25):
            return False
    return True


def check_for_daily_defenses_rank_page(vm_index):
    iar = screenshot(vm_index)
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
        if not pixel_is_equal(p, colors[i], tol=15):
            return False
    return True


def check_for_final_results_page(vm_index) -> bool:
    """Checks if the final results page is displayed on the screen.

    Args:
    ----
        vm_index (int): The index of the virtual machine.

    Returns:
    -------
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


def check_if_on_clan_chat_page(iar) -> bool:
    """Checks if the bot is currently on the clan chat page by comparing specific pixel colors.

    Args:
    ----
        vm_index (int): The index of the virtual machine.

    Returns:
    -------
        bool: True if the bot is on the clan chat page, False otherwise.

    """
    # Define the pixel positions and their expected colors
    pixels = [
        (iar[15][9], (141, 84, 69)),  # X: 9 Y: 15
        (iar[22][324], (245, 231, 222)),  # X: 324 Y: 22
        (iar[36][346], (128, 129, 254)),  # X: 346 Y: 36
        (iar[65][410], (192, 125, 101)),  # X: 410 Y: 65
        (iar[589][268], (243, 123, 19)),  # X: 268 Y: 589
        (iar[589][243], (141, 107, 73)),  # X: 243 Y: 589
        (iar[528][337], (255, 255, 255)),  # X: 337 Y: 528
        (iar[542][310], (255, 175, 78)),  # X: 310 Y: 542
    ]

    # Iterate through each pixel and its expected color
    for pixel, expected_color in pixels:
        if not pixel_is_equal(pixel, expected_color, tol=50):
            return False  # If any pixel doesn't match, return False immediately

    return True  # If all pixels match their expected colors, return True


def check_if_on_profile_page(vm_index) -> bool:
    """Checks if the bot is on the profile page.

    Args:
    ----
        vm_index (int): The index of the virtual machine.

    Returns:
    -------
        bool: True if the bot is on the profile page, False otherwise.

    """
    if not check_line_for_color(
        vm_index,
        x_1=329,
        y_1=188,
        x_2=339,
        y_2=195,
        color=(4, 244, 88),
    ):
        return False
    if not check_line_for_color(
        vm_index,
        x_1=169,
        y_1=50,
        x_2=189,
        y_2=50,
        color=(255, 222, 0),
    ):
        return False
    if not check_line_for_color(
        vm_index,
        x_1=369,
        y_1=63,
        x_2=351,
        y_2=71,
        color=(228, 36, 36),
    ):
        return False
    return True


def wait_for_profile_page(
    vm_index: int,
    logger: Logger,
    printmode: bool = False,
) -> Literal["restart", "good"]:
    """Waits for the profile page to load.

    Args:
    ----
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object.
        printmode (bool, optional): Whether to print status messages. Defaults to False.

    Returns:
    -------
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
                status="Error 8734572456 Waiting too long for profile page",
            )
            return "restart"

    if printmode:
        logger.change_status(status="Done waiting for profile page")
    else:
        logger.log("Done waiting for profile page")
    return "good"


def get_to_profile_page(vm_index: int, logger: Logger) -> Literal["restart", "good"]:
    """Navigates to the profile page.

    Args:
    ----
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object.

    Returns:
    -------
        Literal["restart", "good"]: "restart" if an error occurred, "good" otherwise.

    """
    # if not on clash main, return
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(
            status="ERROR 732457256 Not on clash main menu, returning to start state",
        )
        return "restart"

    # click profile button
    click(vm_index, PROFILE_PAGE_COORD[0], PROFILE_PAGE_COORD[1])

    # wait for profile page
    if wait_for_profile_page(vm_index, logger, printmode=False) == "restart":
        logger.change_status(
            status="Error 0573085 Waited too long for clash profile page",
        )
        return "restart"
    return "good"


def check_for_trophy_reward_menu(vm_index) -> bool:
    iar = screenshot(vm_index)

    pixels = [
        iar[592][172],
        iar[617][180],
        iar[607][190],
        iar[603][200],
        iar[596][210],
        iar[593][220],
        iar[600][230],
        iar[610][235],
        iar[623][246],
    ]
    colors = [
        [255, 184, 68],
        [255, 175, 78],
        [255, 175, 78],
        [248, 239, 227],
        [255, 187, 104],
        [255, 176, 79],
        [255, 187, 104],
        [255, 175, 78],
        [253, 135, 39],
    ]

    for i, pixel in enumerate(pixels):
        if not pixel_is_equal(pixel, colors[i], tol=25):
            return False

    return True


def handle_trophy_reward_menu(
    vm_index,
    logger: Logger,
    printmode=False,
) -> Literal["good"]:
    """Handles the trophy reward menu.

    Args:
    ----
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object.
        printmode (bool, optional): Whether to print status messages. Defaults to False.

    Returns:
    -------
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


def check_for_megaknight_evolution_popup(vm_index):
    iar = screenshot(vm_index)
    pixels = [
        iar[585][170],
        iar[596][208],
        iar[599][180],
        iar[610][200],
        iar[613][190],
        iar[590][210],
        iar[595][220],
        iar[600][230],
        iar[605][240],
        iar[615][250],
    ]
    colors = [
        [255, 186, 53],
        [148, 133, 114],
        [255, 175, 78],
        [255, 178, 79],
        [255, 175, 78],
        [255, 187, 104],
        [101, 76, 46],
        [255, 255, 255],
        [255, 176, 77],
        [255, 141, 19],
    ]
    for i, c in enumerate(colors):
        if not pixel_is_equal(c, pixels[i], tol=25):
            return False
    return True


def wait_for_clash_main_menu(vm_index, logger: Logger, deadspace_click=True) -> bool:
    """Waits for the user to be on the clash main menu.
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

        # handle getting stuck on megaknight evolution popup
        if check_for_megaknight_evolution_popup(vm_index):
            print("Handling megaknight evolution popup")
            click(vm_index, 206, 601)
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
    if check_if_on_clash_main_menu(vm_index) is not True:
        print("Failed to get to clash main! Saw these pixels before restarting:")
        return False

    return True


def check_if_on_path_of_legends_clash_main(vm_index):
    iar = screenshot(vm_index)

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
        [57, 162, 215],
        [51, 208, 238],
        [23, 190, 61],
        [139, 106, 72],
        [156, 121, 81],
        [138, 105, 71],
        [94, 16, 43],
        [91, 14, 41],
    ]

    # if any pixel doesnt match the sentinel, then we're not on clash main
    for i, pixel in enumerate(pixels):
        if not pixel_is_equal(pixel, colors[i], tol=25):
            return pixels

    # if all pixels are good, we're on clash main
    return True


def check_if_on_clash_main_menu(vm_index) -> bool:
    """Checks if the user is on the clash main menu.
    Returns True if on main menu, False if not.
    """
    iar = screenshot(vm_index)

    pixels = [
        iar[14][209],  # white
        iar[14][324],  # white
        iar[20][298],  # yellow
        iar[19][400],  # green
        iar[14][408],  # green
        iar[585][164],  # bluegrey
        iar[586][255],  # bluegrey
    ]

    # sentinel color list
    colors = [
        [255, 255, 255],
        [255, 255, 255],
        [51, 208, 239],
        [28, 217, 76],
        [40, 215, 80],
        [139, 106, 72],
        [139, 106, 72],
    ]



    # pixels = [
    #     #blue strip on the rightmost part of screen
    #     iar[92][414],
    #     iar[120][414],
    #     iar[140][414],
    #     iar[160][414],
    #     iar[260][414],
    #     iar[280][414],
    #     iar[350][414],
    #     iar[370][414],
    #     iar[389][414],

    #     #green plus button for more gold
    #     iar[9][203],
    #     iar[20][202],
    #     iar[9][216],
    #     iar[20][216],
    #     iar[14][210],

    #     #green plus button for more gems
    #     iar[9][319],
    #     iar[21][318],
    #     iar[20][332],
    #     iar[9][331],
    #     iar[14][322],
    #     iar[11][325],
    #     iar[14][329],
    #     iar[17][325],
    # ]

    # colors = []
    # for p in pixels:print(p)

    # if any pixel doesnt match the sentinel, then we're not on clash main
    for i, pixel in enumerate(pixels):
        if not pixel_is_equal(pixel, colors[i], tol=35):
            return False

    # if all pixels are good, we're on clash main
    return True


def get_to_card_page_from_clash_main(
    vm_index: int,
    logger: Logger,
    printmode: bool = False,
) -> Literal["restart", "good"]:
    """Clicks on the card page icon from the clash main screen and waits until the card page is loaded.
    If the card page is not loaded within 3 seconds, returns "restart".
    If the card page is loaded within 3 seconds, returns "good".

    Args:
    ----
    - vm_index (int): The index of the virtual machine to perform the action on.
    - logger (Logger): The logger object to log the action.
    - printmode (bool, optional): If True, changes the logger status instead of logging.

    Returns:
    -------
    - Literal["restart", "good"]: Returns "restart" if the card page is not loaded
    within 3 seconds, "good" otherwise.

    """
    start_time = time.time()

    if printmode:
        logger.change_status(status="Getting to card page from clash main")
    else:
        logger.log("Getting to card page from clash main")

    # click card page icon
    click(
        vm_index,
        CARD_PAGE_ICON_FROM_CLASH_MAIN[0],
        CARD_PAGE_ICON_FROM_CLASH_MAIN[1],
    )
    time.sleep(2.5)

    # while not on the card page, cycle the card page
    while not check_if_on_card_page(vm_index):
        time_taken = time.time() - start_time
        if time_taken > 3:
            return "restart"

        click(
            vm_index,
            CARD_PAGE_ICON_FROM_CARD_PAGE[0],
            CARD_PAGE_ICON_FROM_CARD_PAGE[1],
        )
        time.sleep(3)

    if printmode:
        logger.change_status(status="Made it to card page")
    else:
        logger.log("Made it to card page")
    return "good"


def check_if_on_underleveled_card_page(vm_index):
    iar = screenshot(vm_index)
    pixels = [
        iar[445][50],
        iar[101][57],
        iar[103][370],
        iar[19][331],
    ]
    colors = [
        [227, 1, 242],
        [245, 106, 0],
        [243, 104, 0],
        [73, 228, 58],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=25):
            return False

    return True


def check_if_on_card_page(vm_index) -> bool:
    def check_if_on_card_page2(iar):
        pixels = [
            iar[441][58],
            iar[191][18],
            iar[211][390],
            iar[435][325],
            iar[102][59],
            iar[109][56],
            iar[116][55],
        ]
        colors = [
            [232, 0, 248],
            [105, 43, 1],
            [105, 44, 1],
            [249, 186, 100],
            [255, 255, 255],
            [255, 255, 255],
            [255, 255, 255],
        ]
        for i, p in enumerate(pixels):
            if not pixel_is_equal(colors[i], p, tol=15):
                return False

        return True

    def check_if_on_path_of_legends_mode_card_page(iar):
        pixels = [
            iar[108][175],
            iar[112][189],
            iar[103][254],
            iar[109][295],
            iar[446][54],
            iar[446][64],
            iar[444][49],
            iar[14][210],
            iar[14][325],
        ]
        colors = [
            [186, 105, 143],
            [254, 254, 254],
            [229, 188, 206],
            [213, 175, 191],
            [224, 1, 237],
            [229, 0, 244],
            [187, 7, 191],
            [255, 255, 255],
            [255, 255, 255],
        ]

        for i, p in enumerate(pixels):
            if not pixel_is_equal(colors[i], p, tol=15):
                return False

        return True

    def check_if_on_goblin_mode_card_page(iar):
        pixels = [
            iar[108][175],
            iar[112][189],
            iar[103][254],
            iar[109][295],
            iar[446][54],
            iar[446][64],
            iar[444][49],
            iar[14][210],
            iar[14][325],
        ]
        colors = [
            [255, 255, 255],
            [255, 255, 255],
            [255, 255, 255],
            [255, 255, 255],
            [223, 1, 237],
            [228, 0, 243],
            [186, 8, 190],
            [255, 255, 255],
            [255, 255, 255],
        ]

        for i, p in enumerate(pixels):
            if not pixel_is_equal(colors[i], p, tol=15):
                return False

        return True

    iar = screenshot(vm_index)
    if check_if_on_card_page2(iar):
        return True
    if check_if_on_goblin_mode_card_page(iar):
        return True
    if check_if_on_path_of_legends_mode_card_page(iar):
        return True

    pixels = [
        iar[433][58],
        iar[101][55],
        iar[108][48],
        iar[116][59],
        iar[58][82],
        iar[64][179],
        iar[62][108],
        iar[67][146],
        iar[77][185],
        iar[77][84],
    ]

    colors = [
        [222, 0, 235],
        [255, 255, 255],
        [255, 255, 255],
        [255, 255, 255],
        [203, 137, 44],
        [195, 126, 34],
        [255, 255, 255],
        [255, 255, 255],
        [177, 103, 15],
        [178, 104, 15],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(colors[i], p, tol=15):
            return False

    return True


def get_to_challenges_tab_from_main(vm_index, logger) -> Literal["restart", "good"]:
    """Clicks on the challenges tab in the Clash Main menu to navigate to the challenges tab.

    Args:
    ----
        vm_index (int): The index of the virtual machine to perform the clicks on.
        logger (Logger): The logger object to log messages to.

    Returns:
    -------
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
            status="Error 892572938 waited for challenges tab too long, restarting vm",
        )
        return "restart"
    return "good"


def handle_clash_main_tab_notifications(
    vm_index,
    logger: Logger,
) -> bool:
    """Clicks on the card, shop, and challenges tabs in the Clash Main menu to handle notifications.

    Args:
    ----
        vm_index (int): The index of the virtual machine to perform the clicks on.
        logger (Logger): The logger object to log messages to.

    Returns:
    -------
        Literal["restart", "good"]: "restart" if an error occurred and the VM needs to be restarted,
        "good" otherwise.

    """
    start_time: float = time.time()

    # wait for clash main to appear
    if wait_for_clash_main_menu(vm_index, logger) is False:
        logger.change_status(
            status="Error 246246 Waited too long for clash main menu, restarting vm",
        )
        return False

    # click card tab from main
    print("Clicked card tab")
    click(vm_index, 103, 598)
    time.sleep(1)

    # click shop tab from card tab
    print("Clicked shop tab")
    click(vm_index, 9, 594, clicks=3, interval=0.33)
    time.sleep(1)

    # click clan tab from shop tab
    print("Clicked clan tab")
    click(vm_index, 315, 594)
    time.sleep(3)

    if check_for_war_chest_obstruction(vm_index):
        open_war_chest_obstruction(vm_index, logger)
        logger.add_war_chest_collect()
        print(f"Incremented war chest collects to {logger.war_chest_collects}")
        time.sleep(3)

    # click events tab from clan tab
    print("Getting to events tab...")
    while not check_for_events_page(vm_index):
        print("Still not on events page...")
        click(vm_index, 408, 600)
        handle_war_popup_pages(vm_index, logger)

    print("On events page")

    # spam click shop page at the leftmost location, wait a little bit
    print("Clicked shop page")
    click(vm_index, 9, 594, clicks=3, interval=0.33)
    time.sleep(2)

    # click clash main from shop page
    print("Clicked clash main")
    click(vm_index, 240, 600)
    time.sleep(2)

    # handle possibility of trophy road obstructing clash main
    if check_for_trophy_reward_menu(vm_index):
        handle_trophy_reward_menu(vm_index, logger)
        time.sleep(2)

    # wait for clash main to appear
    if wait_for_clash_main_menu(vm_index, logger) is False:
        logger.change_status(
            status="Error 47 Waited too long for clash main menu, restarting vm",
        )
        return False

    logger.change_status(
        status=f"Handled clash main notifications in {str(time.time() - start_time)[:5]}s",
    )

    return True


def check_for_events_page(vm_index):
    iar = screenshot(vm_index)

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

    for i, p in enumerate(pixels):
        if not pixel_is_equal(colors[i], p, tol=15):
            return False
    return True


def wait_for_clash_main_challenges_tab(
    vm_index,
    logger: Logger,
    printmode=False,
) -> Literal["restart", "good"]:
    """Waits for the Clash Main menu to be on the challenges tab.

    Args:
    ----
        vm_index (int): The index of the virtual machine to check the menu on.
        logger (Logger): The logger object to log messages to.
        printmode (bool, optional): Whether to print status messages to the logger. Defaults to
        False.

    Returns:
    -------
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
                status="Error 8884613 Waited too long for clash main challenges tab",
            )
            return "restart"

    if printmode:
        logger.change_status(status="Done waiting for clash main challenges tab")
    else:
        logger.log("Done waiting for clash main challenges tab")
    return "good"


def check_if_on_clash_main_challenges_tab(vm_index) -> bool:
    """Checks if the Clash Main menu is on the challenges tab.

    Args:
    ----
        vm_index (int): The index of the virtual machine to check the menu on.

    Returns:
    -------
        bool: True if the menu is on the challenges tab, False otherwise.

    """
    if not region_is_color(vm_index, [380, 580, 30, 45], (76, 111, 145)):
        return False
    if not region_is_color(vm_index, [290, 610, 25, 15], (80, 118, 153)):
        return False

    return True


def check_if_on_clash_main_shop_page(vm_index) -> bool:
    """Check if the bot is currently on the main shop page in the Clash of Clans game.

    Args:
    ----
        vm_index (int): The index of the virtual machine to use for image recognition.

    Returns:
    -------
        bool: True if the bot is on the main shop page, False otherwise.

    """
    if not region_is_color(vm_index, region=[9, 580, 30, 45], color=(76, 112, 146)):
        return False

    if not region_is_color(vm_index, region=[90, 580, 18, 40], color=(75, 111, 146)):
        return False

    lines = [
        check_line_for_color(
            vm_index,
            x_1=393,
            y_1=7,
            x_2=414,
            y_2=29,
            color=(44, 144, 21),
        ),
        check_line_for_color(
            vm_index,
            x_1=48,
            y_1=593,
            x_2=83,
            y_2=594,
            color=(102, 236, 56),
        ),
    ]

    return all(lines)


def wait_for_clash_main_shop_page(
    vm_index,
    logger: Logger,
) -> Literal["restart", "good"]:
    """Wait for the bot to navigate to the main shop page in the Clash of Clans game.

    Args:
    ----
        vm_index (int): The index of the virtual machine to use for image recognition.
        logger (Logger): The logger object to use for logging messages.
        printmode (bool, optional): Whether to print status
        messages to the console. Defaults to False.

    Returns:
    -------
        Literal["restart", "good"]: "restart" if the bot needs to be restarted, "good" otherwise.

    """
    start_time = time.time()
    while not check_if_on_clash_main_shop_page(vm_index):
        time_taken = time.time() - start_time
        if time_taken > 20:
            logger.change_status(
                status="Error 764527546 Waiting too long for clash main shop page",
            )
            return "restart"

    return "good"


def get_to_activity_log(
    vm_index: int,
    logger: Logger,
    printmode: bool = False,
) -> Literal["restart", "good"]:
    """Navigates to the activity log page in the Clash of Clans game.

    Args:
    ----
        vm_index (int): The index of the virtual machine to use.
        logger (Logger): The logger object to use for logging.
        printmode (bool, optional): Whether to print status messages. Defaults to False.

    Returns:
    -------
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
            status="Eror 08752389 Not on clash main menu, restarting vm",
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
            status="Error 99993 Waited too long for calsh main options menu, restarting vm",
        )
        return "restart"

    # click battle log button
    if printmode:
        logger.change_status(status="Clicking activity log button")
    else:
        logger.log("Clicking activity log button")
    click(vm_index, BATTLE_LOG_BUTTON[0], BATTLE_LOG_BUTTON[1])
    if wait_for_battle_log_page(vm_index, logger, printmode) == "restart":
        logger.change_status(
            status="Error 923593 Waited too long for battle log page, restarting vm",
        )
        return "restart"

    return "good"


def wait_for_battle_log_page(
    vm_index,
    logger: Logger,
    printmode=False,
) -> Literal["restart", "good"]:
    """Waits for the battle log page to appear.

    Args:
    ----
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object.
        printmode (bool, optional): Whether to print status messages. Defaults to False.

    Returns:
    -------
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
                status="Error 2457245645 Waiting too long for battle log page",
            )
            return "restart"

    if printmode:
        logger.change_status(status="Done waiting for battle log page to appear")
    else:
        logger.log("Done waiting for battle log page to appear")

    return "good"


def check_if_on_battle_log_page(vm_index) -> bool:
    iar = screenshot(vm_index)

    pixels = [
        iar[72][160],
        iar[71][187],
        iar[71][197],
        iar[72][231],
        iar[73][258],
        iar[64][366],
        iar[79][365],
        iar[70][365],
        iar[62][92],
        iar[77][316],
    ]
    colors = [
        [255, 255, 255],
        [255, 255, 255],
        [255, 255, 255],
        [255, 255, 255],
        [255, 255, 255],
        [147, 135, 254],
        [38, 38, 240],
        [255, 255, 255],
        [138, 122, 115],
        [124, 106, 99],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=25):
            return False
    return True


def check_if_on_clash_main_burger_button_options_menu(vm_index) -> bool:
    """Checks if the virtual machine is on the clash main burger button options menu.

    Args:
    ----
        vm_index (int): The index of the virtual machine.

    Returns:
    -------
        bool: True if the virtual machine is on the clash main burger
        button options menu, False otherwise.

    """
    iar = screenshot(vm_index)
    pixels = [
        iar[42][256],
        iar[41][275],
        iar[41][282],
        iar[42][293],
        iar[44][325],
        iar[32][239],
        iar[34][336],
        iar[50][248],
        iar[49][336],
    ]
    colors = [
        [255, 255, 255],
        [255, 255, 255],
        [255, 255, 255],
        [255, 255, 254],
        [255, 255, 255],
        [255, 187, 105],
        [255, 187, 105],
        [255, 175, 78],
        [255, 175, 78],
    ]
    for i, color in enumerate(colors):
        if not pixel_is_equal(pixels[i], color, tol=25):
            return False
    return True


def wait_for_clash_main_burger_button_options_menu(
    vm_index: int,
    logger: Logger,
    printmode: bool = False,
) -> Literal["restart", "good"]:
    """Waits for the virtual machine to be on the clash main burger button options menu.

    Args:
    ----
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object to use for logging.
        printmode (bool, optional): Whether to print status messages. Defaults to False.

    Returns:
    -------
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
                status="Error 57245645362 Waiting too long for clash main options menu to appear",
            )
            return "restart"
    if printmode:
        logger.change_status(
            status="Done waiting for clash main options menu to appear",
        )
    else:
        logger.log("Done waiting for clash main options menu to appear")
    return "good"


def check_if_on_collection_page(vm_index) -> bool:
    iar = screenshot(vm_index)


    trophy_mode_colors = [
        [211, 159, 45],
        [203, 134, 41],
        [255, 255, 255],
        [217, 202, 181],
        [199, 132, 40],
        [207, 141, 47],
        [205, 139, 44],
        [201, 135, 42],
        [149, 98, 29],
        [178, 104, 14],
    ]

    legends2_mode_colors = [
        [251, 215, 231],
        [248, 211, 227],
        [255, 255, 255],
        [235, 218, 226],
        [247, 210, 226],
        [254, 218, 234],
        [254, 218, 234],
        [254, 217, 233],
        [208, 159, 182],
        [207, 159, 179],
    ]

    pixels = [
        iar[53][220],
        iar[60][230],
        iar[70][240],
        iar[65][260],
        iar[60][280],
        iar[55][290],
        iar[57][300],
        iar[59][310],
        iar[62][320],
        iar[78][335],
    ]

    if (
         pixels_match_colors(pixels, trophy_mode_colors)
        or pixels_match_colors(pixels, legends2_mode_colors)
    ):
        return True

    return False


def get_to_collections_page(vm_index) -> bool:
    # starts on clash main
    if not check_if_on_clash_main_menu(vm_index):
        print("Not on clash main for get_to_magic_items_page()!")
        return False

    # click card page
    card_page_coords = [100, 600]
    click(vm_index, card_page_coords[0], card_page_coords[1])
    time.sleep(1)

    cycle_card_page_coord = [135, 590]

    timeout = 30  # s
    start_time = time.time()
    while not check_if_on_collection_page(vm_index):
        # timeout check
        if time.time() - start_time > timeout:
            print("Timed out waiting for collection page")
            return False

        click(vm_index, cycle_card_page_coord[0], cycle_card_page_coord[1])
        time.sleep(1)

    return True


if __name__ == "__main__":
    print("\n\n\n\n\n\n")
    while 1:
        print(check_if_on_clash_main_menu(1))
