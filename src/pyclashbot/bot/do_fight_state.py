"""random module for randomizing fight plays"""

import numpy
import random
import time
from typing import Literal


from xmlrpc.client import Boolean


from pyclashbot.bot.card_detection import (
    get_play_coords_for_card,
    check_which_cards_are_available,
)
from pyclashbot.bot.troop_locater import choose_play_side
from pyclashbot.bot.nav import (
    check_for_trophy_reward_menu,
    check_if_in_battle,
    check_for_in_battle_with_delay,
    check_if_on_clash_main_menu,
    get_to_activity_log,
    get_to_challenges_tab_from_main,
    handle_trophy_reward_menu,
    wait_for_1v1_battle_start,
    wait_for_2v2_battle_start,
    wait_for_clash_main_menu,
    check_for_events_page,
)
from pyclashbot.detection.image_rec import (
    check_line_for_color,
    pixel_is_equal,
)
from pyclashbot.memu.client import (
    click,
    screenshot,
    scroll_up_on_left_side_of_screen,
)
from pyclashbot.utils.logger import Logger
from pyclashbot.detection.image_rec import (
    make_reference_image_list,
    find_references,
    get_file_count,
    get_first_location,
)


SAVE_FIGHT_IMAGES = True
yolo_images_save_path = r"C:\My Files\my Programs\clash_fight_images"

CLOSE_BATTLE_LOG_BUTTON: tuple[Literal[365], Literal[72]] = (365, 72)
# coords of the cards in the hand
HAND_CARDS_COORDS = [
    (142, 561),
    (210, 563),
    (272, 561),
    (341, 563),
]
CLOSE_THIS_CHALLENGE_PAGE_BUTTON = (27, 22)
# coord of the button on the challenges tab
_2V2_BATTLE_ICON_COORD = (327, 483)
_2V2_BATTLE_BUTTON_COORD_2 = (
    209,
    433,
)  # coord of the battle button after you click the 2v2 battle icon

QUICKMATCH_BUTTON_COORD = (
    274,
    353,
)  # coord of the quickmatch button after you click the battle button
ELIXER_WAIT_TIMEOUT = 40  # way to high but someone got errors with that so idk

EMOTE_BUTTON_COORD_IN_2V2 = (67, 521)
EMOTES_COORDS_IN_2V2 = [
    (144, 545),
    (182, 420),
    (308, 470),
    (327, 544),
    (243, 469),
]


def do_2v2_fight_state(
    vm_index,
    logger: Logger,
    next_state,
    random_fight_mode: Boolean,
    called_from_launching=False,
):
    """method to handle the entirety of the 2v2 battle state (start fight, do fight, end fight)"""

    print(f"random_fight_mode is {random_fight_mode} in do_2v2_fight_state()")

    # wait for battle start
    if wait_for_2v2_battle_start(vm_index=vm_index, logger=logger) is not True:
        logger.change_status(
            status="Error 7567336 wait_for_2v2_battle_start() in do_2v2_fight_state()"
        )
        return "restart"

    logger.change_status(status="2v2 Battle started!")

    logger.change_status(status="Starting fight loop")

    # if regular fight mode, run the fight loop
    if not random_fight_mode and _2v2_fight_loop(vm_index, logger) == "restart":
        logger.log("Error 698245 Failuring in 2v2 regular fight loop")
        return "restart"

    # if random fight mode, run the random fight loop
    if random_fight_mode and _2v2_random_fight_loop(vm_index, logger) == "restart":
        logger.log("Error 655 Failuring in 2v2 random fight loop")
        return "restart"

    time.sleep(10)

    return next_state


