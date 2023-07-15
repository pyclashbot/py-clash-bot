"""random module for randomizing fight plays"""
import random
import time
from typing import Literal

from pyclashbot.bot.card_detection import get_play_coords_for_card
from pyclashbot.bot.nav import (
    check_for_in_1v1_battle,
    check_for_in_2v2_battle,
    check_if_on_clash_main_challenges_tab,
    check_if_on_clash_main_menu,
    get_to_activity_log,
    get_to_challenges_tab_from_main,
    wait_for_1v1_battle_start,
    wait_for_2v2_battle_start,
    wait_for_clash_main_menu,
)
from pyclashbot.detection.image_rec import check_line_for_color, region_is_color
from pyclashbot.memu.client import click, scroll_up
from pyclashbot.utils.logger import Logger

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
POST_FIGHT_TIMEOUT = 120  # seconds
ELIXER_WAIT_TIMEOUT = 25


# pre-fight methods


def start_2v2_fight_state(vm_index, logger: Logger) -> Literal["restart", "2v2_fight"]:
    logger.change_status(status="Start fight state")
    logger.change_status(status="Starting 2v2 mode")

    next_state = "2v2_fight"

    # if not on clash main, return restart
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            status="ERROR 24537265435 Not on clash main menu, returning to start state"
        )
        return "restart"

    # get to challenges tab
    if get_to_challenges_tab_from_main(vm_index, logger) == "restart":
        return "restart"

    # check for then close popup
    if check_for_challenge_page_on_events_tab(vm_index):
        close_this_challenge_page(vm_index)
        time.sleep(1)

    # scroll up
    for _ in range(10):
        scroll_up(vm_index)
    time.sleep(1)

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


def start_1v1_fight_state(vm_index, logger: Logger) -> Literal["restart", "1v1_fight"]:
    logger.change_status(status="Start fight state")
    logger.change_status(status="Starting 1v1 mode")

    next_state = "1v1_fight"

    # if not on clash main, return restart
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            status="ERROR 77357352 Not on clash main menu, returning to start state"
        )
        return "restart"

    # click 1v1 button
    click(vm_index, 207, 400)

    return next_state


def check_for_challenge_page_on_events_tab(vm_index):
    if not check_line_for_color(vm_index, 14, 13, 42, 34, (255, 188, 40)):
        return False
    if not check_line_for_color(vm_index, 14, 13, 42, 34, (255, 255, 255)):
        return False
    if not region_is_color(vm_index, [380, 580, 30, 40], (76, 111, 146)):
        return False

    return True


def close_this_challenge_page(vm_index) -> None:
    click(
        vm_index,
        CLOSE_THIS_CHALLENGE_PAGE_BUTTON[0],
        CLOSE_THIS_CHALLENGE_PAGE_BUTTON[1],
    )


def click_2v2_icon_button(vm_index) -> None:
    click(vm_index, _2V2_BATTLE_ICON_COORD[0], _2V2_BATTLE_ICON_COORD[1])


def click_2v2_battle_button(vm_index) -> None:
    click(vm_index, _2V2_BATTLE_BUTTON_COORD_2[0], _2V2_BATTLE_BUTTON_COORD_2[1])


def click_quickmatch_button(vm_index) -> None:
    click(vm_index, QUICKMATCH_BUTTON_COORD[0], QUICKMATCH_BUTTON_COORD[1])


# fight loop methods


def do_1v1_fight_state(vm_index, logger: Logger, next_state):
    logger.change_status(status="do_1v1_fight_state state")
    logger.change_status(status="waiting for 1v1 battle start")

    # wait for battle start
    if wait_for_1v1_battle_start(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 856585736 wait_for_1v1_battle_start() in do_1v1_fight_state()"
        )
        return "restart"

    logger.change_status(status="Battle started!")

    logger.change_status(status="Starting fight loop")
    if _1v1_fight_loop(vm_index, logger) == "restart":
        logger.log("Error 884458245 Failuring in fight loop")
        return "restart"

    prev_1v1_fight_count = logger.get_1v1_fights()
    logger.add_1v1_fight()
    _1v1_fight_count = logger.get_1v1_fights()
    logger.log(
        f"Increment 1v1 fight count from {prev_1v1_fight_count} to {_1v1_fight_count}"
    )

    return next_state


