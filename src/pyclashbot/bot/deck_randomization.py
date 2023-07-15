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


def randomize_deck_state(vm_index: int, logger: Logger, next_state: str):
    start_time = time.time()
    logger.change_status("Randomizing deck number 2")
    logger.add_randomize_deck_attempt()

    # if not on clash main, return fail
    if not check_if_on_clash_main_menu(vm_index):
        pass

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

    logger.log(f"Randomize deck state took {str(time.time()-start_time)[:5]}s")
    return next_state


def randomize_this_deck(vm_index, logger: Logger):
    # starts when looking at the deck to randomize

    logger.change_status("Randomizing this deck")

    # count max scrolls
    logger.log("Counting max scrolls")
    max_scrolls = count_max_scrolls(vm_index, logger)
    logger.log(f"There are {max_scrolls} max scrolls")

    logger.log("Getting back to top of card page")
    # scroll back to top
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

    # for each of the 8 cards:
    logger.log("Entering card replacement loop")
    card_index = 0
    for card_to_replace_coord in CARDS_TO_REPLACE_COORDS:
        card_index += 1
        # while doesnt have replacement card:

        start_time = time.time()
        while 1:
            if time.time() - start_time > RANDOM_CARD_SEARCH_TIMEOUT:
                logger.log(
                    "Error 998745 Searched for a rnadom card to repalce the card with for too long"
                )
                return "restart"

            logger.log("Scrolling a random amount")

            # scroll random amount
            scroll_amount = random.randint(1, max_scrolls)
            if scroll_amount < 3:
                scroll_amount = 3
            logger.log(f"Scrolling {scroll_amount} times ")
            for _ in range(scroll_amount):
                scroll_down(vm_index)
                time.sleep(1)
            time.sleep(3)

            # click a random card
            logger.log("Clicking a random card")
            random_card_coord = find_random_card_in_card_page(vm_index)

            # if doenst have coord at this scroll location:
            if random_card_coord is None:
                logger.log("Didnt find a random card.")
                logger.log("Scrolling back to top")
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

                # redo
                continue

            # click the random card
            logger.log("Found a random card. Clicking it.")
            click(vm_index, random_card_coord[0], random_card_coord[1])
            time.sleep(1)

            # find use button
            logger.log("Clicking use card button")
            use_card_button_coord = find_use_card_button(vm_index)

            # if there is no use button
            if use_card_button_coord is None:
                # redo
                logger.log("Didnt find this cards use button")
                logger.log("Scrolling back to top")
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

                # redo
                continue

            # if use button appears:
            # click it
            logger.log("Found use card button")
            click(vm_index, use_card_button_coord[0], use_card_button_coord[1])
            time.sleep(3)

            # click coord of card to replace
            logger.log("Clicking the card to replace")
            click(vm_index, card_to_replace_coord[0], card_to_replace_coord[1])
            time.sleep(1)

            # break the while loop
            logger.log(
                f"Successfully replaced this card: {card_index}/8\n------------------"
            )
            break


def find_use_card_button(vm_index):
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
    logger.change_status("Counting maximum scrolls in your card page")

    scrolls = 3

    for _ in range(3):
        scroll_down(vm_index)

    while find_random_card_in_card_page_with_delay(vm_index, delay=5) is not None:
        scroll_down(vm_index)
        time.sleep(1)
        scrolls += 1

    scrolls = scrolls - 3
    if scrolls < 3:
        scrolls = 3

    return scrolls


def find_random_card_in_card_page_with_delay(vm_index, delay):
    start_time = time.time()

    while 1:
        time_taken = time.time() - start_time
        if time_taken > delay:
            return None

        coord = find_random_card_in_card_page(vm_index)
        if coord is not None:
            return coord


def find_random_card_in_card_page(vm_index):
    img = screenshot(vm_index)

    random_region = [random.randint(34, 293), random.randint(115, 393), 143, 152]

    cropped_image = crop_image(img, random_region)

    coord = find_elixer_price_icon_in_cropped_image(cropped_image, random_region)

    if coord is None:
        return None

    return coord


def find_elixer_price_icon_in_cropped_image(cropped_image, random_region):
    folder = "elixer_price_icon"
    size = get_file_count(folder)

    names = make_reference_image_list(size)

    locations = find_references(
        cropped_image,
        folder,
        names,
        tolerance=0.88,
    )
    coord = get_first_location(locations)

    if coord is None:
        return None
    return [coord[1] + random_region[0], coord[0] + random_region[1]]


def check_if_deck_2_is_selected(vm_index):
    if not check_line_for_color(vm_index, 147, 119, 139, 113, (248, 193, 101)):
        return False
    if not check_line_for_color(vm_index, 171, 112, 163, 118, (236, 160, 81)):
        return False
    if not check_line_for_color(vm_index, 170, 144, 164, 137, (244, 173, 89)):
        return False
    if not check_line_for_color(vm_index, 140, 144, 147, 137, (244, 175, 91)):
        return False
    return True


def select_deck_2(vm_index):
    click(vm_index, DECK_2_COORD[0], DECK_2_COORD[1])


if __name__ == "__main__":
    while 1:
        print(find_random_card_in_card_page(1))
