"""module for spending the magic items currencies that the bot tends to max out on"""

import time

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    check_if_on_collection_page,
    get_to_collections_page,
    wait_for_clash_main_menu,
)
from pyclashbot.detection.image_rec import pixels_match_colors
from pyclashbot.utils.logger import Logger


def spend_magic_items_state(vm_index: int, logger: Logger, next_state: str) -> str:
    # if not on clash main, return False
    if not check_if_on_clash_main_menu(emulator):
        return "restart"

    if spend_magic_items(vm_index, logger) is False:
        return "restart"

    # return to clash main
    print("Returning to clash main after spending magic items")
    emulator.click(243, 600)
    time.sleep(3)

    # wait for main
    if wait_for_clash_main_menu(vm_index, logger, deadspace_click=False) is False:
        logger.change_status("Failed to wait for clash main after upgrading cards")
        return "restart"

    return next_state


def spend_magic_items(vm_index: int, logger: Logger) -> bool:
    logger.change_status("Spending magic item currencies!")

    # get to magic items page
    logger.change_status("Getting to magic items page...")
    if get_to_collections_page(vm_index) is False:
        logger.change_status("Failed to get to magic items page")

    # select magic items tab
    magic_items_tab_coords = (180, 110)
    logger.log("Clicking magic items tab")
    emulator.click(*magic_items_tab_coords)
    time.sleep(1)

    # spend currency until it doesnt work anymore
    reward_index2name = {
        0: "common",
        1: "rare",
        2: "epic",
        3: "legendary",
    }
    for reward_index in [0, 1, 2, 3]:
        logger.change_status(
            f"Spending magic item type: {reward_index2name[reward_index]}..."
        )
        while spend_rewards(vm_index, logger, reward_index) is True:
            logger.change_status("Successfully spent magic items. Trying again...")
            logger.increment_magic_item_buys()
        logger.change_status(
            f"No more magic item type: {reward_index2name[reward_index]} to spend"
        )
    logger.change_status("Done spending magic item currencies")

    return True


def exit_spend_reward_popup(vm_index) -> bool:
    deadspace = (395, 350)
    start_time = time.time()
    timeout = 30  # s
    while not check_if_on_collection_page(vm_index):
        if time.time() - start_time > timeout:
            return False

        emulator.click(*deadspace)
        time.sleep(1)

    return True


def spend_rewards(vm_index, logger, reward_index) -> bool:
    logger.change_status("Trying to spend the first reward...")

    reward_index2coord = {
        0: (100, 300),
        1: (200, 300),
        2: (300, 300),
        3: (100, 400),
    }
    emulator.click(*reward_index2coord[reward_index])
    time.sleep(1)

    # if the use button doesn't pop up, that mean's we're out of rewards to spend
    if not check_for_use_button(vm_index):
        logger.change_status("No more rewards to spend")
        exit_spend_reward_popup(vm_index)
        return False

    # click the use button
    print("Clicking use currency button")
    use_button_coord = (206, 438)
    emulator.click(*use_button_coord)
    time.sleep(1)

    # click the first card to use it on
    print("Using it on the first card")
    first_card_coord = (80, 200)
    emulator.click(*first_card_coord)
    time.sleep(1)

    # spend the currency
    print("Clicking confirm spend {amount} currency")
    spend_currency_coord = (200, 430)
    emulator.click(*spend_currency_coord)

    # click deadspace
    print("Clicking deadspace until we get back to the collection page")
    exit_spend_reward_popup(vm_index)

    return True


def check_for_use_button(vm_index) -> bool:
    iar = emulator.screenshot()
    pixels = [
        iar[428][188],
        iar[447][198],
        iar[443][208],
        iar[445][218],
        iar[438][220],
        iar[437][222],
        iar[436][224],
        iar[434][226],
        iar[432][227],
        iar[430][225],
        iar[440][223],
        iar[438][189],
        iar[448][227],
    ]
    colors = [
        [255, 131, 156],
        [204, 86, 118],
        [236, 207, 215],
        [75, 55, 61],
        [208, 173, 182],
        [255, 255, 255],
        [101, 52, 62],
        [255, 131, 156],
        [255, 131, 156],
        [255, 131, 156],
        [255, 254, 255],
        [255, 114, 149],
        [255, 108, 147],
    ]

    return pixels_match_colors(pixels, colors, tol=10)


if __name__ == "__main__":
    spend_magic_items_state(1, Logger(), "next_state")
