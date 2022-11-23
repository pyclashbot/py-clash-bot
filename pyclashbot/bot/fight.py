import itertools
import random
import time

import numpy

from pyclashbot.bot.card_detection import (
    get_card_group,
    get_card_images,
    get_play_coords,
    identify_card,
)
from pyclashbot.bot.clashmain import (
    check_if_in_battle,
    check_if_in_battle_with_delay,
    wait_for_clash_main_menu,
)
from pyclashbot.detection import pixel_is_equal
from pyclashbot.memu import click, screenshot


#### card playing
def do_fight(logger):
    logger.change_status("Starting fight")
    in_battle = True
    plays = 0

    while in_battle:
        if wait_until_has_6_elixer(logger) == "restart":
            logger.change_status("Waited for 6 elixer too long. Restarting.")
            return "restart"

        play_random_card(logger)
        plays += 1
        logger.add_card_played()

        in_battle = check_if_in_battle_with_delay()

        if plays > 100:
            logger.change_status(
                "Made too many plays. Match is probably stuck. Ending match"
            )
            return "restart"

    logger.change_status("Done fighting.")
    time.sleep(5)


def wait_until_has_6_elixer(logger):
    # Method to wait untili the bot has 6 expendable elixer

    has_6 = check_if_has_6_elixer()
    logger.change_status("Waiting for 6 elixer")
    loops = 0
    while not has_6:
        loops += 1
        if loops > 250:
            logger.change_status("Waited too long to get to 6 elixer. Restarting.")
            return "restart"
        time.sleep(0.1)
        has_6 = check_if_has_6_elixer()
        if not check_if_in_battle():
            return None


def play_random_card(logger):
    # Method to play a random card

    # Select which card we're to play
    n = random.randint(0, 3)
    # logger.change_status(str("Selected card: "+str(n)))

    # Get an image of this card
    card_image = get_card_images()[n]

    # Identify this card
    card_identification = identify_card(card_image)
    if card_identification is None:
        card_identification = "Unknown"
    # logger.change_status(str("Identified card: "+card_identification))

    # Get the card type of this identification
    card_type = get_card_group(card_identification)
    if card_type is None:
        card_type = "unknown"
    # logger.change_status(str("Card type: "+card_type))

    # Pick a side to play on
    side = pick_a_lane()
    logger.change_status(f"Playing card: {str(n + 1)} on side: {side}")

    # Get the play coordinates of this card type
    play_coords_list = get_play_coords(card_type, side)

    # Pick one of theses coords at random
    play_coord = random.choice(play_coords_list)

    # Click the card we're playing
    if n == 0:
        click(152, 607)
    elif n == 1:
        click(222, 602)
    elif n == 2:
        click(289, 606)
    elif n == 3:
        click(355, 605)

    # print("Playing card ",n," at ",play_coord)

    # Click the location we're playing it at
    click(play_coord[0], play_coord[1])


#### navigation
def leave_end_battle_window(logger):
    # Method for finishing leaving a battle and returning to the clash royale
    # main menu
    # if end screen condition 1 (exit in bottom left)
    if check_if_end_screen_is_exit_bottom_left():
        click(79, 625)
        time.sleep(1)
        if wait_for_clash_main_menu(logger) == "restart":
            logger.change_status("waited for clash main too long")
            return "restart"
        return None

    # if end screen condition 2 (OK in bottom middle)
    if check_if_end_screen_is_ok_bottom_middle():
        click(206, 594)
        time.sleep(1)
        if wait_for_clash_main_menu(logger) == "restart":
            logger.change_status("waited too long for clash main")
            return "restart"
        return None

    if wait_for_clash_main_menu(logger) == "restart":
        logger.change_status("Waited too long for clash main")
        return "restart"
    return None


def check_if_end_screen_is_ok_bottom_middle():
    # Method to check if the end screen is the one with the OK button in the
    # middle
    iar = numpy.array(screenshot())
    # (210,589)
    pix_list = [
        iar[591][234],
        iar[595][178],
        iar[588][192],
        iar[591][233],
    ]
    color = [78, 175, 255]
    return all((pixel_is_equal(pix, color, tol=45)) for pix in pix_list)


def check_if_end_screen_is_exit_bottom_left():
    # Method to check if the end screen is the one with the exit button in the
    # bottom left
    iar = numpy.array(screenshot())
    pix_list = [
        iar[638][57],
        iar[640][110],
        iar[622][59],
        iar[621][110],
    ]
    color = [87, 186, 255]
    return all((pixel_is_equal(pix, color, tol=45)) for pix in pix_list)