def do_2v2_fight_state(vm_index, logger: Logger, next_state):
    logger.change_status(status="do_1v1_fight_state state")
    logger.change_status(status="waiting for 2v2 battle start")

    # wait for battle start
    if wait_for_2v2_battle_start(vm_index=vm_index, logger=logger) == "restart":
        logger.change_status(
            status="Error 7567336 wait_for_1v1_battle_start() in do_1v1_fight_state()"
        )
        return "restart"

    logger.change_status(status="2v2 Battle started!")

    logger.change_status(status="Starting fight loop")
    if _2v2_fight_loop(vm_index=vm_index, logger=logger) == "restart":
        logger.log("Error 698245 Failuring in fight loop")
        return "restart"

    prev_2v2_fight_count = logger.get_2v2_fights()
    logger.add_2v2_fight()
    _2v2_fight_count = logger.get_2v2_fights()
    logger.log(
        f"Increment 2v2 fight count from {prev_2v2_fight_count} to {_2v2_fight_count}"
    )

    return next_state


def choose_play_side(vm_index, favorite_side):
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


def _2v2_fight_loop(vm_index, logger: Logger) -> Literal["restart", "good"]:
    logger.change_status(status="Starting 2v2 battle loop")

    # choose a side to favor this fight
    favorite_side = random.choice(["left", "right"])

    logger.change_status(status=f"Going to favor {favorite_side} this fight...")

    # count plays
    plays = 0

    prev_cards_played = logger.get_cards_played()

    # while in battle:
    while check_for_in_2v2_battle(vm_index):
        logger.log(f"2v2 battle play #{plays}:")

        # wait for 6 elixer
        logger.log("Waiting for 4 elixer")

        elixer_wait_return: Literal["restart", "no battle", "good"] = wait_for_4_elixer(
            vm_index, logger, mode="2v2"
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

        # choose random card to play
        random_card_index = random.randint(0, 3)
        logger.log(f"Clicking card index {random_card_index}")

        # choose play coord but favor a side according to favorite_side var
        this_play_side = choose_play_side(vm_index, favorite_side)

        # get a coord based on the selected side
        card_id, play_coord = get_play_coords_for_card(
            vm_index, random_card_index, this_play_side
        )

        # if coord is none for whatever reason, just skip this play
        if play_coord is None:
            continue

        id_string = "Regular card"
        if card_id != "Unknown":
            id_string = card_id
        logger.change_status(
            status=f"Playing card: {id_string} on {this_play_side} side"
        )

        # click that random card coord
        random_card_coord = HAND_CARDS_COORDS[random_card_index]
        click(vm_index, random_card_coord[0], random_card_coord[1])
        time.sleep(0.1)

        # click that play coord
        click(vm_index, play_coord[0], play_coord[1])
        logger.add_card_played()
        time.sleep(0.1)

        # increment plays counter
        plays += 1

    logger.remove_card_played(cards_to_remove=random.randint(2, 3))
    cards_played = logger.get_cards_played()
    logger.change_status(f"Played ~{cards_played - prev_cards_played} cards this fight")

    return "good"


def _1v1_fight_loop(vm_index, logger: Logger) -> Literal["restart", "good"]:
    logger.change_status(status="Starting battle loop")

    # choose a side to favor this fight
    favorite_side = random.choice(["left", "right"])

    logger.change_status(status=f"Going to favor {favorite_side} this fight...")

    # count plays
    plays = 0
    prev_cards_played = logger.get_cards_played()

    # while in battle:
    while check_for_in_1v1_battle(vm_index):
        logger.log(f"Battle play #{plays}:")

        # wait for 6 elixer
        logger.log("Waiting for 6 elixer")

        elixer_wait_return = wait_for_6_elixer(vm_index, logger)

        if elixer_wait_return == "restart":
            logger.change_status(
                status="Error 788455 wait_for_6_elixer() in fight_loop()"
            )
            return "restart"

        if elixer_wait_return == "no battle":
            break

        # choose random card to play
        random_card_index = random.randint(0, 3)
        logger.log(f"Clicking card index {random_card_index}")

        # choose play coord but favor a side according to favorite_side var
        this_play_side = choose_play_side(vm_index, favorite_side)

        # get a coord based on the selected side
        identification, play_coord = get_play_coords_for_card(
            vm_index, random_card_index, this_play_side
        )

        # if coord is none for whatever reason, just skip this play
        if play_coord is None:
            continue

        id_string = "Regular card"
        if identification != "Unknown":
            id_string = identification
        logger.change_status(
            status=f"Playing card: {id_string} on {this_play_side} side"
        )

        # click that random card coord
        random_card_coord = HAND_CARDS_COORDS[random_card_index]
        click(vm_index, random_card_coord[0], random_card_coord[1])
        time.sleep(0.1)

        # click that play coord
        click(vm_index, play_coord[0], play_coord[1])
        logger.add_card_played()
        time.sleep(0.1)

        # increment plays counter
        plays += 1

    logger.remove_card_played(cards_to_remove=random.randint(2, 3))
    cards_played = logger.get_cards_played()
    logger.change_status(f"Played ~{cards_played - prev_cards_played} cards this fight")
    return "good"


def wait_for_4_elixer(vm_index, logger, mode="1v1"):
    start_time = time.time()
    while not check_for_4_elixer(vm_index):
        if time.time() - start_time > ELIXER_WAIT_TIMEOUT:
            return "restart"

        if mode == "1v1" and not check_for_in_1v1_battle(vm_index):
            logger.change_status(status="Not in battle, stopping waiting for 4 elixer")
            return "no battle"
        if mode == "2v2" and not check_for_in_2v2_battle(vm_index):
            logger.change_status(status="Not in battle, stopping waiting for 4 elixer")
            return "no battle"
    return "good"


def check_for_4_elixer(vm_index):
    if not region_is_color(vm_index, [207, 612, 15, 2], (240, 137, 244)):
        return False
    if not region_is_color(vm_index, [205, 618, 17, 2], (207, 33, 213)):
        return False
    return True


def wait_for_6_elixer(
    vm_index, logger: Logger, mode="1v1"
) -> Literal["restart", "no battle", "good"]:
    start_time = time.time()
    while region_is_color(vm_index, region=[254, 610, 19, 12], color=(4, 56, 125)):
        if time.time() - start_time > ELIXER_WAIT_TIMEOUT:
            return "restart"

        if mode == "1v1" and not check_for_in_1v1_battle(vm_index):
            logger.change_status(status="Not in battle, stopping waiting for 6 elixer")
            return "no battle"
        if mode == "2v2" and not check_for_in_2v2_battle(vm_index):
            logger.change_status(status="Not in battle, stopping waiting for 6 elixer")
            return "no battle"
    return "good"


def check_for_6_elixer(vm_index) -> bool:
    line2 = check_line_for_color(
        vm_index, x_1=253, y_1=611, x_2=273, y_2=622, color=(207, 33, 213)
    )
    line3 = check_line_for_color(
        vm_index, x_1=254, y_1=622, x_2=273, y_2=612, color=(207, 33, 213)
    )

    if line2 and line3:
        return True
    return False


def check_enemy_tower_statuses(
    vm_index,
) -> tuple[Literal["alive", "destroyed"], Literal["alive", "destroyed"]]:
    left_tower_color = (232, 188, 43)
    right_tower_color = (232, 188, 42)

    left_tower_alive = check_line_for_color(
        vm_index, x_1=89, y_1=92, x_2=101, y_2=101, color=left_tower_color
    )
    right_tower_alive = check_line_for_color(
        vm_index, x_1=276, y_1=90, x_2=289, y_2=102, color=right_tower_color
    )

    left_status = "alive" if left_tower_alive else "destroyed"
    right_status = "alive" if right_tower_alive else "destroyed"

    return (left_status, right_status)


# post fight methods


def end_fight_state(vm_index, logger: Logger, next_state):
    # get to clash main after this fight
    if get_to_main_after_fight(vm_index, logger, next_state) == "restart":
        logger.log("Erro 6969 Failed to get to clash main after a fight")
        return "restart"

    # check if the prev game was a win

    win_check_return = check_if_previous_game_was_win(vm_index, logger)

    if win_check_return == "restart":
        logger.log("Error 885869 Failed while checking if previous game was a win")
        return "restart"

    if win_check_return:
        logger.add_win()
        return next_state

    logger.add_loss()
    return next_state


def check_if_previous_game_was_win(
    vm_index, logger: Logger
) -> bool | Literal["restart"]:
    logger.change_status(status="Checking if last game was a win/loss")

    # if not on main, return restart
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            status='534594784234 Error Not on main menu, returning "restart"'
        )
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
    if wait_for_clash_main_menu(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 95867235 wait_for_clash_main_menu() in check_if_previous_game_was_win()"
        )
        return "restart"

    return is_a_win