def do_1v1_fight_state(
    vm_index,
    logger: Logger,
    next_state,
    random_fight_mode,
    fight_mode_choosed,
    called_from_launching=False,
):
    """Handle the entirety of the 1v1 battle state (start fight, do fight, end fight)."""

    logger.change_status("do_1v1_fight_state state")
    logger.change_status("Waiting for 1v1 battle to start")

    print(f"Random fight mode is {random_fight_mode} in do_1v1_fight_state()")
    print(f"Fight mode is {fight_mode_choosed}")

    # Wait for battle start
    if wait_for_1v1_battle_start(vm_index, logger) == "restart":
        logger.change_status(
            "Error waiting for 1v1 battle to start in do_1v1_fight_state()"
        )
        return "restart"

    logger.change_status("Battle started!")
    logger.change_status("Starting fight loop")

    # Run regular fight loop if random mode not toggled
    if not random_fight_mode and _1v1_fight_loop(vm_index, logger) == "restart":
        logger.log("Failure in fight loop")
        return "restart"

    # Run random fight loop if random mode toggled
    if random_fight_mode and _1v1_random_fight_loop(vm_index, logger) == "restart":
        logger.log("Failure in fight loop")
        return "restart"

    # Only log the fight if not called from the start
    if not called_from_launching:
        logger.add_1v1_fight()
        if fight_mode_choosed == "trophy_road":
            logger.increment_trophy_road_fights()
        elif fight_mode_choosed == "path_of_legends":
            logger.increment_path_of_legends_fights()
    time.sleep(10)
    return next_state


def check_both_1v1_modes_available(vm_index):
    """
    Check if the Path of Legends mode is available, indicating that both 1v1 modes are available.

    Args:
        vm_index (int): Index of the virtual machine.

    Returns:
        bool: True if Path of Legends mode is available (implying both modes are available), False otherwise.
    """
    iar = numpy.asarray(screenshot(vm_index))

    # Define positions and their expected colors
    positions_and_colors = {
        (439, 279): [
            [35, 205, 255],
            [82, 249, 255],
        ],
        (435, 279): [
            [63, 214, 255],
            [81, 252, 255],
        ],
    }

    # Iterate through each position and set of expected colors
    for position, expected_colors in positions_and_colors.items():
        # numpy arrays are accessed with [row, column], so use y before x
        y, x = position
        battle_button_pixel = iar[y][x]

        # Check if the color of the pixel matches any of the expected colors with a tolerance
        for expected_color in expected_colors:
            if pixel_is_equal(battle_button_pixel, expected_color, tol=60):
                return True  # If a match is found, return True immediately

    return False  # Return False if no matching colors were found at either position


def check_if_on_path_of_legends_mode(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[415][392],
        iar[386][370],
        iar[410][387],
    ]
    colors = [
        [179, 47, 92],
        [170, 34, 80],
        [181, 48, 92],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=25):
            return False

    return True


def get_current_fight_mode(vm_index):
    # fight_modes = ['trophy_road', 'path_of_legends', 'goblin_queen']
    iar = numpy.asarray(screenshot(vm_index))

    pixels = [
        iar[543][397],
        iar[520][399],
        iar[510][399],
        iar[490][399],
        iar[487][399],
        iar[535][19],
        iar[510][24],
        iar[480][24],
        iar[469][24],
    ]

    # get the average of pixels
    avg_color = [0, 0, 0]
    for p in pixels:
        avg_color[0] += p[0]
        avg_color[1] += p[1]
        avg_color[2] += p[2]

    avg_color[0] = avg_color[0] / len(pixels)
    avg_color[1] = avg_color[1] / len(pixels)
    avg_color[2] = avg_color[2] / len(pixels)

    mode2avgColor = {
        "trophy_road": [95.1, 52.7, 8.5],
        "path_of_legends": [90.5, 25.8, 52.7],
        "goblin_queen": [15.1, 68.7, 11.9],
    }

    diff2mode = {}
    for mode, average_color in mode2avgColor.items():
        diff = 0
        for i in range(3):
            diff += abs(average_color[i] - avg_color[i])
        diff2mode[diff] = mode

    min_diff = min(diff2mode.keys())

    return diff2mode[min_diff]


