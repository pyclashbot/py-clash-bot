"""random module for randomizing fight plays"""

import collections
import random
import time
from typing import Literal

import numpy

from  pyclashbot.bot.recorder import save_image, save_win_loss

from pyclashbot.bot.card_detection import (
    check_which_cards_are_available,
    create_default_bridge_iar,
    get_play_coords_for_card,
    switch_side,
)
from pyclashbot.bot.nav import (
    check_for_events_page,
    check_for_in_battle_with_delay,
    check_for_trophy_reward_menu,
    check_if_in_battle,
    check_if_on_clash_main_menu,
    get_to_activity_log,
    get_to_challenges_tab_from_main,
    handle_trophy_reward_menu,
    wait_for_1v1_battle_start,
    wait_for_2v2_battle_start,
    wait_for_clash_main_menu,
)
from pyclashbot.detection.image_rec import (
    check_line_for_color,
    find_references,
    get_file_count,
    get_first_location,
    make_reference_image_list,
    pixel_is_equal,
)
from pyclashbot.bot.recorder import save_play

from pyclashbot.utils.logger import Logger


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
    (124, 419),
    (182, 420),
    (255, 411),
    (312, 423),
    # (144, 545),
    # (327, 544),
    (133, 471),
    (188, 472),
    (243, 469),
    (308, 470),
]
CLASH_MAIN_DEADSPACE_COORD = (20, 520)


ELIXIR_COORDS = [
    [613, 149],
    [613, 165],
    [613, 188],
    [613, 212],
    [613, 240],
    [613, 262],
    [613, 287],
    [613, 314],
    [613, 339],
    [613, 364],
]
ELIXIR_COLOR = [240, 137, 244]


def do_1v1_fight_state(
    emulator,
    logger: Logger,
    random_fight_mode,
    fight_mode_choosed,
    called_from_launching=False,
    recording_flag: bool = False,
) -> bool:
    """Handle the entirety of the 1v1 battle state (start fight, do fight, end fight)."""

    logger.change_status("do_1v1_fight_state state")
    logger.change_status("Waiting for 1v1 battle to start")

    # Wait for battle start
    if wait_for_1v1_battle_start(emulator, logger) is False:
        logger.change_status(
            "Error waiting for 1v1 battle to start in do_1v1_fight_state()",
        )
        return False

    logger.change_status("Starting fight loop")

    # Run regular fight loop if random mode not toggled
    if (
        not random_fight_mode
        and _1v1_fight_loop(emulator, logger, recording_flag) is False
    ):
        logger.log("Failure in fight loop")
        return False

    # Run random fight loop if random mode toggled
    if (
        random_fight_mode
        and _1v1_random_fight_loop(emulator, logger) is False
    ):
        logger.log("Failure in fight loop")
        return False

    # Only log the fight if not called from the start
    if not called_from_launching:
        logger.add_1v1_fight()
        if fight_mode_choosed == "trophy_road":
            logger.increment_trophy_road_fights()

    time.sleep(10)
    return True


def check_both_1v1_modes_available(emulator):
    """Check if the Path of Legends mode is available, indicating that both 1v1 modes are available.

    Args:
    ----
        emulator (int): Index of the virtual machine.

    Returns:
    -------
        bool: True if Path of Legends mode is available (implying both modes are available), False otherwise.

    """
    iar = emulator.screenshot()

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


def check_if_on_path_of_legends_mode(emulator):
    iar = emulator.screenshot()
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


def get_current_fight_mode(emulator):
    # fight_modes = ['trophy_road', 'path_of_legends']
    iar = emulator.screenshot()

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
        avg_color[0] += int(p[0])
        avg_color[1] += int(p[1])
        avg_color[2] += int(p[2])

    avg_color[0] = avg_color[0] // len(pixels)
    avg_color[1] = avg_color[1] // len(pixels)
    avg_color[2] = avg_color[2] // len(pixels)

    mode2avgColor = {  # noqa: N806
        "trophy_road": [95.1, 52.7, 8.5],
        "path_of_legends": [90.5, 25.8, 52.7],
    }

    diff2mode = {}
    for mode, average_color in mode2avgColor.items():
        diff = 0
        for i in range(3):
            diff += abs(average_color[i] - avg_color[i])
        diff2mode[diff] = mode

    min_diff = min(diff2mode.keys())

    return diff2mode[min_diff]