def check_pixels_for_win_in_battle_log(vm_index) -> bool:
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


def get_to_main_after_fight(vm_index, logger, next_state):
    start_time = time.time()

    while 1:
        if time.time() - start_time > POST_FIGHT_TIMEOUT:
            logger.log("took too long to get to clash main after a fight")
            return "restart"

        # if on end of 2v2 battle screen, click EXIT
        handle_end_2v2_battle_condition_1(vm_index, logger)

        # if on end of 2v2 battle screen c2, click OK
        handle_end_2v2_battle_condition_2(vm_index, logger)

        # if on end of 1v1 battle screen, click OK
        handle_end_1v1_battle_condition_1(vm_index, logger)
        handle_end_1v1_battle_condition_2(vm_index, logger)

        # if on challenges tab, click clash main tab
        if check_if_on_clash_main_challenges_tab(vm_index):
            logger.log("On challenges tab so clicking clash main icon")
            click(vm_index, 173, 591)

        # if on main, we're done
        if check_if_on_clash_main_menu(vm_index):
            logger.log("Made it to clash main after a fight")
            break

    return next_state


# unsorted


def handle_end_2v2_battle_condition_2(vm_index, logger):
    if check_for_end_2v2_battle_condition_2(vm_index):
        logger.log("On the end of 2v2 (c2) battle screen so clicking OK button")
        click(vm_index, 212, 553)