def set_fight_mode(vm_index, fight_mode):
    # fight_modes = ['trophy_road', 'path_of_legends', 'goblin_queen']

    # if not on clash main, return False
    if check_if_on_clash_main_menu(vm_index) is not True:
        return False

    # click the battle type menu
    click(vm_index, 283, 396)
    time.sleep(2)

    mode2coord = {
        "trophy_road": (194, 288),
        "path_of_legends": (192, 535),
        "goblin_queen": (199, 403),
        "queens_journey": (199, 403),
    }
    print(f"Mode is : {fight_mode}")
    coord = mode2coord[fight_mode]
    print(f"Coord is : {coord}")

    # click the type of fight
    click(vm_index, coord[0], coord[1])
    time.sleep(4)

    return True


def start_1v1_type_fight(vm_index, mode):
    # fight_modes = ['trophy_road', 'path_of_legends', 'goblin_queen']

    # if not on clash main, return False
    if check_if_on_clash_main_menu(vm_index) is not True:
        return False

    # verify we're on goblin queen mode
    if get_current_fight_mode(vm_index) != mode:
        set_fight_mode(vm_index, mode)

    # click start button
    click(vm_index, 175, 403)
    return True


def start_fight(vm_index, logger, mode):
    def do_job_incrementing(logger,mode):
        if mode == 'trophy_road':
            logger.increment_trophy_road_fights()
        elif mode == 'path_of_legends':
            logger.increment_path_of_legends_fights()
        elif mode == 'queens_journey':
            logger.increment_queens_journey_fights()
        elif mode == '2v2':
            logger.increment_2v2_fights()

    # fight_modes = ['trophy_road', 'path_of_legends', 'goblin_queen','2v2']
    logger.change_status(f"Starting a {mode} fight")
    do_job_incrementing(logger,mode)
    if mode == "2v2":
        return start_2v2_fight(vm_index, logger)
    else:
        return start_1v1_type_fight(vm_index, mode)


def start_2v2_fight(vm_index, logger: Logger) -> Boolean:
    """method to handle starting a 2v2 fight"""

    logger.change_status(status="Start fight state")
    logger.change_status(status="Starting 2v2 mode")

    # get to challenges tab
    if get_to_challenges_tab_from_main(vm_index, logger) == "restart":
        return False

    # check for then close popup
    if check_for_challenge_page_on_events_tab(vm_index):
        close_this_challenge_page(vm_index)
        time.sleep(1)

    # scroll up
    for _ in range(10):
        scroll_up_on_left_side_of_screen(vm_index)
    time.sleep(1)

    # if there is a locked events page, return restart
    if check_for_locked_events_page(vm_index):
        logger.change_status("Locked events page!")
        return False

    # click 2v2 icon location
    click_2v2_icon_button(vm_index)
    time.sleep(1)

    # click battle button
    click_2v2_battle_button(vm_index)
    time.sleep(1)

    # click quickmatch button
    click_quickmatch_button(vm_index)
    time.sleep(1)

    return True


def check_for_locked_events_page(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[254][93],
        iar[122][240],
        iar[117][216],
        iar[362][343],
        iar[259][325],
    ]

    colors = [
        [239, 130, 25],
        [91, 227, 153],
        [255, 251, 239],
        [241, 129, 25],
        [239, 130, 27],
    ]

    for i, p in enumerate(pixels):
        # print(p)
        if not pixel_is_equal(p, colors[i], tol=10):
            return False
    return True


def check_for_challenge_page_on_events_tab(vm_index):
    """method to check for the presence of an ongoing challenge page in the events tab"""

    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[612][317],
        iar[600][394],
        iar[16][32],
        iar[21][27],
    ]

    colors = [
        [151, 116, 79],
        [146, 111, 76],
        [156, 231, 255],
        [255, 255, 255],
    ]

    for index, pixel in enumerate(pixels):
        color = colors[index]
        if not pixel_is_equal(pixel, color, tol=35):
            return False
    return True


