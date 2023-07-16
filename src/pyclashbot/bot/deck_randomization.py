"""random import for deck randomization"""
import random
import time
from typing import Literal

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
    get_to_clash_main_from_card_page,
)
from pyclashbot.detection.image_rec import (
    check_line_for_color,
    crop_image,
    find_references,
    get_file_count,
    get_first_location,
    make_reference_image_list,
)
from pyclashbot.memu.client import click, screenshot, scroll_down
from pyclashbot.utils.logger import Logger

DECK_2_COORD: tuple[Literal[158], Literal[127]] = (158, 127)

CLASH_MAIN_ICON_FROM_CARD_PAGE: tuple[Literal[245], Literal[600]] = (245, 600)
CARD_PAGE_ICON_FROM_CLASH_MAIN: tuple[Literal[115], Literal[600]] = (115, 600)
RANDOM_CARD_SEARCH_TIMEOUT = 120  # seconds
CARDS_TO_REPLACE_COORDS = [
    (72, 240),
    (156, 240),
    (257, 240),
    (339, 240),
    (72, 399),
    (156, 399),
    (257, 399),
    (339, 399),
]
FIND_REPLACEMENT_CARD_TIMEOUT = 10


def randomize_deck_state(vm_index: int, logger: Logger, next_state: str):
    """method to handle the entirety of the
    randomize deck state in the state tree"""

    start_time = time.time()
    logger.change_status("Randomizing deck number 2")
    logger.add_randomize_deck_attempt()

    # if not on clash main, return fail
    if not check_if_on_clash_main_menu(vm_index):
        logger.log("Error 775 Not on clash main for deck randomization state ")
        return "restart"

    # get to card page tab
    if get_to_card_page_from_clash_main(vm_index, logger) == "restart":
        logger.log(
            "Error 9357389 Failed to get to card page from clash main for deck randomizing"
        )
        return "restart"

    # make sure deck 2 is selected
    if not check_if_deck_2_is_selected(vm_index):
        logger.change_status("Selecting deck number 2")
        select_deck_2(vm_index)
        time.sleep(1)

    # run deck randomize function
    if randomize_this_deck(vm_index, logger) == "restart":
        return "restart"

    # get to clash main
    if get_to_clash_main_from_card_page(vm_index, logger) == "restart":
        logger.log("Error 85893 Issue getting to clash main after deck randomization")

    time_taken = time.time() - start_time
    mins = int(time_taken / 60)
    time_taken = time_taken - (mins * 60)
    seconds = int(time_taken)

    logger.log(f"Randomize deck state took {mins}m {seconds}s")
    return next_state


def reset_card_page_scroll(vm_index):
    """method to reset the clash card page scroll to the top by leaving and returning to the page"""

    click(
        vm_index,
        CLASH_MAIN_ICON_FROM_CARD_PAGE[0],
        CLASH_MAIN_ICON_FROM_CARD_PAGE[1],
    )
    time.sleep(2)
    click(
        vm_index,
        CARD_PAGE_ICON_FROM_CLASH_MAIN[0],
        CARD_PAGE_ICON_FROM_CLASH_MAIN[1],
    )
    time.sleep(2)


def scroll_random_amount_on_card_page(vm_index, logger, max_scrolls):
    """method to scroll a random amount on the clash card page given a max"""

    # scroll random amount
    scroll_amount: int = random.randint(1, max_scrolls)
    scroll_amount = max(3, scroll_amount)

    logger.log(f"Scrolling {scroll_amount} times ")
    for _ in range(scroll_amount):
        scroll_down(vm_index)
        time.sleep(0.5)
    time.sleep(3)

    return "good"


def click_random_card_on_card_page(logger, vm_index) -> Literal["fail", "good"]:
    """method to find a random card on the card page and click it"""

    # click a random card
    logger.log("Clicking a random card")
    random_card_coord = find_random_card_in_card_page(vm_index)

    # if doenst have coord at this scroll location:
    if random_card_coord is None:
        logger.log("Didnt find a random card.")
        logger.log("Scrolling back to top")
        return "fail"

    # click the random card
    click(vm_index, random_card_coord[0] + 5, random_card_coord[1] + 5)
    time.sleep(1)

    return "good"


