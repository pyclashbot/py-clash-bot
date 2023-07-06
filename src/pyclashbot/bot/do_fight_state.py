import random
import time

from pyclashbot.bot.card_detection import get_play_coords_for_card
from pyclashbot.bot.navigation import (
    check_for_in_1v1_battle,
    check_for_in_2v2_battle,
    check_if_on_clash_main_menu,
    get_to_activity_log,
    get_to_challenges_tab_from_main,
    wait_for_1v1_battle_start,
    wait_for_2v2_battle_start,
    wait_for_clash_main_menu,
    wait_for_end_1v1_battle_screen,
)
from pyclashbot.detection.image_rec import check_line_for_color, region_is_color
from pyclashbot.memu.client import click, screenshot, scroll_up
from pyclashbot.utils.logger import Logger

LEAVE_1V1_BATTLE_OK_BUTTON = (210, 554)
CLOSE_BATTLE_LOG_BUTTON = (365, 72)
# coords of the cards in the hand
HAND_CARDS_COORDS = [
    (142, 561),
    (210, 563),
    (272, 561),
    (341, 563),
]


def do_1v1_fight_state(vm_index, logger: Logger):
    NEXT_STATE = "end_fight"

    logger.change_status("do_1v1_fight_state state")
    logger.change_status("waiting for 1v1 battle start")

    # wait for battle start
    if wait_for_1v1_battle_start(vm_index, logger) == "restart":
        logger.change_status(
            "Error 856585736 wait_for_1v1_battle_start() in do_1v1_fight_state()"
        )
        return "restart"

    logger.change_status("Battle started!")

    logger.change_status("Starting fight loop")
    if _1v1_fight_loop(vm_index, logger) == "restart":
        logger.log("Error 884458245 Failuring in fight loop")
        return "restart"

    logger.add_1v1_fight()
    return NEXT_STATE


def do_2v2_fight_state(vm_index, logger: Logger):
    NEXT_STATE = "end_fight"

    logger.change_status("do_1v1_fight_state state")
    logger.change_status("waiting for 2v2 battle start")

    # wait for battle start
    if wait_for_2v2_battle_start(vm_index, logger) == "restart":
        logger.change_status(
            "Error 7567336 wait_for_1v1_battle_start() in do_1v1_fight_state()"
        )
        return "restart"

    logger.change_status("2v2 Battle started!")

    logger.change_status("Starting fight loop")
    if _2v2_fight_loop(vm_index, logger) == "restart":
        logger.log("Error 698245 Failuring in fight loop")
        return "restart"

    logger.add_2v2_fight()
    return NEXT_STATE


def check_for_challenge_page_on_events_tab(vm_index):
    if not check_line_for_color(vm_index, 14, 13, 42, 34, (255, 188, 40)):
        return False
    if not check_line_for_color(vm_index, 14, 13, 42, 34, (255, 255, 255)):
        return False
    if not region_is_color(vm_index, [380, 580, 30, 40], (76, 111, 146)):
        return False

    return True


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


def close_this_challenge_page(vm_index):
    click(
        vm_index,
        CLOSE_THIS_CHALLENGE_PAGE_BUTTON[0],
        CLOSE_THIS_CHALLENGE_PAGE_BUTTON[1],
    )


def click_2v2_icon_button(vm_index):
    click(vm_index, _2V2_BATTLE_ICON_COORD[0], _2V2_BATTLE_ICON_COORD[1])


def click_2v2_battle_button(vm_index):
    click(vm_index, _2V2_BATTLE_BUTTON_COORD_2[0], _2V2_BATTLE_BUTTON_COORD_2[1])


def click_quickmatch_button(vm_index):
    click(vm_index, QUICKMATCH_BUTTON_COORD[0], QUICKMATCH_BUTTON_COORD[1])


def start_2v2_fight_state(vm_index, logger: Logger):
    logger.change_status("Start fight state")
    logger.change_status("Starting 2v2 mode")

    next_state = "2v2_fight"

    # if not on clash main, return restart
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            f"ERROR 24537265435 Not on clash main menu, returning to start state"
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