def close_this_challenge_page(vm_index) -> None:
    """method to close an ongoing challenge page on the events tab"""

    click(
        vm_index,
        CLOSE_THIS_CHALLENGE_PAGE_BUTTON[0],
        CLOSE_THIS_CHALLENGE_PAGE_BUTTON[1],
    )


def click_2v2_icon_button(vm_index) -> None:
    """method to click the 2v2 icon on the challenges tab"""

    click(vm_index, _2V2_BATTLE_ICON_COORD[0], _2V2_BATTLE_ICON_COORD[1])


def click_2v2_battle_button(vm_index) -> None:
    """method to click the 2v2 battle button on the challenges tab"""
    click(vm_index, _2V2_BATTLE_BUTTON_COORD_2[0], _2V2_BATTLE_BUTTON_COORD_2[1])


def click_quickmatch_button(vm_index) -> None:
    """method to click the quickmatch button on the 2v2 battle screen"""

    click(vm_index, QUICKMATCH_BUTTON_COORD[0], QUICKMATCH_BUTTON_COORD[1])


def choose_play_side_barebones(
    vm_index, favorite_side
):  # -> Any | Literal['right', 'left']:
    """method to choose a play side given a favorite side"""

    # get tower_statuses
    tower_statuses = check_enemy_tower_statuses(vm_index)

    # if left is destroyed and right is alive, return right
    if tower_statuses[0] == "destroyed" and tower_statuses[1] == "alive":
        return "right"

    # else, if right is destroyed and left is alive, return left
    if tower_statuses[1] == "destroyed" and tower_statuses[0] == "alive":
        return "left"

    # if neither are destroyed, return favorite_side
    choices = [favorite_side] * 7 + [
        side for side in ["left", "right"] if side != favorite_side
    ] * 3

    return random.choice(choices)


def emote_in_2v2(vm_index, logger: Logger) -> Literal["good"]:
    """method to do an emote in a 2v2 match"""

    logger.change_status("Hitting an emote")

    # click emote button
    click(vm_index, EMOTE_BUTTON_COORD_IN_2V2[0], EMOTE_BUTTON_COORD_IN_2V2[1])
    time.sleep(0.33)

    emote_coord = random.choice(EMOTES_COORDS_IN_2V2)
    click(vm_index, emote_coord[0], emote_coord[1])
    time.sleep(0.33)

    return "good"


def check_if_at_max_elixer(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[612][304],
        iar[612][312],
    ]

    colors = [
        [250, 141, 245],
        [255, 156, 255],
    ]

    for index, pixel in enumerate(pixels):
        color = colors[index]
        if not pixel_is_equal(pixel, color, tol=35):
            return False

    return True


def mag_dump(vm_index, logger):
    card_coords = [
        (137, 559),
        (206, 559),
        (274, 599),
        (336, 555),
    ]

    logger.log("Mag dumping...")
    for index in range(3):
        print(f"mag dump play {index}")
        card_coord = random.choice(card_coords)
        play_coord = (random.randint(101, 440), random.randint(50, 526))

        click(vm_index, card_coord[0], card_coord[1])
        time.sleep(0.1)

        click(vm_index, play_coord[0], play_coord[1])
        time.sleep(0.1)


def wait_for_elixer(
    vm_index, logger, random_elixer_wait
) -> Boolean | Literal["restart"] | Literal["no battle"]:
    """method to wait for 4 elixer during a battle"""

    start_time = time.time()

    while count_elixer(vm_index) <= random_elixer_wait:
        logger.change_status(
            f"Waiting for {random_elixer_wait} elixer for {str(time.time() - start_time)[:4]}s..."
        )

        # play champ ability if its available
        if check_for_champion_ability(vm_index):
            play_champion_ability(vm_index)
            logger.change_status("Played champion ability")

        if len(check_which_cards_are_available(vm_index)) == 4:
            logger.change_status("All cards are available!")
            return True

        if check_if_at_max_elixer(vm_index):
            logger.change_status("Max elixer!")
            break

        if time.time() - start_time > ELIXER_WAIT_TIMEOUT:
            logger.change_status(status="Waited too long for elixer")
            return "restart"

        if not check_for_in_battle_with_delay(vm_index):
            logger.change_status(status="Not in battle, stopping waiting for elixer.")
            return "no battle"

    logger.change_status(
        f"Took {str(time.time() - start_time)[:4]}s for {random_elixer_wait} elixer."
    )

    return True