def check_for_change_fight_mode_page(emulator):
    iar = numpy.array(emulator.screenshot())
    pixels = [
        iar[132][184],
        iar[135][190],
        iar[140][195],
        iar[142][200],
        iar[144][225],
        iar[146][233],
        iar[148][237],
        iar[177][129],
        iar[193][149],
        iar[188][169],
        iar[184][189],
        iar[180][209],
        iar[187][269],
        iar[197][290],
    ]
    # for p in pixels:print(p)
    colors = [
        [255, 204, 85],
        [245, 196, 83],
        [246, 179, 69],
        [204, 120, 44],
        [247, 141, 27],
        [250, 138, 29],
        [253, 138, 33],
        [250, 110, 0],
        [255, 254, 254],
        [255, 255, 255],
        [255, 255, 255],
        [247, 228, 213],
        [193, 159, 135],
        [219, 83, 0],
    ]
    for i, c in enumerate(colors):
        if not pixel_is_equal(pixels[i], c, tol=10):
            return False

    return True


def set_fight_mode(emulator, fight_mode):
    # fight_modes = ['trophy_road', 'path_of_legends']

    # if not on clash main, return False
    if check_if_on_clash_main_menu(emulator) is not True:
        return False

    # click the battle type menu
    emulator.click(283, 396)
    time.sleep(2)

    mode2coord = {
        "trophy_road": (200, 400),
        "path_of_legends": (200, 550),
    }
    coord = mode2coord[fight_mode]
    print(f"This mode {fight_mode} has coord at {coord}")

    # click the type of fight
    emulator.click(coord[0], coord[1])
    time.sleep(3)

    # if the fight mode change page is still open, the
    # change was unsuccessful, and we must close the page
    close_fight_mode_change_page_coord = (200, 140)
    if check_for_change_fight_mode_page(emulator):
        print(
            f"Failed to change to fight mode: {fight_mode}. This is likely because the fight mode is not unlocked yet."
        )
        emulator.click(*close_fight_mode_change_page_coord)
        time.sleep(1)
        return False

    return True


def start_1v1_type_fight(emulator, logger: Logger, mode: str) -> bool:
    # fight_modes = ['trophy_road', 'path_of_legends']

    # if not on clash main, return False
    if check_if_on_clash_main_menu(emulator) is not True:
        print("Not on clash main for start_1v1_type_fight()")
        return False

    # verify we're on the right mode
    if get_current_fight_mode(emulator) != mode:
        print(
            f"Current {get_current_fight_mode(emulator)} != {mode}, setting fight mode"
        )
        if set_fight_mode(emulator, mode) is False:
            print("This mode isn't available yet. Doing a regular 1v1 instead...")
            logger.increment_trophy_road_fights()

    # click start button FIXED
    emulator.click(203, 487)
    return True


def start_fight(emulator, logger, mode) -> bool:
    print("within start_fight")

    # fight_modes = ['trophy_road', 'path_of_legends', '2v2']
    def increment_fight_mode_count(logger, mode):
        if mode == "trophy_road":
            logger.increment_trophy_road_fights()

    logger.change_status(f"Starting a {mode} fight")
    increment_fight_mode_count(logger, mode)
    if mode == "2v2":
        print(f"{mode} is of 2v2 type")
        return start_2v2_fight(emulator, logger)

    print(f"{mode} is of 1v1 type")
    return start_1v1_type_fight(emulator, logger, mode)


def scroll_up_on_left_side_of_screen(emulator):
    """Method for scrolling up faster when interacting with a scrollable menu"""
    emulator.scroll(66, 300, 66, 400)