def find_and_click_replacement_card_on_this_page(
    vm_index, logger
) -> Literal["success", "fail"]:
    """method to try to find and click a replacement card on the current card page"""

    start_time: float = time.time()

    # while within timeout:
    while time.time() - start_time < FIND_REPLACEMENT_CARD_TIMEOUT:
        # click a new card, if fail, continue
        if click_random_card_on_card_page(logger, vm_index) == "fail":
            logger.log("failed to click a card")
            continue

        # find use, if no use, continue
        if click_use_card_button(vm_index, logger) == "fail":
            logger.log("Failed to click use card button")
            continue

        logger.log("Got the use card button!")
        return "success"

    logger.log("Failed to find a replacement card within timeout")
    return "fail"


def click_use_card_button(vm_index, logger) -> Literal["fail", "success"]:
    """method to find and click the use card button on the card page"""

    # find use button
    logger.log("Clicking use card button")
    use_card_button_coord = find_use_card_button(vm_index)

    # if there is no use button
    if use_card_button_coord is None:
        return "fail"

    # if use button appears:
    # click it
    logger.log("Found use card button")
    click(vm_index, use_card_button_coord[0], use_card_button_coord[1])
    time.sleep(3)
    return "success"


def randomize_deck(vm_index, logger, max_scrolls) -> Literal["restart", "good"]:
    """method to randomize the deck currently on the screen given a max_scrolls amount"""

    card_index = 0
    for card_to_replace_coord in CARDS_TO_REPLACE_COORDS:
        this_card_replacement_start_time = time.time()
        card_index += 1
        start_time = time.time()

        logger.change_status(f"Replacing card {card_index}/8")

        # while doesnt have replacement card:
        while 1:
            if time.time() - start_time > RANDOM_CARD_SEARCH_TIMEOUT:
                logger.log(
                    "Error 998745 Searched for a rnadom card to repalce the card with for too long"
                )
                return "restart"

            logger.log("Scrolling a random amount")

            # scroll random amount
            scroll_random_amount_on_card_page(vm_index, logger, max_scrolls)

            if find_and_click_replacement_card_on_this_page(vm_index, logger) == "fail":
                reset_card_page_scroll(vm_index)
                continue
            time.sleep(3)

            #  CHECK FOR CHAMPION TYPE CARD
            if check_for_champion_replacement_card(vm_index, logger):
                logger.log(
                    "Champion type card so its no good. Gotta redo this card replacement"
                )
                reset_card_page_scroll(vm_index)
                continue

            logger.log("This card type is good!")

            # click coord of card to replace
            logger.log("Clicking the card to replace")
            click(vm_index, card_to_replace_coord[0], card_to_replace_coord[1])
            time.sleep(1)

            # break the while loop
            logger.add_card_randomization()
            this_card_replacement_time_taken: str = str(
                time.time() - this_card_replacement_start_time
            ).split(".", maxsplit=1)[0]
            logger.change_status(
                f"Replaced this card in {this_card_replacement_time_taken}s {card_index}/8"
            )
            logger.log("- - - - - - - - - - - - -")
            break

    return "good"


def randomize_this_deck(vm_index, logger: Logger) -> Literal["good"]:
    """method to count max scrolls then randomize the deck currently on the screen"""

    # starts when looking at the deck to randomize

    logger.change_status("Randomizing this deck")
    time.sleep(1)

    # count max scrolls
    logger.change_status("Counting length of your card list")

    logger.log("Counting max scrolls")
    max_scrolls: int = count_max_scrolls(vm_index, logger)
    logger.log(f"There are {max_scrolls} max scrolls")

    logger.log("Getting back to top of card page")
    # scroll back to top
    reset_card_page_scroll(vm_index)

    # for each of the 8 cards:
    logger.log("Entering card replacement loop")
    logger.change_status("Replacing this deck with random cards...")

    random.shuffle(CARDS_TO_REPLACE_COORDS)
    randomize_deck(vm_index, logger, max_scrolls)

    return "good"