def count_elixer(vm_index) -> bool:
    """method to check for 4 elixer during a battle"""

    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[613][149],
        iar[613][165],
        iar[613][188],
        iar[613][212],
        iar[613][240],
        iar[613][262],
        iar[613][287],
        iar[613][314],
        iar[613][339],
        iar[613][364],
    ]

    positive_color = [255, 164, 255]

    bool_list = []

    for p in pixels:
        if pixel_is_equal(p, positive_color, tol=65):
            bool_list.append(True)

    return sum(bool_list)


def check_enemy_tower_statuses(
    vm_index,
) -> tuple[Literal["alive", "destroyed"], Literal["alive", "destroyed"]]:
    """method to scan pixels during a battle to determine
    which of  the enemy towers are alive or destroyed"""

    # 'alive'
    # or
    # 'destroyed'

    iar = numpy.asarray(screenshot(vm_index))

    left_tower_pixel = iar[117][102]
    right_tower_pixel = iar[118][280]

    left_tower_pixel = [
        left_tower_pixel[2],
        left_tower_pixel[1],
        left_tower_pixel[0],
    ]
    right_tower_pixel = [
        right_tower_pixel[2],
        right_tower_pixel[1],
        right_tower_pixel[0],
    ]

    left_tower_status = "destroyed"
    if pixel_is_equal([187, 143, 44], left_tower_pixel, tol=30):
        left_tower_status = "alive"

    right_tower_status = "destroyed"
    if pixel_is_equal([232, 188, 44], right_tower_pixel, tol=30):
        right_tower_status = "alive"

    return (left_tower_status, right_tower_status)


def end_fight_state(
    vm_index, logger: Logger, next_state, disable_win_tracker_toggle=True
):
    """method to handle the time after a fight and before the next state"""
    # count the crown score on this end-battle screen

    # get to clash main after this fight
    logger.log("Getting to clash main after doing a fight")
    if get_to_main_after_fight(vm_index, logger) is False:
        logger.log("Erro 69a3d69 Failed to get to clash main after a fight")
        return "restart"

    logger.log("Made it to clash main after doing a fight")
    time.sleep(3)

    # check if the prev game was a win
    if not disable_win_tracker_toggle:
        win_check_return = check_if_previous_game_was_win(vm_index, logger)

        if win_check_return == "restart":
            logger.log("Error 885869 Failed while checking if previous game was a win")
            return "restart"

        if win_check_return:
            logger.add_win()
            return next_state

        logger.add_loss()
    else:
        logger.log("Not checking win/loss because check is disabled")

    return next_state


def check_if_previous_game_was_win(
    vm_index, logger: Logger
) -> bool | Literal["restart"]:
    """method to handle the checking if the previous game was a win or loss"""

    logger.change_status(status="Checking if last game was a win/loss")

    # Use wait_for_clash_main_menu to ensure we are on the main menu.
    if not wait_for_clash_main_menu(vm_index, logger, deadspace_click=True):
        logger.change_status(status='Error Not on main menu, returning "restart"')
        return "restart"

    # get to clash main options menu
    if get_to_activity_log(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 8967203948 get_to_activity_log() in check_if_previous_game_was_win()"
        )

        return "restart"

    logger.change_status(status="Checking if last game was a win...")
    is_a_win = check_pixels_for_win_in_battle_log(vm_index)
    logger.change_status(status=f"Last game is win: {is_a_win}")

    # close battle log
    logger.change_status(status="Returning to clash main")
    click(vm_index, CLOSE_BATTLE_LOG_BUTTON[0], CLOSE_BATTLE_LOG_BUTTON[1])
    if wait_for_clash_main_menu(vm_index, logger) is False:
        logger.change_status(
            status="Error 95867235 wait_for_clash_main_menu() in check_if_previous_game_was_win()"
        )
        return "restart"
    time.sleep(2)

    return is_a_win