def start_1v1_fight_state(vm_index, logger: Logger):
    logger.change_status("Start fight state")
    logger.change_status("Starting 1v1 mode")

    next_state = "1v1_fight"

    # if not on clash main, return restart
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            f"ERROR 24537265435 Not on clash main menu, returning to start state"
        )
        return "restart"

    # click 1v1 button
    click(vm_index, 207, 400)

    return next_state


def end_fight_state(vm_index: int, logger: Logger, NEXT_STATE: str):
    logger.change_status("end fight state")
    logger.change_status("Waiting for the leave battle screen to pop up ")
    if wait_for_end_1v1_battle_screen(vm_index, logger) == "restart":
        logger.change_status(
            "Error 98573429805 Waiting too long for end 1v1 battle in end fight state()"
        )
        return "restart"

    # click leave button OK button
    click(vm_index, LEAVE_1V1_BATTLE_OK_BUTTON[0], LEAVE_1V1_BATTLE_OK_BUTTON[1])

    if wait_for_clash_main_menu(vm_index, logger) == "restart":
        logger.change_status(
            f"Error 353216346 wait_for_clash_main_menu)() fail in end_fight_state()"
        )
        return "restart"

    game_was_win_return = check_if_previous_game_was_win(vm_index, logger)
    if game_was_win_return == "restart":
        logger.change_status(
            "Erropr 498573204985 Failure with check_if_previous_game_was_win() in end_fight_state()"
        )
        return "restart"

    if game_was_win_return:
        logger.change_status("Last game was a win")
        logger.add_win()
    else:
        logger.change_status("Last game was a loss")
        logger.add_loss()

    time.sleep(3)

    return NEXT_STATE


def choose_play_side(vm_index, favorite_side):
    # get tower_statuses
    tower_statuses = check_enemy_tower_statuses(vm_index)

    # if left is destroyed and right is alive, return right
    if tower_statuses[0] == "destroyed" and tower_statuses[1] == "alive":
        return "right"

    # else, if right is destroyed and left is alive, return left
    elif tower_statuses[1] == "destroyed" and tower_statuses[0] == "alive":
        return "left"

    # if neither are destroyed, return favorite_side
    choices = [favorite_side] * 7 + [
        side for side in ["left", "right"] if side != favorite_side
    ] * 3

    return random.choice(choices)


def _2v2_fight_loop(vm_index, logger: Logger):
    logger.change_status("Starting 2v2 battle loop")

    # choose a side to favor this fight
    favorite_side = random.choice(["left", "right"])

    logger.change_status(f"Going to favor {favorite_side} this fight...")

    # count plays
    plays = 0

    # while in battle:
    while check_for_in_2v2_battle(vm_index):
        logger.log(f"2v2 battle play #{plays}:")

        # wait for 6 elixer
        logger.log("Waiting for 6 elixer")

        elixer_wait_return = wait_for_6_elixer(vm_index, logger, "2v2")

        if elixer_wait_return == "restart":
            logger.change_status("Error 788455 wait_for_6_elixer() in fight_loop()")
            return "restart"

        elif elixer_wait_return == "no battle":
            break

        # choose random card to play
        random_card_index = random.randint(0, 3)
        logger.log(f"Clicking card index {random_card_index}")

        # choose play coord but favor a side according to favorite_side var
        this_play_side = choose_play_side(vm_index, favorite_side)

        # get a coord based on the selected side
        id, play_coord = get_play_coords_for_card(
            vm_index, random_card_index, this_play_side
        )

        # if coord is none for whatever reason, just skip this play
        if play_coord is None:
            continue

        id_string = "Regular card"
        if id != "Unknown":
            id_string = id
        logger.change_status(f"Playing card: {id_string} on {this_play_side} side")

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
    logger.log("Done with fight loop")


