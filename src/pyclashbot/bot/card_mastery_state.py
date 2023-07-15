import time
from typing import Literal

from pyclashbot.bot.nav import (
    check_if_on_card_page,
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
    get_to_clash_main_from_card_page,
)
from pyclashbot.detection.image_rec import check_line_for_color
from pyclashbot.memu.client import click
from pyclashbot.utils.logger import Logger

CARD_MASTERY_ICON = (257, 504)
FIRST_CARD_MASTERY_REWARD_CARD = (99, 182)
CARD_MASTERY_REWARD_COORD_LIST = [
    (206, 308),
    (216, 398),
    (224, 485),
]
CARD_PAGE_DEADSPACE: tuple[Literal[21], Literal[355]] = (21, 355)


def card_mastery_collection_state(vm_index: int, logger: Logger, next_state: str):
    logger.change_status(status="Card mastery collection state")
    logger.add_card_mastery_reward_collection_attempt()

    # if not on clash main, return fail
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            status="Error 1983513 Not on clash main for card mastery state"
        )
        return "restart"

    # get to card page
    if get_to_card_page_from_clash_main(vm_index, logger) == "restart":
        logger.log(
            "Failure 528973589  getting to card page for card mastery collection state"
        )
        return "restart"

    # while there are rewards to collect, run the collect loop
    while check_for_card_mastery_rewards_icon_with_delay(vm_index):
        logger.change_status(status="There are mastery rewards to collect")

        # click card mastery reward button
        logger.change_status(status="Clicking card mastery reward button")
        click(
            vm_index,
            CARD_MASTERY_ICON[0],
            CARD_MASTERY_ICON[1],
        )
        time.sleep(1.5)

        # click first card
        logger.change_status(status="Clicking first card mastery reward")
        click(
            vm_index,
            FIRST_CARD_MASTERY_REWARD_CARD[0],
            FIRST_CARD_MASTERY_REWARD_CARD[1],
        )
        time.sleep(1.5)

        # click the reward coords
        logger.change_status(status="Clicking rewards")
        for coord in CARD_MASTERY_REWARD_COORD_LIST:
            click(vm_index, coord[0], coord[1])
            time.sleep(0.5)

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

    logger.change_status(status="Done collecting mastery rewards")

    if get_to_clash_main_from_card_page(vm_index=vm_index, logger=logger) == "restart":
        logger.change_status(
            status="Error 9856723985 Failure getting to clash main from card page (mastery mode)"
        )
        return "restart"

    return next_state


def check_for_card_mastery_rewards_icon_with_delay(vm_index) -> bool | None:
    start_time: float = time.time()
    while 1:
        if time.time() - start_time > 4:
            return False

        if check_for_card_mastery_rewards_icon(vm_index=vm_index):
            return True


def check_for_card_mastery_rewards_icon(vm_index) -> bool:
    if not check_if_on_card_page(vm_index=vm_index):
        return False

    lines: list[bool] = [
        check_line_for_color(
            vm_index=vm_index, x_1=241, y_1=483, x_2=242, y_2=527, color=(255, 188, 42)
        ),
        check_line_for_color(
            vm_index=vm_index, x_1=234, y_1=520, x_2=281, y_2=519, color=(255, 160, 8)
        ),
        check_line_for_color(
            vm_index=vm_index, x_1=264, y_1=482, x_2=283, y_2=500, color=(236, 8, 56)
        ),
        check_line_for_color(
            vm_index=vm_index, x_1=263, y_1=499, x_2=283, y_2=481, color=(236, 8, 56)
        ),
    ]

    return all(lines)


if __name__ == "__main__":
    pass