def find_use_card_button(vm_index):
    """method to scan a screenshot image for the use card button image and return its coord"""

    folder = "use_button"
    size = get_file_count(folder)

    names = make_reference_image_list(size)

    locations = find_references(
        screenshot(vm_index),
        folder,
        names,
        tolerance=0.88,
    )
    coord = get_first_location(locations)

    if coord is None:
        return None
    return [coord[1], coord[0]]


def count_max_scrolls(vm_index, logger):
    """method to count how many adb scrolls it takes to get to the bottom of the card page"""

    logger.change_status("Counting maximum scrolls in your card page")

    scrolls = 3

    for _ in range(3):
        scroll_down(vm_index)
        time.sleep(0.3)

    while (
        find_random_card_in_bottom_half_of_card_page_with_timeout(vm_index, timeout=6)
        is not None
    ):
        scroll_down(vm_index)
        time.sleep(0.33)
        scrolls += 1

    scrolls = scrolls - 3
    scrolls = max(scrolls, 3)

    return scrolls


def find_random_card_in_card_page_with_timeout(vm_index, timeout) -> list[int] | None:
    """method to find a random card on the page with a timeout"""

    start_time = time.time()

    while 1:
        time_taken = time.time() - start_time
        if time_taken > timeout:
            return None

        coord = find_random_card_in_card_page(vm_index)
        if coord is not None:
            return coord


def find_random_card_in_bottom_half_of_card_page_with_timeout(
    vm_index, timeout
) -> list[int] | None:
    """method to find a random card in the
    bottom half of the card page with a timeout"""

    start_time: float = time.time()

    while 1:
        time_taken: float = time.time() - start_time
        if time_taken > timeout:
            return None

        coord: list[int] | None = find_random_card_in_bottom_half_of_card_page(vm_index)
        if coord is not None:
            return coord


def find_random_card_in_bottom_half_of_card_page(vm_index) -> list[int] | None:
    """method to scan the bottom half of the screen for a usable card. Bottom
    half so it can detect bottom of card page on 109/109 cards unlocked accounts"""

    img = screenshot(vm_index)

    region_1: list[int] = [19, 370, 370, 178]
    region_2: list[int] = [178, 302, 223, 241]

    cropped_image_1 = crop_image(img, region_1)
    cropped_image_2 = crop_image(img, region_2)

    coord_1: list[int] | None = find_elixer_price_icon_in_cropped_image(
        cropped_image_1, region_1
    )
    coord_2: list[int] | None = find_elixer_price_icon_in_cropped_image(
        cropped_image_2, region_2
    )

    if coord_1 is not None:
        return coord_1

    if coord_2 is not None:
        return coord_2

    return None


def find_random_card_in_card_page(vm_index):
    """method to find a random card on the card page given the entire region"""

    img = screenshot(vm_index)

    random_region: list[int] = [
        random.randint(34, 293),
        random.randint(115, 393),
        143,
        152,
    ]

    cropped_image = crop_image(img, random_region)

    coord: list[int] | None = find_elixer_price_icon_in_cropped_image(
        cropped_image, random_region
    )

    if coord is None:
        return None

    return coord


def find_elixer_price_icon_in_cropped_image(cropped_image, random_region):
    """method to find the elixer price icon in a cropped image"""

    folder = "elixer_price_icon"
    size: int = get_file_count(folder)

    names = make_reference_image_list(size)

    locations: list[list[int] | None] = find_references(
        cropped_image,
        folder,
        names,
        tolerance=0.88,
    )
    coord: list[int] | None = get_first_location(locations)

    if coord is None:
        return None
    return [coord[1] + random_region[0], coord[0] + random_region[1]]


def check_if_deck_2_is_selected(vm_index) -> bool:
    """method to scan pixels on the card tab to see if the 2 deck is selected"""

    if not check_line_for_color(vm_index, 147, 119, 139, 113, (248, 193, 101)):
        return False
    if not check_line_for_color(vm_index, 171, 112, 163, 118, (236, 160, 81)):
        return False
    if not check_line_for_color(vm_index, 170, 144, 164, 137, (244, 173, 89)):
        return False
    if not check_line_for_color(vm_index, 140, 144, 147, 137, (244, 175, 91)):
        return False
    return True