def check_pixels_for_win_in_battle_log(vm_index) -> bool:
    """method to check pixels that appear in the battle
    log to determing if the previous game was a win"""

    line1 = check_line_for_color(
        vm_index, x_1=47, y_1=135, x_2=109, y_2=154, color=(255, 51, 102)
    )
    line2 = check_line_for_color(
        vm_index, x_1=46, y_1=152, x_2=115, y_2=137, color=(255, 51, 102)
    )
    line3 = check_line_for_color(
        vm_index, x_1=47, y_1=144, x_2=110, y_2=147, color=(255, 51, 102)
    )

    if line1 and line2 and line3:
        return False
    return True


def find_exit_battle_button(vm_index):
    folder = "exit_battle_button"

    names = make_reference_image_list(get_file_count(folder))
    locations: list[list[int] | None] = find_references(
        screenshot(vm_index),
        folder,
        names,
        tolerance=0.9,
    )

    coord = get_first_location(locations)

    if coord is None:
        return None

    return [coord[1], coord[0]]


def find_ok_battle_button2(vm_index):
    iar = numpy.asarray(screenshot(vm_index))

    pixels = [
        iar[545][178],
        iar[547][239],
        iar[553][214],
        iar[554][201],
    ]

    colors = [
        [255, 187, 104],
        [255, 187, 104],
        [255, 255, 255],
        [255, 255, 255],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=20):
            return False
    return True


def find_ok_battle_button(vm_index):
    if find_ok_battle_button2(vm_index):
        print("Used find_ok_battle_button2 patch-job")
        return (200, 550)

    folder = "ok_post_battle_button"

    names = make_reference_image_list(get_file_count(folder))
    locations: list[list[int] | None] = find_references(
        screenshot(vm_index),
        folder,
        names,
        tolerance=0.85,
    )

    coord = get_first_location(locations)

    if coord is None:
        return None

    return [coord[1], coord[0]]


def get_to_main_after_fight(vm_index, logger):
    timeout = 120  # s
    start_time = time.time()
    clicked_ok_or_exit = False

    logger.change_status("Returning to clash main after the fight...")

    while time.time() - start_time < timeout:

        # if on clash main
        if check_if_on_clash_main_menu(vm_index) is True:
            # wait 3 seconds for the trophy road page to maybe appear bc of UI lag
            time.sleep(3)

            # if that trophy road page appears, handle it, then return True
            if check_for_trophy_reward_menu(vm_index):
                print("Found trophy reward menu")
                handle_trophy_reward_menu(vm_index, logger, printmode=False)
                time.sleep(2)

            print("Made it to clash main after a fight")
            return True


        # check for trophy reward screen
        if check_for_trophy_reward_menu(vm_index):
            print("Found trophy reward menu!\nHandling Trophy Reward Menu")
            handle_trophy_reward_menu(vm_index, logger, printmode=False)
            time.sleep(3)
            continue


        # check for OK button after battle
        if not clicked_ok_or_exit:
            ok_button_coord = find_ok_battle_button(vm_index)
            if ok_button_coord is None:
                ok_button_coord = find_exit_battle_button(vm_index)
            if ok_button_coord is not None:
                print("Found OK button, clicking it.")
                click(vm_index, ok_button_coord[0], ok_button_coord[1])
                clicked_ok_or_exit = True
                continue


        # if on events page, click clash main button
        if check_for_events_page(vm_index):
            print("Found events page, clicking clash main button.")
            click(vm_index, 179, 600)
            time.sleep(3)
            continue
        else:
            print("Not on events page...")

        time.sleep(1)
        print("Clicking on deadspace to close potential pop-up windows.")
        click(vm_index, 1, 435)

    return False


