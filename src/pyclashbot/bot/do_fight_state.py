"""random module for randomizing fight plays"""

import numpy
import random
import time
from typing import Literal


from xmlrpc.client import Boolean
from pyclashbot.bot.account_switching import check_for_switch_ssid_page

from pyclashbot.bot.card_detection3 import get_play_coords_for_card,check_which_cards_are_available
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
    region_is_color,
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

LEAVE_1V1_BATTLE_OK_BUTTON: tuple[Literal[210], Literal[554]] = (210, 554)
CLOSE_BATTLE_LOG_BUTTON: tuple[Literal[365], Literal[72]] = (365, 72)
# coords of the cards in the hand
HAND_CARDS_COORDS = [
    (142, 561),
    (210, 563),
    (272, 561),
    (341, 563),
]
CLOSE_THIS_CHALLENGE_PAGE_BUTTON = (27, 22)
_2V2_BATTLE_ICON_COORD = (327, 483)  # coord of the button on the challenges tab
_2V2_BATTLE_BUTTON_COORD_2 = (
    209,
    433,
)  # coord of the battle button after you click the 2v2 battle icon

QUICKMATCH_BUTTON_COORD = (
    274,
    353,
)  # coord of the quickmatch button after you click the battle button
POST_FIGHT_TIMEOUT = 40  # seconds
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
    if (
        not random_fight_mode
        and _2v2_fight_loop(vm_index=vm_index, logger=logger) == "restart"
    ):
        logger.log("Error 698245 Failuring in 2v2 regular fight loop")
        return "restart"

    # if random fight mode, run the random fight loop
    if (
        random_fight_mode
        and _2v2_random_fight_loop(vm_index=vm_index, logger=logger) == "restart"
    ):
        logger.log("Error 655 Failuring in 2v2 random fight loop")
        return "restart"

    logger.add_2v2_fight()

    time.sleep(10)

    return next_state


def do_1v1_fight_state(vm_index, logger: Logger, next_state, random_fight_mode):
    """method to handle the entirety of the 1v1 battle state (start fight, do fight, end fight)"""

    logger.change_status(status="do_1v1_fight_state state")
    logger.change_status(status="waiting for 1v1 battle start")

    print(f"random_fight_mode is {random_fight_mode} in do_1v1_fight_state()")

    # wait for battle start
    if wait_for_1v1_battle_start(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 856585736 wait_for_1v1_battle_start() in do_1v1_fight_state()"
        )
        return "restart"

    logger.change_status(status="Battle started!")

    logger.change_status(status="Starting fight loop")

    # run regular fight loop if random mode not toggles
    if not random_fight_mode and _1v1_fight_loop(vm_index, logger) == "restart":
        logger.log("Error 884458245 Failuring in fight loop")
        return "restart"

    # run random fight loop if random mode toggled
    if random_fight_mode and _1v1_random_fight_loop(vm_index, logger) == "restart":
        logger.log("Error 35236 Failuring in fight loop")
        return "restart"

    logger.add_1v1_fight()

    time.sleep(10)
    return next_state


def start_2v2_fight_state(vm_index, logger: Logger) -> Literal["restart", "2v2_fight"]:
    """method to handle starting a 2v2 fight"""

    logger.change_status(status="Start fight state")
    logger.change_status(status="Starting 2v2 mode")

    next_state = "2v2_fight"

    # clash_main_check = check_if_on_clash_main_menu(vm_index)
    # if clash_main_check is not True:
    #     logger.change_status(status="ERROR 34 Not on main for start of start 2v2")
    #     logger.log("These are the pixels the bot saw after failing to find clash main:")
    #     for pixel in clash_main_check:
    #         logger.log(f"   {pixel}")

    #     return "restart"

    # get to challenges tab
    if get_to_challenges_tab_from_main(vm_index, logger) == "restart":
        return "restart"

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
        logger.change_status("Locked events page! Doing 1v1 instead...")
        click(vm_index, 170, 589)
        time.sleep(3)
        if check_if_on_clash_main_menu(vm_index) is not True:
            logger.change_status(
                "Failed to get from events tab to clash main after locked events page"
            )
            return "restart"
        return start_1v1_fight_state(vm_index, logger)

    # click 2v2 icon location
    click_2v2_icon_button(vm_index)
    time.sleep(1)

    # click battle button
    click_2v2_battle_button(vm_index)
    time.sleep(1)

    # click quickmatch button
    click_quickmatch_button(vm_index)
    time.sleep(1)

    return next_state


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


def start_1v1_fight_state(vm_index, logger: Logger) -> Literal["restart", "1v1_fight"]:
    """method to handle starting a 1v1 fight"""

    logger.change_status(status="Start fight state")
    logger.change_status(status="Starting 1v1 mode")

    next_state = "1v1_fight"

    # if not on clash main, return restart
    clash_main_check = check_if_on_clash_main_menu(vm_index)
    if clash_main_check is not True:
        logger.change_status(
            status="ERROR 46246 Not on main menu for start of start 1v1 fight"
        )
        logger.log("These are the pixels the bot saw after failing to find clash main:")
        for pixel in clash_main_check:
            logger.log(f"   {pixel}")

        return "restart"

    # click 1v1 button
    click(vm_index, 207, 400)

    return next_state


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