def start_2v2_fight(emulator, logger: Logger) -> bool:
    """Method to handle starting a 2v2 fight"""
    logger.change_status(status="Start fight state")
    logger.change_status(status="Starting 2v2 mode")

    # get to challenges tab
    if get_to_challenges_tab_from_main(emulator, logger) == "restart":
        return False

    # check for then close popup
    if check_for_challenge_page_on_events_tab(emulator):
        close_this_challenge_page(emulator)
        for _ in range(10):
            scroll_up_on_left_side_of_screen(emulator)
        time.sleep(1)

    # scroll up
    for _ in range(3):
        scroll_up_on_left_side_of_screen(emulator)
    time.sleep(1)

    # if there is a locked events page, return restart
    if check_for_locked_events_page(emulator):
        logger.change_status("Locked events page!")
        return False

    # click 2v2 icon location
    click_2v2_icon_button(emulator)
    time.sleep(0.41)

    # click battle button
    click_2v2_battle_button(emulator)
    time.sleep(0.4)

    # click quickmatch button
    click_quickmatch_button(emulator)
    time.sleep(0.3)

    return True


def check_for_locked_events_page(emulator):
    iar = emulator.screenshot()
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
        if not pixel_is_equal(p, colors[i], tol=10):
            return False
    return True


def check_for_challenge_page_on_events_tab(emulator):
    """Method to check for the presence of an ongoing challenge page in the events tab"""
    iar = emulator.screenshot()
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


def close_this_challenge_page(emulator) -> None:
    """Method to close an ongoing challenge page on the events tab"""
    emulator.click(
        CLOSE_THIS_CHALLENGE_PAGE_BUTTON[0],
        CLOSE_THIS_CHALLENGE_PAGE_BUTTON[1],
    )


def click_2v2_icon_button(emulator) -> None:
    """Method to click the 2v2 icon on the challenges tab"""
    emulator.click(_2V2_BATTLE_ICON_COORD[0], _2V2_BATTLE_ICON_COORD[1])


def click_2v2_battle_button(emulator) -> None:
    """Method to click the 2v2 battle button on the challenges tab"""
    emulator.click(_2V2_BATTLE_BUTTON_COORD_2[0], _2V2_BATTLE_BUTTON_COORD_2[1])


def click_quickmatch_button(emulator) -> None:
    """Method to click the quickmatch button on the 2v2 battle screen"""
    emulator.click(QUICKMATCH_BUTTON_COORD[0], QUICKMATCH_BUTTON_COORD[1])


def emote_in_2v2(emulator, logger: Logger):
    """Method to do an emote in a 2v2 match"""
    logger.change_status("Hitting an emote")

    # click emote button
    emulator.click(EMOTE_BUTTON_COORD_IN_2V2[0], EMOTE_BUTTON_COORD_IN_2V2[1])
    time.sleep(0.33)

    emote_coord = random.choice(EMOTES_COORDS_IN_2V2)
    emulator.click(emote_coord[0], emote_coord[1])


def mag_dump(emulator, logger):
    card_coords = [
        (137, 559),
        (206, 559),
        (274, 599),
        (336, 555),
    ]

    logger.log("Mag dumping...")
    for index in range(3):
        print(f"mag dump play {index}")
        card_index = random.randint(0, 3)
        card_coord = card_coords[card_index]
        play_coord = (random.randint(101, 440), random.randint(50, 526))

        # record play here

        emulator.click(card_coord[0], card_coord[1])
        time.sleep(0.1)

        emulator.click(play_coord[0], play_coord[1])
        time.sleep(0.1)