def _1v1_fight_loop(vm_index, logger: Logger):
    logger.change_status("Starting battle loop")

    # choose a side to favor this fight
    favorite_side = random.choice(["left", "right"])

    logger.change_status(f"Going to favor {favorite_side} this fight...")

    # count plays
    plays = 0

    # while in battle:
    while check_for_in_1v1_battle(vm_index):
        logger.log(f"Battle play #{plays}:")

        # wait for 6 elixer
        logger.log("Waiting for 6 elixer")

        elixer_wait_return = wait_for_6_elixer(vm_index, logger)

        if elixer_wait_return == "restart":
            logger.change_status("Error 788455 wait_for_6_elixer() in fight_loop()")
            return "restart"

        elif elixer_wait_return == "no battle":
            break

        # choose random card to play
        random_card_index = random.randint(0, 3)
        logger.log(f"Clicking card index {random_card_index}")

        # choose play coord but favor a side according to favorite_side var
        this_play_side = choose_play_side(vm_index, favorite_side)

        # get a coord based on the selected side
        id, play_coord = get_play_coords_for_card(
            vm_index, random_card_index, this_play_side
        )

        # if coord is none for whatever reason, just skip this play
        if play_coord is None:
            continue

        id_string = "Regular card"
        if id != "Unknown":
            id_string = id
        logger.change_status(f"Playing card: {id_string} on {this_play_side} side")

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
    logger.log("Done with fight loop")


def check_if_previous_game_was_win(vm_index, logger: Logger):
    logger.change_status("Checking if last game was a win/loss")

    # if not on main, return restart
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status('534594784234 Error Not on main menu, returning "restart"')
        return "restart"

    # get to clash main options menu
    if get_to_activity_log(vm_index, logger) == "restart":
        logger.change_status(
            "Error 8967203948 get_to_activity_log() in check_if_previous_game_was_win()"
        )

        return "restart"

    logger.change_status("Checking if last game was a win...")
    is_a_win = check_pixels_for_win_in_battle_log(vm_index)
    logger.change_status(f"Last game is win: {is_a_win}")

    # close battle log
    logger.change_status("Returning to clash main")
    click(vm_index, CLOSE_BATTLE_LOG_BUTTON[0], CLOSE_BATTLE_LOG_BUTTON[1])
    if wait_for_clash_main_menu(vm_index, logger) == "restart":
        logger.change_status(
            "Error 95867235 wait_for_clash_main_menu() in check_if_previous_game_was_win()"
        )
        return "restart"

    return is_a_win


def check_pixels_for_win_in_battle_log(vm_index):
    line1 = check_line_for_color(
        vm_index, x1=47, y1=135, x2=109, y2=154, color=(255, 51, 102)
    )
    line2 = check_line_for_color(
        vm_index, x1=46, y1=152, x2=115, y2=137, color=(255, 51, 102)
    )
    line3 = check_line_for_color(
        vm_index, x1=47, y1=144, x2=110, y2=147, color=(255, 51, 102)
    )

    if line1 and line2 and line3:
        return False
    return True


def wait_for_6_elixer(vm_index, logger: Logger, mode="1v1"):
    start_time = time.time()
    while region_is_color(vm_index, region=[254, 610, 19, 12], color=(4, 56, 125)):
        if time.time() - start_time > 15:
            return "restart"

        if mode == "1v1" and not check_for_in_1v1_battle(vm_index):
            logger.change_status("Not in battle, stopping waiting for 6 elixer")
            return "no battle"
        elif mode == "2v2" and not check_for_in_2v2_battle(vm_index):
            logger.change_status("Not in battle, stopping waiting for 6 elixer")
            return "no battle"


def check_for_6_elixer_with_delay(vm_index):
    start_time = time.time()
    while time.time() - start_time < 3:
        if check_for_6_elixer(vm_index):
            return True
        time.sleep(0.1)
    return False


def check_for_6_elixer(vm_index):
    line2 = check_line_for_color(
        vm_index, x1=253, y1=611, x2=273, y2=622, color=(207, 33, 213)
    )
    line3 = check_line_for_color(
        vm_index, x1=254, y1=622, x2=273, y2=612, color=(207, 33, 213)
    )

    if line2 and line3:
        return True
    return False


def check_enemy_tower_statuses(vm_index):
    left_tower_color = (232, 188, 43)
    right_tower_color = (232, 188, 42)

    left_tower_alive = check_line_for_color(
        vm_index, x1=89, y1=92, x2=101, y2=101, color=left_tower_color
    )
    right_tower_alive = check_line_for_color(
        vm_index, x1=276, y1=90, x2=289, y2=102, color=right_tower_color
    )

    left_status = "alive" if left_tower_alive else "destroyed"
    right_status = "alive" if right_tower_alive else "destroyed"

    return (left_status, right_status)


if __name__ == "__main__":
    pass