def wait_for_4_elixer(vm_index, logger, mode="1v1"):
    """method to wait for 4 elixer during a battle"""

    start_time = time.time()

    while 1:
        logger.change_status(
            f"Waiting for 4 elixer for {str(time.time() - start_time)[:4]}s..."
        )

        print('checking which cards are availabe...')
        if len(check_which_cards_are_available(vm_index)) == 4:
            logger.change_status('All cards are available!')
            return True

        if check_for_4_elixer(vm_index):
            break

        if check_if_at_max_elixer(vm_index):
            return "mag_dump"

        if time.time() - start_time > ELIXER_WAIT_TIMEOUT:
            return "restart"

        if mode == "1v1" and not check_for_in_battle_with_delay(vm_index):
            logger.change_status(status="Not in battle, stopping waiting for 4 elixer.")
            return "no battle"
        if mode == "2v2" and not check_for_in_battle_with_delay(vm_index):
            logger.change_status(status="Not in battle, stopping waiting for 4 elixer.")
            return "no battle"

    logger.change_status(f"Took {str(time.time() - start_time)[:4]}s for 4 elixer.")

    return True


def check_for_4_elixer(vm_index) -> bool:
    """method to check for 4 elixer during a battle"""



    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[619][205],
        iar[619][225],
    ]
    for p in pixels:
        if not pixel_is_equal(p, [203, 31, 209], tol=45):
            return False
    return True


def check_for_6_elixer(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[613][255],
        iar[613][270],
    ]
    colors = [[244, 137, 240], [244, 137, 240]]

    for index, pixel in enumerate(pixels):
        color = colors[index]
        if not pixel_is_equal(pixel, color, tol=35):
            return False
    return True


def wait_for_6_elixer(
    vm_index, logger: Logger
) -> Literal["restart", "no battle", "good"]:
    """method to wait for 6 elixer during a battle"""

    start_time = time.time()
    while not check_for_6_elixer(vm_index):
        if time.time() - start_time > ELIXER_WAIT_TIMEOUT:
            return "restart"

        if not check_for_in_battle_with_delay(vm_index):
            logger.change_status(status="Not in battle, stopping waiting for 6 elixer")
            return "no battle"

    return "good"


def check_enemy_tower_statuses(
    vm_index,
) -> tuple[Literal["alive", "destroyed"], Literal["alive", "destroyed"]]:
    """method to scan pixels during a battle to determine
    which of  the enemy towers are alive or destroyed"""

    #'alive'
    # or
    #'destroyed'

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

    # if not on main, return restart
    clash_main_check = check_if_on_clash_main_menu(vm_index)
    if clash_main_check is not True:
        logger.change_status(status='54676 Error Not on main menu, returning "restart"')
        logger.log("These are the pixels the bot saw after failing to find clash main:")
        for pixel in clash_main_check:
            logger.log(f"   {pixel}")

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
[255 ,187, 104],
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
        print('Used find_ok_battle_button2 patch-job')
        return (200,550)

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

    while time.time() - start_time < timeout:
        print("Checking if on clash main after a fight...")

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

        print("Not on Clash Main\nChecking for moves to make to get to clash main...")

        # check for trophy reward screen
        if check_for_trophy_reward_menu(vm_index):
            print("Found trophy reward menu!\nHandling Trophy Reward Menu")
            handle_trophy_reward_menu(vm_index, logger, printmode=False)
            time.sleep(3)
            continue
        else:
            print("Not on trophy reward page")

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
        else:
            # print("Already clicked OK or EXIT so not checking for those buttons again")
            pass

        # if on events page, click clash main button
        if check_for_events_page(vm_index):
            print("Found events page, clicking clash main button.")
            click(vm_index, 179, 600)
            time.sleep(3)
            continue
        else:
            print("Not on events page...")

        time.sleep(1)

    return False



# main fight loops