def wait_for_elixer(
    emulator,
    logger,
    random_elixer_wait,
    WAIT_THRESHOLD=5000,  # noqa: N803
    PLAY_THRESHOLD=10000,  # noqa: N803
    recording_flag: bool = False,
) -> Literal["restart", "no battle"] | bool:
    """Method to wait for 4 elixer during a battle"""
    start_time = time.time()

    while not count_elixer(emulator, random_elixer_wait):
        if recording_flag:
            save_image(emulator.screenshot())
        
        wait_time = time.time() - start_time
        logger.change_status(
            f"Waiting for {random_elixer_wait} elixer for {str(wait_time)[:4]}s...",
        )

        card_inhand = len(check_which_cards_are_available(emulator, True, False))
        action_offset, _ = switch_side()
        if action_offset > PLAY_THRESHOLD and card_inhand > 0:
            logger.change_status("Too much going on, playing now")
            return True

        if action_offset > WAIT_THRESHOLD and card_inhand == 4:
            logger.change_status("All cards are available!")
            return True

        if wait_time > ELIXER_WAIT_TIMEOUT:
            logger.change_status(status="Waited too long for elixer")
            return "restart"

        if not check_for_in_battle_with_delay(emulator):
            logger.change_status(status="Not in battle, stopping waiting for elixer.")
            return "no battle"

    logger.change_status(
        f"Took {str(time.time() - start_time)[:4]}s for {random_elixer_wait} elixer.",
    )

    return True


def count_elixer(emulator, elixer_count) -> bool:
    """Method to check for 4 elixer during a battle"""
    iar = emulator.screenshot()

    if pixel_is_equal(
        iar[ELIXIR_COORDS[elixer_count - 1][0], ELIXIR_COORDS[elixer_count - 1][1]],
        ELIXIR_COLOR,
        tol=65,
    ):
        return True
    return False


def end_fight_state(
    emulator,
    logger: Logger,recording_flag,
    disable_win_tracker_toggle=True,
):
    """Method to handle the time after a fight and before the next state"""
    # count the crown score on this end-battle screen

    # get to clash main after this fight
    logger.log("Getting to clash main after doing a fight")
    if get_to_main_after_fight(emulator, logger) is False:
        logger.log("Error 69a3d69 Failed to get to clash main after a fight")
        return False

    logger.log("Made it to clash main after doing a fight")
    time.sleep(3)

    # check if the prev game was a win
    if not disable_win_tracker_toggle:
        win_check_return = check_if_previous_game_was_win(emulator, logger)

        if win_check_return == "restart":
            logger.log("Error 885869 Failed while checking if previous game was a win")
            return False

        if win_check_return:
            logger.add_win()

            if recording_flag: 
                save_win_loss('win')
            return True

        logger.add_loss()
        if recording_flag: 
            save_win_loss('loss')
    else:
        logger.log("Not checking win/loss because check is disabled")

    return True


def check_if_previous_game_was_win(
    emulator,
    logger: Logger,
) -> bool | Literal["restart"]:
    """Method to handle the checking if the previous game was a win or loss"""
    logger.change_status(status="Checking if last game was a win/loss")

    # Use wait_for_clash_main_menu to ensure we are on the main menu.
    if not wait_for_clash_main_menu(emulator, logger, deadspace_click=True):
        logger.change_status(status='Error Not on main menu, returning "restart"')
        return "restart"

    # get to clash main options menu
    if get_to_activity_log(emulator, logger, printmode=False) == "restart":
        logger.change_status(
            status="Error 8967203948 get_to_activity_log() in check_if_previous_game_was_win()",
        )

        return "restart"

    logger.change_status(status="Checking if last game was a win...")
    is_a_win = check_pixels_for_win_in_battle_log(emulator)
    logger.change_status(status=f"Last game is win: {is_a_win}")

    # close battle log
    logger.change_status(status="Returning to clash main")
    emulator.click(CLOSE_BATTLE_LOG_BUTTON[0], CLOSE_BATTLE_LOG_BUTTON[1])
    if wait_for_clash_main_menu(emulator, logger) is False:
        logger.change_status(
            status="Error 95867235 wait_for_clash_main_menu() in check_if_previous_game_was_win()",
        )
        return "restart"
    time.sleep(2)

    return is_a_win


def check_pixels_for_win_in_battle_log(emulator) -> bool:
    """Method to check pixels that appear in the battle
    log to determing if the previous game was a win
    """
    line1 = check_line_for_color(
        emulator,
        x_1=47,
        y_1=135,
        x_2=109,
        y_2=154,
        color=(255, 51, 102),
    )
    line2 = check_line_for_color(
        emulator,
        x_1=46,
        y_1=152,
        x_2=115,
        y_2=137,
        color=(255, 51, 102),
    )
    line3 = check_line_for_color(
        emulator,
        x_1=47,
        y_1=144,
        x_2=110,
        y_2=147,
        color=(255, 51, 102),
    )

    if line1 and line2 and line3:
        return False
    return True


