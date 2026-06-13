import time

from pyclashbot.bot.coords import (
    CARD_MASTERY_COLLECT_COORD,
    CARD_MASTERY_OPTIONS_COORD,
    CARD_MASTERY_RETURN_TO_MAIN_COORD,
    CARD_MASTERY_TAB_COORD,
)
from pyclashbot.bot.nav import (
    get_to_card_page_from_clash_main,
    wait_for_clash_main_menu,
)
from pyclashbot.bot.state_detect import (
    card_mastery_rewards_exist,
    check_for_inventory_full_popup,
    check_if_on_card_page,
    check_if_on_clash_main_menu,
)
from pyclashbot.utils.logger import Logger


def card_mastery_state(emulator, logger):
    logger.change_status("Going to collect Card Mastery rewards")

    if check_if_on_clash_main_menu(emulator) is not True:
        logger.change_status("Not on main menu — cannot collect Card Mastery rewards")
        return False

    if collect_card_mastery_rewards(emulator, logger) is False:
        logger.change_status("Failed to collect Card Mastery rewards")
        return False

    return True


def collect_card_mastery_rewards(emulator, logger: Logger) -> bool:
    # get to card page
    logger.change_status("Collecting Card Mastery rewards...")
    if get_to_card_page_from_clash_main(emulator, logger) == "restart":
        logger.change_status(
            "Failed to open card page for Card Mastery rewards",
        )
        return False
    time.sleep(3)

    if not card_mastery_rewards_exist_with_delay(emulator):
        logger.change_status("No Card Mastery rewards to collect.")
        time.sleep(1)

    else:
        # while card mastery icon exists:
        while card_mastery_rewards_exist_with_delay(emulator):
            logger.change_status("Detected Card Mastery rewards")
            #   click card mastery icon
            collect_first_mastery_reward(emulator)
            logger.change_status("Collected a Card Mastery reward!")
            logger.add_card_mastery_reward_collection()
            time.sleep(2)

    # get to clash main
    logger.change_status("Returning to main menu")
    emulator.click(CARD_MASTERY_RETURN_TO_MAIN_COORD[0], CARD_MASTERY_RETURN_TO_MAIN_COORD[1])

    # wait for main to appear
    if wait_for_clash_main_menu(emulator, logger) is False:
        logger.change_status(
            "Timed out returning to main menu from card page",
        )
        return False

    return True


def collect_first_mastery_reward(emulator):
    # click the card mastery reward icon
    emulator.click(CARD_MASTERY_OPTIONS_COORD[0], CARD_MASTERY_OPTIONS_COORD[1])
    time.sleep(0.5)

    # click first card
    emulator.click(CARD_MASTERY_TAB_COORD[0], CARD_MASTERY_TAB_COORD[1])
    time.sleep(0.5)

    # click rewards at specific Y positions
    y_positions = [316, 403, 488]
    for y in y_positions:
        emulator.click(200, y)
        time.sleep(1)
        if check_for_inventory_full_popup(emulator):
            print("Inventory full popup detected!\nClicking it")
            emulator.click(CARD_MASTERY_COLLECT_COORD[0], CARD_MASTERY_COLLECT_COORD[1])
            time.sleep(1)

    # click deadspace
    ds = (14, 278)
    ds_click_timeout = 60  # s
    ds_start_time = time.time()
    while not check_if_on_card_page(emulator):
        emulator.click(*ds)

        if time.time() - ds_start_time > ds_click_timeout:
            print("Clicked deadspace after collecting card mastery reward for too long")
            return False

    return True


def card_mastery_rewards_exist_with_delay(emulator):
    timeout = 2  # s
    start_time = time.time()
    while time.time() - start_time < timeout:
        if card_mastery_rewards_exist(emulator):
            return True

    return False


if __name__ == "__main__":
    collect_first_mastery_reward(1)