def _2v2_fight_loop(vm_index, logger: Logger) -> Literal["restart", "good"]:
    """method to handle a dynamicly timed 2v2 fight"""

    logger.change_status(status="Starting 2v2 battle loop")

    # count plays
    plays = 0

    prev_cards_played = logger.get_cards_played()

    # while in battle:
    while check_for_in_battle_with_delay(vm_index):
        # if check_if_at_max_elixer(vm_index):
        #     logger.change_status("At max elixer so just mag dumping!!!")
        #     mag_dump(vm_index, logger)

        # emote sometimes to do daily challenge (jk its to be funny)
        if random.randint(0, 10) == 1:
            emote_in_2v2(vm_index, logger)

        logger.log(f"2v2 battle play #{plays}:")

        # wait for 4 elixer
        if not check_for_4_elixer(vm_index):
            logger.log("Waiting for 4 elixer")

            elixer_wait_return: Literal["restart", "no battle", "good"] = (
                wait_for_4_elixer(vm_index, logger)
            )

            if elixer_wait_return == "restart":
                logger.change_status(
                    status="Error 99765684 wait_for_4_elixer() in fight_loop()"
                )
                return "restart"

            if elixer_wait_return == "no battle":
                logger.log(
                    "No battle detected in elixer_wait_return var in _2v2_fight_loop()"
                )
                break

        this_play_start_time = time.time()


        # choose play coord but favor a side according to favorite_side var
        play_choice_start_time = time.time()
        this_play_side = choose_play_side(logger, vm_index)
        logger.change_status(
            f"Choose a play side in {str(time.time() - play_choice_start_time)[:4]}s"
        )
        card_indicies = check_which_cards_are_available(vm_index)
        if card_indicies == []:
            logger.change_status("No cards are avilable.. waiting...")
            continue

        logger.change_status(f'These cards are available: {card_indicies}')

        card_index = random.choice(card_indicies)
        logger.change_status(f'Choosing this card index: {card_index}')

        # get a coord based on the selected side
        play_coords_start_time = time.time()
        card_id, play_coord = get_play_coords_for_card(
            vm_index, card_index, this_play_side
        )
        logger.change_status(
            f"Choose a play coord in {str(time.time() - play_coords_start_time)[:4]}s"
        )

        # if coord is none for whatever reason, just skip this play
        if play_coord is None:
            logger.change_status("Bad play coord. Redoing...")
            continue

        id_string = "Regular card"
        if card_id != "Unknown":
            id_string = card_id
        logger.change_status(
            status=f"Playing card: {id_string} on {this_play_side} side"
        )

        # click that random card coord
        random_card_coord = HAND_CARDS_COORDS[card_index]
        click(vm_index, random_card_coord[0], random_card_coord[1])
        time.sleep(0.1)

        # click that play coord
        click(vm_index, play_coord[0], play_coord[1])
        logger.add_card_played()
        time.sleep(1.5)

        # increment plays counter
        plays += 1

        logger.change_status(
            f"Played {id_string} on {this_play_side} side in {str(time.time() - this_play_start_time)[:4]}s"
        )

    cards_played = logger.get_cards_played()
    logger.change_status(f"Played ~{cards_played - prev_cards_played} cards this fight")

    return "good"


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
    prev_card_index = None
    while check_if_in_battle(vm_index):
        logger.log(f"Battle play #{plays}:")

        # wait for 6 elixer
        logger.log("Waiting for 6 elixer")

        _6_elixer_wait_start_time = time.time()
        elixer_wait_return = wait_for_4_elixer(vm_index, logger)
        logger.change_status(
            f"Waited {str(time.time() - _6_elixer_wait_start_time)[:5]}s for 6 elixer"
        )

        if elixer_wait_return == "restart":
            logger.change_status(
                status="Error 788455 wait_for_6_elixer() in fight_loop()"
            )
            return "restart"

        if elixer_wait_return == "no battle":
            break

        # choose random card idnex to play
        random_card_index = random.randint(0, 3)
        while 1:
            if prev_card_index is None:
                break
            random_card_index = random.randint(0, 3)
            if random_card_index != prev_card_index:
                break

        # update prev card index for next play's choice
        prev_card_index = random_card_index

        logger.log(f"Using card index {random_card_index}")

        # choose play coord but favor a side according to favorite_side var
        choose_play_side_start_time = time.time()
        this_play_side = choose_play_side_barebones(vm_index, favorite_side)
        # this_play_side = choose_play_side(vm_index, favorite_side)
        logger.change_status(
            f"Waited {str(time.time() - choose_play_side_start_time)[:5]}s to choose a side"
        )

        # get a coord based on the selected side
        choose_play_coords_start_time = time.time()
        identification, play_coord = get_play_coords_for_card(
            vm_index, random_card_index, this_play_side
        )
        logger.change_status(
            f"Waited {str(time.time() - choose_play_coords_start_time)[:5]}s to calculate a coord"
        )

        # if coord is none for whatever reason, just skip this play
        if play_coord is None:
            logger.change_status("Bad play coord. Redoing...")
            continue

        id_string = "Regular card"
        if identification != "Unknown":
            id_string = identification
        logger.change_status(
            status=f"Playing card: {id_string} on {this_play_side} side..."
        )

        # click that random card coord
        random_card_coord = HAND_CARDS_COORDS[random_card_index]
        click(vm_index, random_card_coord[0], random_card_coord[1])
        time.sleep(0.1)

        # click that play coord
        click(vm_index, play_coord[0], play_coord[1])
        logger.add_card_played()
        time.sleep(1.5)

        logger.change_status(
            status=f"Played card: {id_string} on {this_play_side} side"
        )

        # increment plays counter
        plays += 1
        time.sleep(0.33)

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
