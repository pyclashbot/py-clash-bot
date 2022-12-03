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
from pyclashbot.bot.deck import check_if_pixel_is_grey
from pyclashbot.detection import pixel_is_equal
from pyclashbot.memu import click, screenshot


#### card playing
def do_fight(logger):
    """
    do_fight waits until has 6 elixer, then plays a random card, all on a loop until it detects that the battle is over
    :logger: logger from logger class initialized in main
    :return: returns "restart" upon any failure. Else returns None
    """

    logger.change_status("Starting fight")
    in_battle = True
    plays = 0

    while in_battle:
        print("plays: ", plays)
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
    """
    wait_until_has_6_elixer does check_if_has_6_elixer() check every 0.1 seconds until it returns True (periodically checking if the battle is over also)
    :logger: logger object from logger class initialized in main
    :return: returns "restart" if waited too long, else returns None.
    """

    has_6 = check_if_has_6_elixer()
    logger.change_status("Waiting for 6 elixer")
    loops = 0
    while not has_6:
        if check_if_all_cards_are_available():
            logger.change_status("All cards are available. Making a play")
            break

        loops += 1
        if loops > 250:
            logger.change_status("Waited too long to get to 6 elixer. Restarting.")
            return "restart"
        time.sleep(0.1)
        has_6 = check_if_has_6_elixer()
        if not check_if_in_battle():
            return None


def play_random_card(logger):
    """
    play_random_card picks a random card (1-4), identifies it, detemines the play logic for this card, then plays it according to that logic
    :logger: logger object from logger class initialized in main
    :return: None
    """

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
    print("current card identification: ", card_identification)

    # Get the card type of this identification
    card_type = get_card_group(card_identification)
    if card_type is None:
        card_type = "unknown"
    print("Current card group: ", card_type)

    # Pick a side to play on
    side = pick_a_lane()
    logger.change_status(f"Playing card: {str(card_identification)} on side: {side}")

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

    # Click the location we're playing it at
    click(play_coord[0], play_coord[1])


#### navigation
def leave_end_battle_window(logger):
    """
    leave_end_battle_window checks which end screen case is (there are two),
    clicks the appropriate button to leave the end battle screen, then waits for clash main.
    :logger: logger object from logger class initialized in main
    :return: returns "restart" if it fails to get to clash main, else None
    """

    # if end screen condition 1 (exit in bottom left)
    if check_if_end_screen_is_exit_bottom_left():
        print("Leaving end battle (condition 1)")
        click(79, 625)
        time.sleep(1)
        if wait_for_clash_main_menu(logger) == "restart":
            logger.change_status("waited for clash main too long")
            return "restart"
        return None

    # if end screen condition 2 (OK in bottom middle)
    if check_if_end_screen_is_ok_bottom_middle():
        print("Leaving end battle (condition 2)")
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
    """
    check_if_end_screen_is_ok_bottom_middle checks for one of the end of battle screen cases (OK in bottom middle)
    :return: bool: True if pixels indicate this is the case, else False
    """

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
    """
    check_if_end_screen_is_exit_bottom_left checks for one of the end of battle screen cases (OK in bottom left)
    :return: bool: True if pixels indicate this is the case, else False
    """

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
    """
    open_activity_log opens the activity log from the clash main
    :return: None
    """

    print("Opening activity log")
    click(x=360, y=99)
    time.sleep(1)

    click(x=255, y=75)
    time.sleep(1)


#### detection
def check_if_past_game_is_win(logger):
    """
    check_if_past_game_is_win scans the pixels across a specific region in the acitvity log that indicate the past game's win or loss.
    :logger: logger object from logger class initialized
    :return: bool: true if pixels are blue, else false
    """

    print("Checking if game was a win")
    open_activity_log()
    time.sleep(3)
    if check_if_pixels_indicate_win_on_activity_log():
        logger.change_status("Last game was a win. Incrementing win count.")
        logger.add_win()
    else:
        logger.change_status("Last game was a loss. Incrementing loss count.")

        logger.add_loss()

    # Close activity log
    click(200, 640)
    time.sleep(2)


