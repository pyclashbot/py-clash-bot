"""random module for randomizing fight plays"""
from xmlrpc.client import Boolean
import numpy
import random
import time
from typing import Literal

from pyclashbot.bot.card_detection import get_play_coords_for_card
from pyclashbot.bot.nav import (
    check_if_in_battle,
    check_for_in_battle_with_delay,
    check_if_on_clash_main_challenges_tab,
    check_if_on_clash_main_menu,
    get_to_activity_log,
    get_to_challenges_tab_from_main,
    wait_for_1v1_battle_start,
    wait_for_2v2_battle_start,
    wait_for_clash_main_menu,
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


def start_2v2_fight_state(vm_index, logger: Logger) -> Literal["restart", "2v2_fight"]:
    """method to handle starting a 2v2 fight"""

    logger.change_status(status="Start fight state")
    logger.change_status(status="Starting 2v2 mode")

    next_state = "2v2_fight"

    clash_main_check = check_if_on_clash_main_menu(vm_index)
    if clash_main_check is not True:
        logger.change_status(status="ERROR 34 Not on main for start of start 2v2")
        logger.log("There are the pixels the bot saw after failing to find clash main:")
        for pixel in clash_main_check:
            logger.log(f"   {pixel}")

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
        scroll_up_on_left_side_of_screen(vm_index)
    time.sleep(1)

    # if there is a locked events page, return restart
    if check_for_locked_events_page(vm_index):
        logger.change_status("Locked events page! Doing 1v1 instead...")
        click(vm_index, 170, 589)
        time.sleep(3)
        if not check_if_on_clash_main_menu(vm_index):
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
        logger.log("There are the pixels the bot saw after failing to find clash main:")
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


def choose_play_side(vm_index, favorite_side):
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
    time.sleep(1)

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
    for index in range(8):
        print(f"mag dump play {index}")
        card_coord = random.choice(card_coords)
        play_coord = (random.randint(101, 440), random.randint(50, 526))

        click(vm_index, card_coord[0], card_coord[1])
        time.sleep(0.1)

        click(vm_index, play_coord[0], play_coord[1])
        time.sleep(0.1)


def _2v2_fight_loop(vm_index, logger: Logger) -> Literal["restart", "good"]:
    """method to handle a dynamicly timed 2v2 fight"""

    logger.change_status(status="Starting 2v2 battle loop")

    # choose a side to favor this fight
    favorite_side = random.choice(["left", "right"])

    logger.change_status(status=f"Going to favor {favorite_side} this fight...")

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

        # wait for 6 elixer
        if not check_for_4_elixer(vm_index):
            logger.log("Waiting for 4 elixer")

            elixer_wait_return: Literal[
                "restart", "no battle", "good"
            ] = wait_for_6_elixer(vm_index, logger)

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

            # if elixer_wait_return == "mag_dump":
            #     logger.change_status("At max elixer so just mag dumping!!!")
            #     mag_dump(vm_index, logger)

        this_play_start_time = time.time()

        # choose random card to play
        random_card_index = random.randint(0, 3)
        logger.change_status(f"Gonna play card index #{random_card_index}")

        # choose play coord but favor a side according to favorite_side var
        play_choice_start_time = time.time()
        this_play_side = choose_play_side(vm_index, favorite_side)
        logger.change_status(
            f"Choose a play side in {str(time.time() - play_choice_start_time)[:4]}s"
        )

        # get a coord based on the selected side
        play_coords_start_time = time.time()
        card_id, play_coord = get_play_coords_for_card(
            vm_index, random_card_index, this_play_side
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
        random_card_coord = HAND_CARDS_COORDS[random_card_index]
        click(vm_index, random_card_coord[0], random_card_coord[1])
        time.sleep(0.1)

        # click that play coord
        click(vm_index, play_coord[0], play_coord[1])
        logger.add_card_played()
        time.sleep(0.1)

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
    while check_if_in_battle(vm_index):
        logger.log(f"Battle play #{plays}:")

        # wait for 6 elixer
        logger.log("Waiting for 6 elixer")

        _6_elixer_wait_start_time = time.time()
        elixer_wait_return = wait_for_6_elixer(vm_index, logger)
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

        # choose random card to play
        random_card_index = random.randint(0, 3)
        logger.log(f"Clicking card index {random_card_index}")

        # choose play coord but favor a side according to favorite_side var
        choose_play_side_start_time = time.time()
        this_play_side = choose_play_side(vm_index, favorite_side)
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
        time.sleep(0.1)

        logger.change_status(
            status=f"Played card: {id_string} on {this_play_side} side"
        )

        # increment plays counter
        plays += 1
        time.sleep(0.33)

    cards_played = logger.get_cards_played()
    logger.change_status(f"Played ~{cards_played - prev_cards_played} ht")
    return "good"


def wait_for_4_elixer(vm_index, logger, mode="1v1"):
    """method to wait for 4 elixer during a battle"""

    start_time = time.time()

    while 1:
        logger.change_status(
            f"Waiting for 4 elixer for {str(time.time() - start_time)[:4]}s..."
        )

        if check_for_4_elixer(vm_index):
            break

        if check_if_at_max_elixer(vm_index):
            return "mag_dump"

        if time.time() - start_time > ELIXER_WAIT_TIMEOUT:
            return "restart"

        if mode == "1v1" and not check_if_in_battle(vm_index):
            logger.change_status(status="Not in battle, stopping waiting for 4 elixer.")
            return "no battle"
        if mode == "2v2" and not check_if_in_battle(vm_index):
            logger.change_status(status="Not in battle, stopping waiting for 4 elixer.")
            return "no battle"

    logger.change_status(f"Took {str(time.time() - start_time)[:4]}s for 4 elixer.")

    return True


def check_for_4_elixer(vm_index):
    """method to check for 4 elixer during a battle"""

    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[621][205],
        iar[620][224],
    ]
    for p in pixels:
        if not pixel_is_equal(p, [204, 31, 198], tol=45):
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


def count_enemy_crowns(vm_index):
    enemy_crown_coords = [
        (119, 121),
        (205, 109),
        (290, 117),
    ]
    iar = numpy.asarray(screenshot(vm_index))

    pixels = []
    for coord in enemy_crown_coords:
        pixels.append(iar[coord[1]][coord[0]])

    colors = [
        [37, 148, 255],
        [35, 141, 247],
        [52, 150, 249],
    ]

    crowns = 0

    for index, pixel in enumerate(pixels):
        color = colors[index]
        if pixel_is_equal(pixel, color, tol=35):
            crowns += 1

    return crowns


def count_friendly_crowns(vm_index):
    friendly_crown_coords = [
        (127, 300),
        (209, 294),
        (292, 301),
    ]
    iar = numpy.asarray(screenshot(vm_index))

    pixels = []
    for coord in friendly_crown_coords:
        pixels.append(iar[coord[1]][coord[0]])

    colors = [
        [77, 174, 254],
        [68, 163, 253],
        [73, 167, 254],
    ]

    crowns = 0

    for index, pixel in enumerate(pixels):
        color = colors[index]
        if pixel_is_equal(pixel, color, tol=35):
            crowns += 1

    return crowns


def check_for_2v2_chat_window(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[19][403],
        iar[12][396],
        iar[598][53],
        iar[19][320],
    ]
    colors = [
        [247, 239, 235],
        [255, 255, 255],
        [255, 186, 104],
        [255, 154, 51],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=35):
            return False

    return True


def close_2v2_chat_window(vm_index):
    click(vm_index, 399, 15)


def count_crowns(vm_index, logger: Logger):
    # close chat window if its 2v2
    if check_for_2v2_chat_window(vm_index):
        close_2v2_chat_window(vm_index)
        time.sleep(1)

    friendly_crowns = count_friendly_crowns(vm_index)

    enemy_crowns = count_enemy_crowns(vm_index)

    logger.add_count_to_enemy_crowns(enemy_crowns)
    logger.add_count_to_friendly_crowns(friendly_crowns)

    print("New crown count")
    print(f"friendly crowns: {friendly_crowns}")
    print(f"enemy crowns: {enemy_crowns}")

    return friendly_crowns, enemy_crowns


def end_fight_state(
    vm_index, logger: Logger, next_state, disable_win_tracker_toggle=True
):
    """method to handle the time after a fight and before the next state"""
    # count the crown score on this end-battle screen

    # get to clash main after this fight
    logger.log("Getting to clash main after doing a fight")
    if get_to_main_after_fight(vm_index, logger, next_state) == "restart":
        logger.log("Erro 6969 Failed to get to clash main after a fight")
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
        logger.change_status(
            status='534594784234 Error Not on main menu, returning "restart"'
        )
        logger.log("There are the pixels the bot saw after failing to find clash main:")
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
    if wait_for_clash_main_menu(vm_index, logger) == "restart":
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


def get_to_main_after_fight(vm_index, logger, next_state):
    """method to handle the navigation between the end of a fight and the main menu"""

    start_time = time.time()

    logger.log("Counting crowns")
    friendly_crowns, enemy_crowns = count_crowns(vm_index, logger)
    logger.log(f"Score last match was: {friendly_crowns}/{enemy_crowns}")

    while 1:
        logger.log("Getting back to main")

        if time.time() - start_time > POST_FIGHT_TIMEOUT:
            logger.log("took too long to get to clash main after a fight")
            return "restart"

        # if on main, we're done
        if check_if_on_clash_main_menu(vm_index) is True:
            logger.log("Made it to clash main after a fight")
            break

        # if on end of 2v2 battle screen, click EXIT
        if handle_end_2v2_battle_condition_1(vm_index, logger):
            time.sleep(1)
            continue

        # if on end of 2v2 battle screen c2, click OK
        if handle_end_2v2_battle_condition_2(vm_index, logger):
            time.sleep(1)
            continue

        # if on end of 2v2 battle screen c3, click OK
        if handle_end_2v2_battle_condition_3(logger, vm_index):
            time.sleep(1)
            continue

        # if on end of 1v1 battle screen c1, click OK
        if handle_end_1v1_battle_condition_1(vm_index, logger):
            time.sleep(1)
            continue

        # if on end of 1v1 battle screen c2, click OK
        if handle_end_1v1_battle_condition_2(vm_index, logger):
            time.sleep(1)
            continue

        # if on challenges tab, click clash main tab
        if check_if_on_clash_main_challenges_tab(vm_index):
            logger.log("On challenges tab so clicking clash main icon")
            click(vm_index, 173, 591)
            time.sleep(1)
            continue



    return next_state


def handle_end_2v2_battle_condition_2(vm_index, logger):
    """method to handle end of 2v2 battle screen condition 2"""

    if check_for_end_2v2_battle_condition_2(vm_index):
        logger.log("On the end of 2v2 (c2) battle screen so clicking OK button")
        click(vm_index, 212, 553)
        return True
    return False


def check_for_end_2v2_battle_condition_2(vm_index):
    """method to check if on second possible end of 2v2 battle screen"""

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


def handle_end_2v2_battle_condition_1(vm_index, logger):
    """method to handle end of 2v2 battle screen condition 1"""

    if check_for_end_2v2_battle_condition_1(vm_index):
        logger.log("On the end of 2v2 (c1) battle screen so clicking exit button")
        click(vm_index, 81, 600)
        return True
    return False


def check_for_end_2v2_battle_condition_1(vm_index) -> bool:
    """method to check if on first possible end of 2v2 battle screen"""

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


def handle_end_1v1_battle_condition_1(vm_index, logger):
    """method to handle the #1 possible end of 1v1 battle screen"""

    if check_for_end_1v1_battle_condition_1(vm_index):
        logger.log("On the end of 1v1 (c1) battle screen to clicking OK button")
        click(vm_index, 211, 554)
        return True
    return False


def check_for_end_1v1_battle_condition_1(vm_index) -> bool:
    """method to check if on the #1 possible end of 1v1 battle screen"""

    if not region_is_color(vm_index, [175, 556, 20, 6], (78, 175, 255)):
        return False
    if not region_is_color(vm_index, [225, 546, 242, 4], (101, 185, 255)):
        return False
    if not region_is_color(vm_index, [52, 514, 20, 8], (255, 255, 255)):
        return False
    return True


def handle_end_1v1_battle_condition_2(vm_index, logger) -> bool:
    """method to handle the #2 possible end of 1v1 battle screen"""
    if check_for_end_1v1_battle_condition_2(vm_index):
        logger.log("On the end of 1v1 (c2) battle screen to clicking OK button")
        click(vm_index, 211, 552)
        return True
    return False


def check_for_end_1v1_battle_condition_2(vm_index) -> bool:
    """method to check if the #2 possible end of 1v1 battle screen is on the screen"""

    if not region_is_color(vm_index, [175, 554, 20, 12], (78, 175, 255)):
        return False
    if not region_is_color(vm_index, [228, 545, 12, 6], (99, 184, 255)):
        return False

    if not check_line_for_color(vm_index, 197, 545, 201, 553, (255, 255, 255)):
        return False
    if not check_line_for_color(vm_index, 212, 544, 214, 553, (255, 255, 255)):
        return False
    return True


def check_for_end_2v2_battle_condition_3(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[518][56],
        iar[517][76],
        iar[558][182],
        iar[546][236],
    ]

    colors = [
        (255, 255, 255),
        (255, 255, 255),
        (78, 175, 255),
        (104, 187, 255),
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=35):
            return False
    return True


def handle_end_2v2_battle_condition_3(logger, vm_index):
    """method to handle the #3 possible end of 2v2 battle screen"""
    if check_for_end_2v2_battle_condition_3(vm_index):
        logger.log("On the end of 2v2 (c3) battle screen to clicking OK button")
        click(vm_index, 216, 554)
        return True
    return False


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


def _2v2_random_fight_loop(vm_index, logger: Logger):
    """method to handle a dynamicly timed 2v2 fight"""

    # while in battle:
    while check_for_in_battle_with_delay(vm_index):
        this_play_start_time = time.time()

        time.sleep(8)

        mag_dump(vm_index, logger)

        # emote sometimes to do daily challenge (jk its to be funny and annoy ur teammate)
        if random.randint(0, 10) == 1:
            emote_in_2v2(vm_index, logger)

        # increment plays counter
        logger.change_status(
            f"Made a play in 2v2 mode in {str(time.time() - this_play_start_time)[:4]}\n"
        )

    logger.change_status("Finished with this 2v2 fight")

    return "good"


if __name__ == "__main__":
    logger = Logger()
    vm_index = 12

    while 1:
        print(check_for_locked_events_page(vm_index))
