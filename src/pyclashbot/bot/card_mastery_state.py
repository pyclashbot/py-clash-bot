from bot.navigation import (
    check_if_on_card_page,
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
    get_to_clash_main_from_card_page,
)
from detection.image_rec import check_line_for_color
from memu.client import click
import time

from utils.logger import Logger

CARD_MASTERY_ICON = (257, 504)
FIRST_CARD_MASTERY_REWARD_CARD = (99, 182)
CARD_MASTERY_REWARD_COORD_LIST = [
    (206, 308),
    (216, 398),
    (224, 485),
]
CARD_PAGE_DEADSPACE = (21, 355)


def card_mastery_collection_state(vm_index: int, logger: Logger, NEXT_STATE: str):
    logger.log("Card mastery collection state")

    # if not on clash main, return fail
    if not check_if_on_clash_main_menu(vm_index):
        logger.log("Error 1983513 Not on clash main for card mastery state")
        return "restart"

    # get to card page
    if get_to_card_page_from_clash_main(vm_index, logger) == "restart":
        return "restart"

    # while there are rewards to collect, run the collect loop
    while check_for_card_mastery_rewards_icon_with_delay(vm_index):
        logger.log("There are mastery rewards to collect")

        # click card mastery reward button
        logger.log("Clicking card mastery reward button")
        click(
            vm_index,
            CARD_MASTERY_ICON[0],
            CARD_MASTERY_ICON[1],
        )
        time.sleep(1.5)

        # click first card
        logger.log("Clicking first card mastery reward")
        click(
            vm_index,
            FIRST_CARD_MASTERY_REWARD_CARD[0],
            FIRST_CARD_MASTERY_REWARD_CARD[1],
        )
        time.sleep(1.5)

        # click the reward coords
        logger.log("Clicking rewards")
        for coord in CARD_MASTERY_REWARD_COORD_LIST:
            click(vm_index, coord[0], coord[1])
            time.sleep(0.5)

        # click deadspace a bunch
        logger.log("Clicking deadspace to skip through mastery rewards")
        click(
            vm_index,
            CARD_PAGE_DEADSPACE[0],
            CARD_PAGE_DEADSPACE[1],
            clicks=21,
            interval=0.33,
        )

    logger.log("Done collecting mastery rewards")

    if get_to_clash_main_from_card_page(vm_index, logger) == "restart":
        logger.log(
            "Error 9856723985 Failure getting to clash main from card page (mastery mode)"
        )
        return "restart"

    return NEXT_STATE


def check_for_card_mastery_rewards_icon_with_delay(vm_index):
    start_time = time.time()
    while 1:
        if time.time() - start_time > 4:
            return False

        if check_for_card_mastery_rewards_icon(vm_index):
            return True


def check_for_card_mastery_rewards_icon(vm_index):
    if not check_if_on_card_page(vm_index):
        return False

    lines = [
        check_line_for_color(
            vm_index, x1=241, y1=483, x2=242, y2=527, color=(255, 188, 42)
        ),
        check_line_for_color(
            vm_index, x1=234, y1=520, x2=281, y2=519, color=(255, 160, 8)
        ),
        check_line_for_color(
            vm_index, x1=264, y1=482, x2=283, y2=500, color=(236, 8, 56)
        ),
        check_line_for_color(
            vm_index, x1=263, y1=499, x2=283, y2=481, color=(236, 8, 56)
        ),
    ]

    return all(lines)


if __name__ == "__main__":
    print(card_mastery_collection_state(1, Logger(), "NEXT_STATE"))

    # while 1:
    #     print(check_for_card_mastery_rewards_icon(1))