def open_activity_log():
    # Method for opening the activity log from the clash royale main menu as
    # to see past game outcomes
    click(x=360, y=99)
    time.sleep(1)

    click(x=255, y=75)
    time.sleep(1)


#### detection
def check_if_past_game_is_win(logger):
    # Method for reading the actiivty log to check if the previous game was a
    # win or loss
    open_activity_log()
    iar = numpy.array(screenshot())

    for n in range(40, 130):
        pix = iar[191][n]
        sentinel = [1] * 3
        sentinel[0] = 102
        sentinel[1] = 204
        sentinel[2] = 255
        if pixel_is_equal(pix, sentinel, 10):
            _extracted_from_check_if_past_game_is_win_12(
                logger, "Last game was a win. Incrementing win counter."
            )

            logger.add_win()
            return True
    time.sleep(1)
    click(385, 507)
    _extracted_from_check_if_past_game_is_win_12(
        logger, "Last game was a loss. Incrementing loss counter."
    )

    logger.add_loss()
    return False


def check_if_has_6_elixer():
    # Method to see if the bot has 6 expendable elixer in the given moment
    # during a battle
    iar = numpy.array(screenshot())
    pix_list = [
        # iar[643][258],
        iar[648][272],
        iar[649][257],
    ]
    color_list = [[208, 34, 214], [245, 175, 250]]

    return any(
        pixel_is_equal(pix, color, tol=45)
        for color, pix in itertools.product(color_list, pix_list)
    )


#### board detection
def cover_board_image(iar):
    # Method for covering parts of a board image that may obstruct enemy
    # detection

    # Cover left enemy tower
    for x, y in itertools.product(range(101, 147), range(154, 215)):
        iar[y][x] = [0, 0, 0]

    # Cover enemy king tower
    for x, y in itertools.product(range(156, 266), range(81, 185)):
        iar[y][x] = [0, 0, 0]

    # Cover enemy right tower
    for x, y in itertools.product(range(272, 322), range(152, 216)):
        iar[y][x] = [0, 0, 0]

    # Cover left side
    for x, y in itertools.product(range(70), range(700)):
        iar[y][x] = [0, 0, 0]

    # Cover right side
    for x, y in itertools.product(range(350, 500), range(700)):
        iar[y][x] = [0, 0, 0]

    # Cover bottom
    for x, y in itertools.product(range(500), range(495, 700)):
        iar[y][x] = [0, 0, 0]

    # Cover top
    for x, y in itertools.product(range(500), range(70)):
        iar[y][x] = [0, 0, 0]

    # Cover river
    for x, y in itertools.product(range(500), range(300, 340)):
        iar[y][x] = [0, 0, 0]

    # Cover friendly left tower
    for x, y in itertools.product(range(101, 148), range(401, 452)):
        iar[y][x] = [0, 0, 0]

    # Cover friendly right tower
    for x, y in itertools.product(range(275, 320), range(403, 459)):
        iar[y][x] = [0, 0, 0]

    # Cover friendly king tower
    for x, y in itertools.product(range(152, 269), range(442, 500)):
        iar[y][x] = [0, 0, 0]

    # Cover top again
    for x, y in itertools.product(range(500), range(50, 136)):
        iar[y][x] = [0, 0, 0]

    # return
    return iar


def get_left_and_right_totals(iar):
    # Method for getting the left and right totals of enemies on the board

    left_lane_total = 0
    right_lane_total = 0

    red = [212, 45, 43]
    for x, y in itertools.product(range(500), range(700)):
        pixel = iar[y][x]
        if pixel_is_equal(pixel, red, tol=35):
            if x > 250:
                right_lane_total += 1
            if x < 250:
                left_lane_total += 1

    return left_lane_total, right_lane_total


def pick_a_lane():
    # Method for choosing a side to attack based on the number of enemies on
    # each side
    # Either returns left right or random
    iar = numpy.array(screenshot())

    covered_iar = cover_board_image(iar)

    lane_ratio = get_left_and_right_totals(covered_iar)

    if (lane_ratio[0] < 10) and (lane_ratio[1] < 10):
        return "random"
    return "right" if lane_ratio[1] > lane_ratio[0] else "left"


#### etc
def _extracted_from_check_if_past_game_is_win_12(logger, arg1):
    click(20, 507)

    logger.change_status(arg1)
    time.sleep(2)