# main fight loops


def play_a_card(vm_index, logger) -> Boolean:
    print("\n")

    # check which cards are available
    logger.change_status("Looking at which cards are available")
    available_card_check_start_time = time.time()
    card_indicies = check_which_cards_are_available(vm_index)
    available_card_check_time_taken = str(
        time.time() - available_card_check_start_time
    )[:3]
    logger.change_status(
        f"These cards are available: {card_indicies} ({available_card_check_time_taken}s)"
    )

    # pick a random card index
    if len(card_indicies) == 0:
        logger.change_status("No cards ready yet...")
        return False

    card_index = random.choice(card_indicies)
    logger.change_status(f"Choosing this card index: {card_index}")

    # get a coord based on the selected side
    play_coord_calculation_start_time = time.time()
    card_id, play_coord = get_play_coords_for_card(vm_index, logger,card_index, 'left')
    play_coord_calculation_time_taken = str(
        time.time() - play_coord_calculation_start_time
    )[:3]

    # if coord is none for whatever reason, just skip this play
    if play_coord is None:
        logger.change_status("Bad play coord. Redoing...")
        return False

    logger.change_status(
        f"Calculated play for: {card_id} at {play_coord} ({play_coord_calculation_time_taken}s)"
    )

    # click the card index
    click_and_play_card_start_time = time.time()
    random_card_coord = HAND_CARDS_COORDS[card_index]
    click(vm_index, random_card_coord[0], random_card_coord[1])
    time.sleep(0.1)

    # click the play coord
    click(vm_index, play_coord[0], play_coord[1])
    logger.add_card_played()
    click_and_play_card_time_taken = str(time.time() - click_and_play_card_start_time)[
        :3
    ]
    logger.change_status(f"Made the play {click_and_play_card_time_taken}s")

    return True


def verify_matt_pc():
    import socket

    computer_name = socket.gethostname()
    if computer_name == "MATT-PC":
        return True
    return False


import os
from PIL import Image
import cv2


def save_fight_image(vm_index):
    if random.randint(0,1)==1:
        print('Skipping saving fight image')
        return

    # screenshot twice
    start_time = time.time()

    # Assuming screenshot() returns a BGR NumPy array
    bgr_image = screenshot(vm_index)

    # Convert BGR to RGB
    rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)

    # Convert NumPy array to PIL image
    image = Image.fromarray(rgb_image)

    folder_path = yolo_images_save_path

    if not verify_matt_pc():
        return

    if os.path.exists(folder_path):
        # print("Folder exists.")
        pass
    else:
        print("Folder doesnt exist.")

        return

    path = os.path.join(
        folder_path, f"screenshot{time.time() + random.randint(0, 9)}.png"
    )
    image.save(path)

    print(f"saved fight image in {str(time.time() - start_time)[:3]}s")


def _2v2_fight_loop(vm_index: int, logger: Logger):
    prev_cards_played = logger.get_cards_played()

    while check_for_in_battle_with_delay(vm_index):

        random_elixer_wait_count = random.randint(3, 7)

        wait_output = wait_for_elixer(vm_index, logger, random_elixer_wait_count)
        if SAVE_FIGHT_IMAGES:
            save_fight_image(vm_index)

        if wait_output == "restart":
            logger.change_status("Failure while waiting for elixer")
            return "restart"

        if wait_output == "no battle":
            logger.change_status("Not in a 1v1 battle anymore!")
            break

        if not check_if_in_battle(vm_index):
            "Not in a battle anymore"
            break

        print("playing a card in 2v2...")
        play_start_time = time.time()
        if play_a_card(vm_index, logger) is False:
            logger.change_status("Failed to play a card, retrying...")
        play_time_taken = str(time.time() - play_start_time)[:4]
        logger.change_status(f"Made a play in {play_time_taken}s")

    logger.change_status("End of the 2v2 fight!")
    time.sleep(3)
    cards_played = logger.get_cards_played()
    logger.change_status(f"Played ~{cards_played - prev_cards_played} cards this fight")

    return "good"