def check_for_end_2v2_battle_condition_2(vm_index):
    if not region_is_color(vm_index, [175, 558, 15, 8], (78, 175, 255)):
        return False
    if not region_is_color(vm_index, [225, 544, 17, 6], (99, 184, 255)):
        return False

    if not check_line_for_color(vm_index, 197, 545, 201, 550, (255, 255, 255)):
        return False
    if not check_line_for_color(vm_index, 210, 544, 201, 550, (255, 255, 255)):
        return False
    if not check_line_for_color(vm_index, 211, 544, 213, 554, (255, 255, 255)):
        return False
    if not check_line_for_color(vm_index, 225, 558, 215, 554, (255, 255, 255)):
        return False

    return True


def handle_end_2v2_battle_condition_1(vm_index, logger) -> None:
    if check_for_end_2v2_battle_condition_1(vm_index):
        logger.log("On the end of 2v2 (c1) battle screen so clicking exit button")
        click(vm_index, 81, 600)


def check_for_end_2v2_battle_condition_1(vm_index) -> bool:
    if not region_is_color(vm_index, [44, 602, 14, 8], (76, 174, 255)):
        return False
    if not region_is_color(vm_index, [100, 588, 8, 10], (104, 184, 255)):
        return False

    if not check_line_for_color(vm_index, 61, 590, 65, 601, (255, 255, 255)):
        return False
    if not check_line_for_color(vm_index, 74, 592, 76, 599, (255, 255, 255)):
        return False
    if not check_line_for_color(vm_index, 83, 590, 83, 599, (255, 255, 255)):
        return False
    if not check_line_for_color(vm_index, 90, 590, 91, 598, (255, 255, 255)):
        return False
    return True


def handle_end_1v1_battle_condition_1(vm_index, logger) -> None:
    if check_for_end_1v1_battle_condition_1(vm_index):
        logger.log("On the end of 1v1 (c1) battle screen to clicking OK button")
        click(vm_index, 211, 554)


def check_for_end_1v1_battle_condition_1(vm_index) -> bool:
    if not region_is_color(vm_index, [175, 556, 20, 6], (78, 175, 255)):
        return False
    if not region_is_color(vm_index, [225, 546, 242, 4], (101, 185, 255)):
        return False
    if not region_is_color(vm_index, [52, 514, 20, 8], (255, 255, 255)):
        return False
    return True


def handle_end_1v1_battle_condition_2(vm_index, logger) -> None:
    if check_for_end_1v1_battle_condition_2(vm_index):
        logger.log("On the end of 1v1 (c2) battle screen to clicking OK button")
        click(vm_index, 211, 552)


def check_for_end_1v1_battle_condition_2(vm_index) -> bool:
    if not region_is_color(vm_index, [175, 554, 20, 12], (78, 175, 255)):
        return False
    if not region_is_color(vm_index, [228, 545, 12, 6], (99, 184, 255)):
        return False

    if not check_line_for_color(vm_index, 197, 545, 201, 553, (255, 255, 255)):
        return False
    if not check_line_for_color(vm_index, 212, 544, 214, 553, (255, 255, 255)):
        return False
    return True