def find_exit_battle_button(emulator):
    folder = "exit_battle_button"

    names = make_reference_image_list(get_file_count(folder))
    locations: list[list[int] | None] = find_references(
        emulator.screenshot(),
        folder,
        names,
        tolerance=0.9,
    )

    coord = get_first_location(locations)

    if coord is None:
        return None

    return [coord[1], coord[0]]


def find_ok_battle_button2(emulator):
    iar = emulator.screenshot()

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


def find_ok_battle_button(emulator):
    if find_ok_battle_button2(emulator):
        print("Used find_ok_battle_button2 patch-job")
        return (200, 550)

    folder = "ok_post_battle_button"

    names = make_reference_image_list(get_file_count(folder))
    locations: list[list[int] | None] = find_references(
        emulator.screenshot(),
        folder,
        names,
        tolerance=0.85,
    )

    coord = get_first_location(locations)

    if coord is None:
        return None

    return [coord[1], coord[0]]


def get_to_main_after_fight(emulator, logger):
    timeout = 120  # s
    start_time = time.time()
    clicked_ok_or_exit = False

    logger.change_status("Returning to clash main after the fight...")

    while time.time() - start_time < timeout:
        # if on clash main
        if check_if_on_clash_main_menu(emulator) is True:
            # wait 3 seconds for the trophy road page to maybe appear bc of UI lag
            time.sleep(3)

            # if that trophy road page appears, handle it, then return True
            if check_for_trophy_reward_menu(emulator):
                print("Found trophy reward menu")
                handle_trophy_reward_menu(emulator, logger, printmode=False)
                time.sleep(2)

            print("Made it to clash main after a fight")
            return True

        # check for trophy reward screen
        if check_for_trophy_reward_menu(emulator):
            print("Found trophy reward menu!\nHandling Trophy Reward Menu")
            handle_trophy_reward_menu(emulator, logger, printmode=False)
            time.sleep(3)
            continue

        # check for OK button after battle
        if not clicked_ok_or_exit:
            ok_button_coord = find_ok_battle_button(emulator)
            if ok_button_coord is None:
                ok_button_coord = find_exit_battle_button(emulator)
            if ok_button_coord is not None:
                print("Found OK button, clicking it.")
                emulator.click(ok_button_coord[0], ok_button_coord[1])
                clicked_ok_or_exit = True
                continue

        # if on events page, click clash main button
        if check_for_events_page(emulator):
            print("Found events page, clicking clash main button.")
            emulator.click(179, 600)
            time.sleep(3)
            continue
        print("Not on events page...")

        time.sleep(1)
        print("Clicking on deadspace to close potential pop-up windows.")
        emulator.click(CLASH_MAIN_DEADSPACE_COORD[0], CLASH_MAIN_DEADSPACE_COORD[1])

    return False


# main fight loops

# Initialize a deque with a maximum length of 3 to store the last three chosen cards
last_three_cards = collections.deque(maxlen=3)


def select_card_index(card_indices, last_three_cards):
    if not card_indices:
        raise ValueError("card_indices cannot be empty")

    # First preference: Cards not in the last_three_cards queue
    preferred_cards = [index for index in card_indices if index not in last_three_cards]

    # Second preference: Cards not among the last two added to the queue
    if not preferred_cards and len(last_three_cards) == 3:
        preferred_cards = [
            index for index in card_indices if index not in list(last_three_cards)[-2:]
        ]

    # Third preference: Any card except the most recently added one
    if not preferred_cards and last_three_cards:
        preferred_cards = [
            index for index in card_indices if index != last_three_cards[-1]
        ]

    # Fallback: If all else fails, consider all cards
    if not preferred_cards:
        preferred_cards = card_indices

    return random.choice(preferred_cards)