def select_deck_2(vm_index) -> Literal["good"]:
    """method to click the location of the deck 2 button"""
    click(vm_index, DECK_2_COORD[0], DECK_2_COORD[1])
    return "good"


def check_for_champion_replacement_card(vm_index, logger):
    """method to check if the card the randomizer is
    going to use as a replacement card is a champion type card"""

    if check_for_skeleton_king(vm_index):
        logger.log("Detected skeleton_king")
        return True
    if check_for_archer_queen(vm_index):
        logger.log("Detected archer_queen")
        return True
    if check_for_golden_knight(vm_index):
        logger.log("Detected golden_knight")
        return True
    if check_for_mighty_miner(vm_index):
        logger.log("Detected mighty_miner")
        return True
    if check_for_monk(vm_index):
        logger.log("Detected monk")
        return True

    logger.log("Not a champion type card.")
    return False


def check_for_monk(vm_index) -> bool:
    """method to check if the card the randomizer is
    going to use as a replacement card is a monk"""

    if not check_line_for_color(vm_index, 191, 551, 201, 554, (225, 202, 181)):
        return False
    if not check_line_for_color(vm_index, 217, 547, 223, 553, (254, 249, 233)):
        return False
    if not check_line_for_color(vm_index, 204, 544, 212, 543, (235, 140, 78)):
        return False
    if not check_line_for_color(vm_index, 225, 547, 233, 549, (49, 165, 156)):
        return False
    if not check_line_for_color(vm_index, 188, 556, 180, 555, (97, 164, 156)):
        return False
    return True


def check_for_archer_queen(vm_index) -> bool:
    """method to check if the card the randomizer is
    going to use as a replacement card is a archer_queen"""

    if not check_line_for_color(vm_index, 186, 565, 184, 554, (175, 105, 75)):
        return False
    if not check_line_for_color(vm_index, 236, 557, 226, 553, (254, 226, 92)):
        return False
    if not check_line_for_color(vm_index, 223, 544, 214, 539, (79, 44, 112)):
        return False
    if not check_line_for_color(vm_index, 210, 563, 208, 553, (182, 91, 18)):
        return False

    return True


def check_for_golden_knight(vm_index) -> bool:
    """method to check if the card the randomizer is
    going to use as a replacement card is a golden_knight"""

    if not check_line_for_color(vm_index, 203, 552, 202, 541, (251, 227, 106)):
        return False
    if not check_line_for_color(vm_index, 201, 554, 195, 560, (254, 224, 117)):
        return False
    if not check_line_for_color(vm_index, 210, 551, 217, 557, (254, 234, 137)):
        return False
    if not check_line_for_color(vm_index, 213, 552, 219, 544, (155, 98, 43)):
        return False
    return True


def check_for_mighty_miner(vm_index) -> bool:
    """method to check if the card the randomizer is
    going to use as a replacement card is a mighty_miner"""

    if not check_line_for_color(vm_index, 202, 563, 203, 546, (236, 165, 79)):
        return False
    if not check_line_for_color(vm_index, 219, 565, 222, 559, (83, 36, 33)):
        return False
    if not check_line_for_color(vm_index, 181, 562, 186, 563, (118, 98, 99)):
        return False
    if not check_line_for_color(vm_index, 189, 566, 180, 561, (254, 242, 105)):
        return False
    return True


def check_for_skeleton_king(vm_index) -> bool:
    """method to check if the card the randomizer is
    going to use as a replacement card is a skeleton_king"""
    if not check_line_for_color(vm_index, 207, 544, 216, 547, (166, 176, 227)):
        return False
    if not check_line_for_color(vm_index, 194, 555, 205, 566, (8, 4, 9)):
        return False
    if not check_line_for_color(vm_index, 226, 554, 227, 567, (17, 0, 7)):
        return False
    if not check_line_for_color(vm_index, 193, 544, 176, 543, (169, 8, 169)):
        return False
    return True


if __name__ == "__main__":
    pass
