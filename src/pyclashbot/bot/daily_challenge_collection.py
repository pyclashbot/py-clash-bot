from pyclashbot.bot.nav import check_if_on_clash_main_menu
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.utils.logger import Logger
import numpy
from pyclashbot.memu.client import screenshot, click
import time


def collect_daily_rewards_state(vm_index, logger, next_state):
    if collect_all_daily_rewards(vm_index, logger) is False:
        logger.change_status("Failed to collect daily rewards")
        return "restart"

    return next_state


def collect_challenge_rewards(vm_index, logger, rewards) -> bool:
    # if not on clash main, reutrn False
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(
            "Not on clash main at start of collect_challenge_rewards(). Returning False"
        )
        return False

    # open daily rewards menu
    click(vm_index, 41, 206)
    time.sleep(2)

    # click first task's reward
    if rewards[0]:
        click(vm_index, 90, 191)
        logger.change_status("Collected 1st daily challenge reward")
        logger.add_daily_reward()
        time.sleep(1)

        # click deadspace a few times
        click(vm_index, 10, 350, clicks=5, interval=1)

        # reopen daily rewards menu
        click(vm_index, 41, 206)
        time.sleep(2)

    # click second task's reward
    if rewards[1]:
        click(vm_index, 90, 260)
        logger.change_status("Collected 2nd daily challenge reward")
        logger.add_daily_reward()
        time.sleep(1)

        # click deadspace a few times
        click(vm_index, 10, 350, clicks=5, interval=1)

        # reopen daily rewards menu
        click(vm_index, 41, 206)
        time.sleep(2)

    # click third task's reward
    if rewards[2]:
        click(vm_index, 90, 330)
        logger.change_status("Collected 3rd daily challenge reward")
        logger.add_daily_reward()
        time.sleep(1)

    # click deadspace a bunch
    deadspace_clicks = 5
    if rewards[1]:
        deadspace_clicks = 15
    click(vm_index, 15, 290, clicks=deadspace_clicks, interval=0.33)

    # if not on clash main, reutrn False
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(
            "Not on clash main at start of collect_challenge_rewards(). Returning False"
        )
        return False

    return True


def collect_daily_bonus(vm_index, logger) -> bool:
    # if not on clash main, retunr False
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(
            "Not on clash main at start of collect_daily_bonus(). Returning False"
        )
        return False

    # open daily rewards menu
    click(vm_index, 41, 206)
    time.sleep(2)

    # click the daily bonus reward
    click(vm_index, 206, 415)
    logger.add_daily_reward()
    logger.change_status("Collected daily reward chest")
    time.sleep(1)

    # click deadspace a bunch
    print('deadspace clicks')
    click(vm_index, 10, 300, clicks=15, interval=1)

    # if not on clash main, retunr False
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(
            "Not on clash main at start of collect_daily_bonus(). Returning False"
        )
        return False

    return True


def collect_weekly_bonus(vm_index, logger: Logger) -> bool:
    # if not on clash main, retunr False
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(
            "Not on clash main at start of collect_weekly_bonus(). Returning False"
        )
        return False

    # open daily rewards menu
    click(vm_index, 41, 206)
    time.sleep(2)

    # click the weekly bonus reward
    click(vm_index, 197, 500)
    logger.change_status("Collected weekly reward chest")
    logger.add_daily_reward()
    time.sleep(1)

    # click deadspace a bunch
    click(vm_index, 15, 300, clicks=15, interval=0.33)

    # if not on clash main, retunr False
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(
            "Not on clash main at start of collect_weekly_bonus(). Returning False"
        )
        return False

    return True


def check_if_daily_rewards_button_exists(vm_index) -> bool:
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[181][17],
        iar[210][48],
        iar[200][36],
        iar[195][26],
        iar[205][63],
        iar[215][45],
        iar[226][31],
        iar[216][55],
        iar[236][66],
    ]

    colors = [
        [111, 75, 13],
        [136, 90, 23],
        [129, 91, 20],
        [118, 84, 16],
        [152, 102, 33],
        [132, 88, 21],
        [136, 96, 25],
        [147, 98, 27],
        [158, 101, 33],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=35):
            return True

    return False