def check_for_champion_ability(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[462][324],
        iar[453][334],
        iar[462][336],
    ]
    colors = [
        [215, 28, 223],
        [240, 39, 254],
        [239, 40, 251],
    ]

    # for p in pixels:print(p)

    for p in pixels:
        for c in colors:
            if pixel_is_equal(p, c, tol=30):
                return True

    return False


def play_champion_ability(vm_index):
    click(vm_index, 330, 460)


def _1v1_fight_loop(vm_index, logger: Logger) -> Literal["restart", "good"]:
    """method for handling dynamicly timed 1v1 fight"""

    logger.change_status(status="Starting battle loop")

    # choose a side to favor this fight
    favorite_side = random.choice(["left", "right"])

    logger.change_status(status=f"Going to favor {favorite_side} this fight...")

    # count plays
    plays = 0
    prev_cards_played = logger.get_cards_played()

    # while in battle:
    while check_if_in_battle(vm_index):
        print("\n")
        logger.log(f"Battle play #{plays}:")

        # wait for 6 elixer
        random_elixer_wait = random.randint(3, 7)
        elixer_wait_return = wait_for_elixer(vm_index, logger, random_elixer_wait)
        if SAVE_FIGHT_IMAGES:
            save_fight_image(vm_index)
        # if a failure during elixer wait
        if elixer_wait_return == "restart":
            logger.change_status(
                status="Error 788455 wait_for_6_elixer() in fight_loop()"
            )
            return "restart"

        # if the battle is over
        if elixer_wait_return == "no battle":
            break

        # make a play
        print("Playing a card in 1v1...")
        play_start_time = time.time()
        if play_a_card(vm_index, logger) is False:
            logger.change_status("Failed to play a card, retrying...")

        play_time_taken = str(time.time() - play_start_time)[:4]
        logger.change_status(f"Made a play in {play_time_taken}s")
        plays += 1

    cards_played = logger.get_cards_played()
    logger.change_status(
        f"Played ~{cards_played - prev_cards_played} cards this 1v1 game"
    )
    return "good"


def _2v2_random_fight_loop(vm_index, logger: Logger):
    """method to handle a dynamicly timed 2v2 fight"""
    start_time = time.time()

    # while in battle:
    while check_for_in_battle_with_delay(vm_index):
        this_play_start_time = time.time()

        time.sleep(8)

        mag_dump(vm_index, logger)

        # emote sometimes to do daily challenge (jk its to be funny and annoy ur teammate)
        if time.time() - start_time > 30 and random.randint(0, 10) == 1:
            emote_in_2v2(vm_index, logger)

        # increment plays counter
        logger.change_status(
            f"Made a play in 2v2 mode in {str(time.time() - this_play_start_time)[:4]}\n"
        )

    logger.change_status("Finished with this 2v2 fight")

    return "good"


def _1v1_random_fight_loop(vm_index, logger):
    """method for handling dynamicly timed 1v1 fight"""

    logger.change_status(status="Starting 1v1 battle with random plays")

    mag_dump(vm_index, logger)
    for _ in range(random.randint(1, 3)):
        logger.add_card_played()

    # while in battle:
    while check_if_in_battle(vm_index):
        time.sleep(8)

        mag_dump(vm_index, logger)
        for _ in range(random.randint(1, 3)):
            logger.add_card_played()

    logger.change_status("Finished with 1v1 battle with random plays...")
    return "good"


if __name__ == "__main__":
    pass