def check_if_pixels_indicate_win_on_activity_log():
    # fill pix list with a list of pixels that scan across the victory/defeat text
    iar = numpy.asarray(screenshot())
    pix_list = [iar[180][x_coord] for x_coord in range(48, 113)]
    # cast this list to ints
    int_pix_list = []
    for pix in pix_list:
        this_int_pix = [int(pix[0]), int(pix[1]), int(pix[2])]
        int_pix_list.append(this_int_pix)

    # count red pixels
    red_count = sum(
        bool(pixel_is_equal(pix, [255, 50, 100], tol=35)) for pix in int_pix_list
    )

    # return logic
    return red_count <= 10


def check_if_has_6_elixer():
    """
    check_if_has_6_elixer checks pixels in the bottom elixer bar during a fight to see if it is full to the point of 6 elixer.
    :return: true if pixels are pink, else false
    """

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
    """
    cover_board_image covers specific regions in the board image with black that may indicate false positives to make the board detection more accurate.
    :iar: a numpy image array. This is the image array of the board screenshot.
    :return: iar: the image array of the board screenshot with the covered regions.
    """

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
    """
    get_left_and_right_totals counts the red pixels on the left and right lanes of the board.
    :iar: a numpy image array. This is the image array of the board screenshot.
    :return: [left_lane_total, right_lane_total]: integer totals of the red pixels on the left and right lanes of the board.
    """

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
    """
    pick_a_lane gets a numpy image array of the board screenshot, covers the regions that may indicate false positives, and counts the red pixels on the left and right lanes of the board. It then returns the lane with the most red pixels.
    :return: String: "left" or "right" depending on which lane has the most red pixels. Returns "random" if the lanes are equal within a threshold.
    """

    iar = numpy.array(screenshot())

    covered_iar = cover_board_image(iar)

    lane_ratio = get_left_and_right_totals(covered_iar)

    # if (lane_ratio[0] < 10) and (lane_ratio[1] < 10):
    #     return "random"
    # return "right" if lane_ratio[1] > lane_ratio[0] else "left"

    return "random"


##### to sort
def check_if_card_1_is_available():
    iar = numpy.asarray(screenshot())
    pix_list = [
        iar[560][120],
        iar[580][135],
        iar[610][165],
    ]

    grey_bool_list = []
    for pix in pix_list:
        grey_bool = check_if_pixel_is_grey(pix)
        grey_bool_list.append(grey_bool)

    is_available = False
    for is_grey in grey_bool_list:
        if not is_grey:
            is_available = True

    return is_available


def check_if_card_2_is_available():
    iar = numpy.asarray(screenshot())
    pix_list = [
        iar[565][185],
        iar[585][195],
        iar[595][210],
        iar[610][230],
    ]

    grey_bool_list = []
    for pix in pix_list:
        grey_bool = check_if_pixel_is_grey(pix)
        grey_bool_list.append(grey_bool)

    # print(grey_bool_list)

    is_available = False
    for is_grey in grey_bool_list:
        if not is_grey:
            is_available = True

    return is_available


def check_if_card_3_is_available():
    iar = numpy.asarray(screenshot())
    pix_list = [
        iar[565][250],
        iar[585][265],
        iar[595][285],
        iar[610][300],
    ]

    grey_bool_list = []
    for pix in pix_list:
        grey_bool = check_if_pixel_is_grey(pix)
        grey_bool_list.append(grey_bool)

    # print(grey_bool_list)

    is_available = False
    for is_grey in grey_bool_list:
        if not is_grey:
            is_available = True

    return is_available


def check_if_card_4_is_available():
    iar = numpy.asarray(screenshot())
    pix_list = [
        iar[565][320],
        iar[585][335],
        iar[595][350],
        iar[610][365],
    ]

    grey_bool_list = []
    for pix in pix_list:
        grey_bool = check_if_pixel_is_grey(pix)
        grey_bool_list.append(grey_bool)

    # print(grey_bool_list)

    is_available = False
    for is_grey in grey_bool_list:
        if not is_grey:
            is_available = True

    return is_available


def check_available_cards():
    available_cards_return = [False, False, False, False]
    available_cards_return[0] = check_if_card_1_is_available()
    available_cards_return[1] = check_if_card_2_is_available()
    available_cards_return[2] = check_if_card_3_is_available()
    available_cards_return[3] = check_if_card_4_is_available()

    return available_cards_return


def check_if_all_cards_are_available():
    available_cards = check_available_cards()
    return all(available_cards)
