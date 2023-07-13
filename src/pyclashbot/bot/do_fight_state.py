import random
import time
from typing import Literal

from pyclashbot.bot.card_detection import get_play_coords_for_card
from pyclashbot.bot.nav import (
    check_for_end_2v2_battle_screen,
    check_for_in_1v1_battle,
    check_for_in_2v2_battle,
    check_if_on_clash_main_menu,
    get_to_activity_log,
    get_to_challenges_tab_from_main,
    get_to_main_from_challenges_tab,
    wait_for_1v1_battle_start,
    wait_for_2v2_battle_start,
    wait_for_clash_main_challenges_tab,
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
CLASH_MAIN_ICON_FROM_CHALLENGES_TAB: tuple[Literal[170], Literal[590]] = (170, 590)
END_1V1_BATTLE_OK_BUTTON_COORD = (211, 553)
END_2V2_BATTLE_EXIT_BUTTON_COORD = (82, 596)


LEAVE_1V1_BATTLE_CONDITION_1_EXIT_BUTTON: tuple[Literal[71], Literal[600]] = (71, 600)


def end_fight_state(vm_index: int, logger: Logger, next_state: str) -> str:
    logger.change_status("End fight state")
    wait_return: Literal["restart", "good", "2v2", "1v1"] = wait_for_end_battle_screen(
        vm_index, logger
    )

    if wait_return == "restart":
        logger.log("Error 5987235 Failure with waitign for end battle screen")
        return "restart"

    if wait_return == "1v1":
        if leave_1v1_battle(vm_index, logger) == "restart":
            logger.log("Error 928579823 Failure leaving 1v1 match.")
            return "restart"

    if wait_return == "2v2":
        if leave_2v2_battle(vm_index, logger) == "restart":
            logger.log("Error 777533 Failure leaving 2v2 match.")
            return "restart"

    time.sleep(3)

    game_was_win_return: bool | Literal['restart'] = check_if_previous_game_was_win(vm_index, logger)
    if game_was_win_return == "restart":
        logger.change_status(
            status="Error 115 Failure with check_if_previous_game_was_win() in end_fight_state()"
        )
        return "restart"

    if game_was_win_return:
        logger.change_status(status="Last game was a win")
        logger.add_win()
    else:
        logger.change_status(status="Last game was a loss")
        logger.add_loss()

    time.sleep(3)

    return next_state


def leave_1v1_battle(vm_index, logger) -> Literal["restart", "good"]:
    click(
        vm_index, END_1V1_BATTLE_OK_BUTTON_COORD[0], END_1V1_BATTLE_OK_BUTTON_COORD[1]
    )
    if wait_for_clash_main_menu(vm_index, logger) == "restart":
        logger.log(
            "error 587325 Failure waiting for clash main after leaving 1v1 battle"
        )
        return "restart"

    return "good"


def leave_2v2_battle(vm_index, logger):
    click(
        vm_index,
        END_2V2_BATTLE_EXIT_BUTTON_COORD[0],
        END_2V2_BATTLE_EXIT_BUTTON_COORD[1],
    )
    wait_for_clash_main_challenges_tab(vm_index, logger)

    if get_to_main_from_challenges_tab(vm_index, logger) == "restart":
        logger.change_status("Error 96872 Failed to get to clash main after 2v2 match")
        return "restart"

    return "good"


def check_for_challenges_page():
    pass


def do_1v1_fight_state(vm_index, logger: Logger) -> Literal["restart", "end_fight"]:
    next_state = "end_fight"

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

    logger.add_1v1_fight()
    return next_state


def do_2v2_fight_state(vm_index, logger: Logger) -> Literal["restart", "end_fight"]:
    next_state = "end_fight"

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

    logger.add_2v2_fight()
    return next_state


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


def wait_for_end_battle_screen(
    vm_index, logger
) -> Literal["restart", "good", "2v2", "1v1"]:
    logger.change_status("Waiting for end battle screen to appear")

    start_time = time.time()

    while 1:
        if check_for_end_battle_screen_2(vm_index) or check_for_end_battle_screen_1(
            vm_index
        ):
            return "2v2"

        if check_for_end_battle_screen_3(vm_index):
            return "1v1"

        time_taken = time.time() - start_time
        if time_taken > 60:
            logger.log("Error 666895 Failure waiting for end battle screen to appear")
            return "restart"
        time.sleep(3)

    logger.log("Done waiting for end battle screen to appear")

    return "good"


def check_for_end_battle_screen_3(vm_index):  # 1v1 end battle
    if not region_is_color(
        vm_index, [170, 555, 25, 15], (77, 174, 255)
    ):  # blue OK button
        return False
    if not region_is_color(
        vm_index, [175, 555, 15, 10], (73, 172, 255)
    ):  # blue OK button
        return False
    if not region_is_color(
        vm_index, [55, 515, 20, 5], (255, 255, 255)
    ):  # white emote button region
        return False
    return True


def check_for_end_battle_screen_2(vm_index):  # 2v2 end battle, teammate hasn't left
    if not check_line_for_color(
        vm_index, 50, 588, 50, 611, (76, 176, 255)
    ):  # blue exit button
        return False
    if not check_line_for_color(
        vm_index, 105, 589, 105, 609, (76, 172, 255)
    ):  # blue exit button
        return False
    if not check_line_for_color(
        vm_index, 59, 590, 96, 606, (255, 255, 255)
    ):  # blue exit button
        return False

    if not check_line_for_color(vm_index, 133, 589, 200, 589, (255, 200, 80)):
        return False

    if not region_is_color(vm_index, [309, 588, 10, 19], (76, 178, 255)):
        return False
    return True


def check_for_end_battle_screen_1(vm_index):  # 2v2 end battle, teammate has left
    if not check_line_for_color(
        vm_index, 50, 588, 50, 611, (76, 176, 255)
    ):  # blue exit button
        return False
    if not check_line_for_color(
        vm_index, 105, 589, 105, 609, (76, 172, 255)
    ):  # blue exit button
        return False
    if not check_line_for_color(
        vm_index, 59, 590, 96, 606, (255, 255, 255)
    ):  # blue exit button
        return False
    if not region_is_color(
        vm_index, [150, 590, 17, 2], (203, 203, 203)
    ):  # grey play again button
        return False
    if not check_line_for_color(
        vm_index, 391, 23, 405, 23, (232, 36, 36)
    ):  # close button
        return False
    return True


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


def check_for_exit_battle_button_condition_1(vm_index) -> bool:
    if not check_for_end_2v2_battle_screen(vm_index):
        return False

    if not region_is_color(vm_index, [44, 600, 11, 9], (76, 173, 255)):
        return False

    return True


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

    # while in battle:
    while check_for_in_2v2_battle(vm_index):
        logger.log(f"2v2 battle play #{plays}:")

        # wait for 6 elixer
        logger.log("Waiting for 6 elixer")

        elixer_wait_return = wait_for_6_elixer(vm_index, logger, "2v2")

        if elixer_wait_return == "restart":
            logger.change_status(
                status="Error 99765684 wait_for_6_elixer() in fight_loop()"
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
    logger.log("Done with fight loop")
    return "good"


def _1v1_fight_loop(vm_index, logger: Logger) -> Literal["restart", "good"]:
    logger.change_status(status="Starting battle loop")

    # choose a side to favor this fight
    favorite_side = random.choice(["left", "right"])

    logger.change_status(status=f"Going to favor {favorite_side} this fight...")

    # count plays
    plays = 0

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
    logger.log("Done with fight loop")
    return "good"


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


def wait_for_6_elixer(
    vm_index, logger: Logger, mode="1v1"
) -> Literal["restart", "no battle", "good"]:
    start_time = time.time()
    while region_is_color(vm_index, region=[254, 610, 19, 12], color=(4, 56, 125)):
        if time.time() - start_time > 25:
            return "restart"

        if mode == "1v1" and not check_for_in_1v1_battle(vm_index):
            logger.change_status(status="Not in battle, stopping waiting for 6 elixer")
            return "no battle"
        if mode == "2v2" and not check_for_in_2v2_battle(vm_index):
            logger.change_status(status="Not in battle, stopping waiting for 6 elixer")
            return "no battle"
    return "good"


def check_for_6_elixer_with_delay(vm_index) -> bool:
    start_time = time.time()
    while time.time() - start_time < 3:
        if check_for_6_elixer(vm_index):
            return True
        time.sleep(0.1)
    return False


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


if __name__ == "__main__":
    pass