def play_a_card(emulator, logger, recording_flag: bool) -> bool:
    print("\n")

    # check which cards are available
    logger.change_status("Looking at which cards are available")
    available_card_check_start_time = time.time()
    card_indicies = check_which_cards_are_available(emulator, False, True)

    if not card_indicies:
        logger.change_status("No cards ready yet...")
        return False

    available_card_check_time_taken = str(
        time.time() - available_card_check_start_time,
    )[:3]

    logger.change_status(
        f"These cards are available: {card_indicies} ({available_card_check_time_taken}s)",
    )

    card_index = select_card_index(card_indicies, last_three_cards)
    if card_index not in last_three_cards:
        last_three_cards.append(card_index)
    logger.change_status(f"Choosing this card index: {card_index}")

    # get a coord based on the selected side
    play_coord_calculation_start_time = time.time()
    card_id, play_coord = get_play_coords_for_card(emulator, logger, card_index)
    play_coord_calculation_time_taken = str(
        time.time() - play_coord_calculation_start_time,
    )[:3]

    logger.change_status(
        f"Calculated play for: {card_id} at {play_coord} ({play_coord_calculation_time_taken}s)",
    )

    # click the card index
    click_and_play_card_start_time = time.time()
    if None in [HAND_CARDS_COORDS, card_index]:
        print("[!] Non fatal error: card_index is None")
        return False

    emulator.click(HAND_CARDS_COORDS[card_index][0], HAND_CARDS_COORDS[card_index][1])

    # click the play coord
    if play_coord is None:
        print("[!] Non fatal error: play_coord is None")
        return False

    emulator.click(play_coord[0], play_coord[1])
    click_and_play_card_time_taken = str(time.time() - click_and_play_card_start_time)[
        :3
    ]
    if recording_flag:
        save_play(play_coord, card_index)

    logger.change_status(f"Made the play {click_and_play_card_time_taken}s")
    logger.add_card_played()

    if random.randint(0, 9) == 1:
        emote_in_2v2(emulator, logger)
    return True


elixer_count = [3, 4, 5, 6, 7, 8, 9]
percentage_first_5 = [0, 0, 0, 0, 0.3, 0.3, 0.4]
percentage_single = [0.05, 0.05, 0.1, 0.15, 0.15, 0.3, 0.2]
percentage_double = [0.05, 0.05, 0.1, 0.15, 0.25, 0.3, 0.1]
percentage_triple = [0.05, 0.05, 0.1, 0.1, 0.3, 0.4, 0]
global elapsed_time  # noqa: PLW0604


def _2v2_fight_loop(emulator, logger: Logger, recording_flag: bool):
    # this needs comments
    create_default_bridge_iar(emulator)
    collections.deque(maxlen=3)
    ingame_time = time.time()
    prev_cards_played = logger.get_cards_played()
    while check_for_in_battle_with_delay(emulator):
        global elapsed_time
        elapsed_time = time.time() - ingame_time
        if elapsed_time < 7:  # Less than 5 seconds
            percentage = percentage_first_5
            WAIT_THRESHOLD = 6000  # noqa: N806
            PLAY_THRESHOLD = 10000  # noqa: N806
        elif elapsed_time < 90:  # Less than 2 minutes
            percentage = percentage_single
            WAIT_THRESHOLD = 6000  # noqa: N806
            PLAY_THRESHOLD = 10000  # noqa: N806
        elif elapsed_time < 200:  # Less than 4 minutes
            percentage = percentage_double
            WAIT_THRESHOLD = 7000  # noqa: N806
            PLAY_THRESHOLD = 11000  # noqa: N806
        else:  # 4 minutes or more
            percentage = percentage_triple
            WAIT_THRESHOLD = 8000  # noqa: N806
            PLAY_THRESHOLD = 12000  # noqa: N806

        wait_output = wait_for_elixer(
            emulator,
            logger,
            random.choices(elixer_count, weights=percentage, k=1)[0],
            WAIT_THRESHOLD,
            PLAY_THRESHOLD,
        )

        if wait_output == "restart":
            logger.change_status("Failure while waiting for elixer")
            return "restart"

        if wait_output == "no battle" or not check_if_in_battle(emulator):
            logger.change_status("Not in a 2v2 battle anymore!")
            break

        # print("playing a card in 2v2...")
        play_start_time = time.time()
        if play_a_card(emulator, logger, recording_flag) is False:
            logger.change_status("Failed to play a card, retrying...")
        # play_time_taken = str(time.time() - play_start_time)[:4]
        logger.change_status(
            f"Made a play in {str(time.time() - play_start_time)[:4]}s",
        )

    logger.change_status("End of the 2v2 fight!")
    time.sleep(2.13)
    cards_played = logger.get_cards_played()
    logger.change_status(f"Played ~{cards_played - prev_cards_played} cards this fight")

    return "good"


