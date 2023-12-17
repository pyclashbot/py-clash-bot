import time
from typing import Literal

from pyclashbot.bot.nav import (
    check_if_on_card_page,
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
    get_to_clash_main_from_card_page,
)
from pyclashbot.detection.image_rec import check_line_for_color, pixel_is_equal
from pyclashbot.memu.client import click
from pyclashbot.utils.logger import Logger
import numpy
from pyclashbot.memu.client import screenshot


CARD_MASTERY_ICON = (275,476)
FIRST_CARD_MASTERY_REWARD_CARD = (99,170)
CARD_MASTERY_REWARD_COORD_LIST = [
    (202,290),
    (202,300),
    (202,320),
    (202,340),
    (202,360),
    (202,380),
    (202,400),
    (202,430),
    (202,460),
]
CARD_PAGE_DEADSPACE: tuple[Literal[21], Literal[355]] = (5, 355)




def card_mastery_collection_state(vm_index: int, logger: Logger, next_state: str):
    logger.change_status(status="Card mastery collection state")
    logger.add_card_mastery_reward_collection_attempt()

    # if not on clash main, return fail
    clash_main_check = check_if_on_clash_main_menu(vm_index)
    if clash_main_check is not True:
        logger.log("Not on clash main for the start of card_mastery_collection_state()")

        logger.log(
            f"There are the pixels the bot saw after failing to find clash main:"
        )
        for pixel in clash_main_check:
            logger.log(f"   {pixel}")

        return "restart"

    # get to card page
    if get_to_card_page_from_clash_main(vm_index, logger) == "restart":
        logger.log(
            "Failure 528973589  getting to card page for card mastery collection state"
        )
        return "restart"

    # while there are rewards to collect, run the collect loop
    while check_for_card_mastery_rewards_icon(vm_index):
        logger.change_status(status="There are mastery rewards to collect")
        collect_first_card_mastery_reward(vm_index, logger)


    logger.change_status(status="Done collecting mastery rewards")

    if get_to_clash_main_from_card_page(vm_index=vm_index, logger=logger) == "restart":
        logger.change_status(
            status="Error 9856723985 Failure getting to clash main from card page (mastery mode)"
        )
        return "restart"

    return next_state


def collect_first_card_mastery_reward(vm_index, logger):
    # click card mastery reward button
    logger.change_status(status="Clicking card mastery reward button")
    click(
        vm_index,
        CARD_MASTERY_ICON[0],
        CARD_MASTERY_ICON[1],
    )
    time.sleep(3)

    # click first card
    logger.change_status(status="Clicking first card mastery reward")
    click(
        vm_index,
        FIRST_CARD_MASTERY_REWARD_CARD[0],
        FIRST_CARD_MASTERY_REWARD_CARD[1],
    )
    time.sleep(3)

    # click the reward coords
    logger.change_status(status="Clicking rewards")
    for coord in CARD_MASTERY_REWARD_COORD_LIST:
        click(vm_index, coord[0], coord[1])

    logger.add_card_mastery_reward_collection()

    # click deadspace a bunch
    logger.change_status(
        status="Clicking deadspace to skip through mastery rewards"
    )
    click(
        vm_index=vm_index,
        x_coord=CARD_PAGE_DEADSPACE[0],
        y_coord=CARD_PAGE_DEADSPACE[1],
        clicks=21,
        interval=0.33,
    )


def check_for_card_mastery_rewards_icon(vm_index) -> bool:
    if not check_if_on_card_page(vm_index=vm_index):
        return False

    iar = numpy.asarray(screenshot(vm_index))

    pixels = [
        iar[460][280],
        iar[462][280],
        iar[463][280],
        iar[62][36],
    ]

    colors = [
        [56, 8, 235],
        [57, 9, 236],
        [57, 9, 236],
        [86, 44, 10],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=15):
            return False
    return True


if __name__ == "__main__":
    vm_index = 11
    logger = Logger(None)

    card_mastery_collection_state(vm_index, logger, 'next_state')