def check_for_green_checkmark(vm_index) -> bool:
    """ Check if the green checkmark is present indicating all rewards have been collected. """
    iar = numpy.asarray(screenshot(vm_index))
    checkmark_pixels = [
        (46, 195, [56, 236, 91]),
        (52, 199, [54, 235, 89]),
        (58, 194, [52, 235, 87])
    ]
    for x, y, color in checkmark_pixels:
        if not pixel_is_equal(iar[y][x], color, tol=15):
            return False
    return True


def check_for_yellow_button(vm_index) -> bool:
    """ Check if the daily rewards button is yellow indicating rewards are available. """
    iar = numpy.asarray(screenshot(vm_index))
    yellow_button_pixels = [
        (42, 185, [70, 217, 255]),
        (32, 192, [37, 170, 226]),
        (16, 209, [35, 180, 238])
    ]
    for x, y, color in yellow_button_pixels:
        if not pixel_is_equal(iar[y][x], color, tol=15):
            return False
    return True


def collect_all_daily_rewards(vm_index, logger):
    # if not on clash main, reutrn False
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(
            "Not on clash main at start of collect_daily_rewards(). Returning False"
        )
        return False

    # if daily rewards button doesnt exist, reutnr True
    if not check_if_daily_rewards_button_exists(vm_index):
        logger.change_status("Daily rewards button doesn't exist")
        return True

    # Check for green checkmark
    if check_for_green_checkmark(vm_index):
        logger.change_status("All rewards have already been collected")
        return True

    # Check for yellow button
    if not check_for_yellow_button(vm_index):
        logger.change_status("No rewards to collect")
        return True

    # check which rewards are available
    rewards = check_which_rewards_are_available(vm_index, logger)
    time.sleep(1)

    # collect the basic 3 daily rewards for completing tasks
    if rewards[0] or rewards[1] or rewards[2]:
        if collect_challenge_rewards(vm_index, logger, rewards) is False:
            logger.change_status("Failed to collect challenge rewards")
            return False

    # collect the daily bonus reward if it exists
    if rewards[3] and collect_daily_bonus(vm_index, logger) is False:
        logger.change_status("Failed to collect daily bonus reward")
        return False

    # collect the weekly bonus reward if it exists
    if rewards[4] and collect_weekly_bonus(vm_index, logger) is False:
        logger.change_status("Failed to collect weekly bonus reward")
        return False

    return True


def check_which_rewards_are_available(vm_index, logger):
    logger.change_status("Checking which daily rewards are available")

    # if not on clash main, return False
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(
            "Not on clash main before check_which_rewards_are_available() "
        )
        return False

    # open daily rewards menu
    click(vm_index, 41, 206)
    time.sleep(2)

    # check which rewards are available
    rewards = check_rewards_menu_pixels(vm_index)

    # click deadspace a bunch
    click(vm_index, 15, 290, clicks=3, interval=0.33)
    time.sleep(2)

    # if not on clash main, return False
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(
            "Not on clash main after check_which_rewards_are_available()"
        )
        return False

    positives = 0
    for _ in rewards:
        if _:
            positives += 1

    print(f"There are {positives} to collect")
    return rewards


def check_rewards_menu_pixels(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    pixels = [
        iar[206][117],
        iar[273][112],
        iar[341][115],
        iar[413][233],
        iar[530][216],
    ]

    colors = [
        [181, 211, 229],
        [182, 212, 230],
        [181, 211, 229],
        [224, 132, 29],
        [113, 156, 0],
    ]

    bool_list = []
    for i, p in enumerate(pixels):
        # print(p)
        this_bool = pixel_is_equal(p, colors[i], 5)
        bool_list.append(not this_bool)

    return bool_list


if __name__ == "__main__":
    bs = check_rewards_menu_pixels(12)
    for b in bs:
        print(b)
