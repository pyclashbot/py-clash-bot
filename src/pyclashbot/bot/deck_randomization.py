import random
from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
)
from pyclashbot.detection.image_rec import (
    check_line_for_color,
    crop_image,
    find_references,
    get_file_count,
    get_first_location,
    make_reference_image_list,
)
from pyclashbot.memu.client import click, screenshot, scroll_down, scroll_up
from pyclashbot.utils.logger import Logger
import time

DECK_2_COORD = (158, 127)


def randomize_deck_2(vm_index, logger):
    logger.change_status("Randomizing deck number 2")

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

    # get to clash main

    return "good"


def randomize_this_deck(vm_index, logger: Logger):
    # starts when looking at the deck to randomize

    logger.change_status("Randomizing this deck")

    # count max scrolls
    max_scrolls = count_max_scrolls(vm_index)

    # scroll back to top
    for _ in range(10):
        scroll_up(vm_index)
        time.sleep(1)

    # for each of the 8 cards:
    for card_to_replace_coord in card_to_replace_coords:
        # while doesnt have replacement card:
        while 1:
            # scroll random amount
            for _ in range(random.randint(1, max_scrolls)):
                scroll_up(vm_index)
                time.sleep(1)

            # click a random card
            random_card_coord = find_random_card_in_card_page(vm_index)

            # if doenst have coord at this scroll location:
            if random_card_coord is None:
                # scroll back to top
                for _ in range(10):
                    scroll_up(vm_index)
                    time.sleep(1)

                # redo
                continue

            # click the random card
            click(vm_index, random_card_coord[0], random_card_coord[1])
            time.sleep(1)

            # find use button
            use_card_button_coord = find_use_card_button(vm_index)

            # if there is no use button
            if use_card_button_coord is None:
                # redo
                continue

            # if use button appears:
            # click it
            click(vm_index, use_card_button_coord[0], use_card_button_coord[1])
            time.sleep(3)

            # click coord of card to place
            click(vm_index, card_to_replace_coord[0], card_to_replace_coord[1])
            time.sleep(1)

            # break the while loop
            break


def find_use_card_button(vm_index):
    folder = "use_card_button"
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

    print(f"scrolls is {scrolls}")


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

    random_region = [random.randint(34, 293), random.randint(115, 423), 143, 122]

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
    # count_max_scrolls(1, Logger())
    while 1:
        print(find_random_card_in_card_page_with_delay(1, 5))
        time.sleep(3)
    # screenshot(1)