def _1v1_fight_loop(emulator, logger: Logger, recording_flag: bool) -> bool:
    """Method for handling dynamicly timed 1v1 fight"""
    create_default_bridge_iar(emulator)
    collections.deque(maxlen=3)
    ingame_time = time.time()
    prev_cards_played = logger.get_cards_played()

    while check_for_in_battle_with_delay(emulator):
        if recording_flag:
            save_image(emulator.screenshot())
        global elapsed_time
        elapsed_time = time.time() - ingame_time
        if elapsed_time < 7:  # Less than 5 seconds
            percentage = percentage_first_5
            WAIT_THRESHOLD = 6000  # noqa: N806
            PLAY_THRESHOLD = 9000  # noqa: N806
        elif elapsed_time < 90:  # Less than 2 minutes
            percentage = percentage_single
            WAIT_THRESHOLD = 6000  # noqa: N806
            PLAY_THRESHOLD = 9000  # noqa: N806
        elif elapsed_time < 200:  # Less than 4 minutes
            percentage = percentage_double
            WAIT_THRESHOLD = 7000  # noqa: N806
            PLAY_THRESHOLD = 10000  # noqa: N806
        else:  # 4 minutes or more
            percentage = percentage_triple
            WAIT_THRESHOLD = 8000  # noqa: N806
            PLAY_THRESHOLD = 11000  # noqa: N806

        wait_output = wait_for_elixer(
            emulator,
            logger,
            random.choices(elixer_count, weights=percentage, k=1)[0],
            WAIT_THRESHOLD,
            PLAY_THRESHOLD,
            recording_flag
        )

        if wait_output == "restart":
            logger.change_status("Failure while waiting for elixer")
            return False

        if wait_output == "no battle":
            logger.change_status("Not in a 1v1 battle anymore!")
            break

        if not check_if_in_battle(emulator):
            "Not in a battle anymore"
            break

        # print("playing a card in 1v1...")
        if recording_flag:
            save_image(emulator.screenshot())

        play_start_time = time.time()
        if play_a_card(emulator, logger, recording_flag) is False:
            logger.change_status("Failed to play a card, retrying...")
        # play_time_taken = str(time.time() - play_start_time)[:4]
        logger.change_status(
            f"Made a play in {str(time.time() - play_start_time)[:4]}s",
        )

    logger.change_status("End of the 1v1 fight!")
    time.sleep(2.13)
    cards_played = logger.get_cards_played()
    logger.change_status(f"Played ~{cards_played - prev_cards_played} cards this fight")

    return True


def _1v1_random_fight_loop(emulator, logger) -> bool:
    """Method for handling dynamicly timed 1v1 fight"""
    logger.change_status(status="Starting 1v1 battle with random plays")
    fight_timeout = 5 * 60  # 5 minutes
    start_time = time.time()

    # while in battle:
    while check_if_in_battle(emulator):
        if time.time() - start_time > fight_timeout:
            logger.change_status("1v1_random_fight_loop() timed out. Breaking")
            return False

        mag_dump(emulator, logger)
        for _ in range(random.randint(1, 3)):
            logger.add_card_played()

        time.sleep(8)

    logger.change_status("Finished with 1v1 battle with random plays...")
    return True


if __name__ == "__main__":
    pass
