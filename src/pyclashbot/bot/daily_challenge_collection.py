from pyclashbot.bot.nav import check_if_on_clash_main_menu
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.utils.logger import Logger
import numpy
from pyclashbot.memu.client import screenshot, click
import time


def collect_daily_rewards_state(vm_index, logger, next_state):
    if not collect_all_daily_rewards(vm_index, logger):
        logger.change_status("Failed to collect daily rewards")
        return "restart"

    return next_state


def collect_challenge_rewards(vm_index, logger, rewards) -> bool:
    # Ensure we are on the main menu of Clash
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            "Not on clash main at start of collect_challenge_rewards(). Returning False")
        return False

    # Open the daily rewards menu
    click(vm_index, 41, 206)
    time.sleep(2)

    # Collect rewards
    # Click positions to collect the rewards
    reward_positions = [(114, 235), (210, 235), (308, 235)]
    reward_messages = [
        "Collected 1st daily challenge reward",
        "Collected 2nd daily challenge reward",
        "Collected lucky drop challenge reward",
    ]

    for i, (x, y) in enumerate(reward_positions):
        if rewards[i]:
            click(vm_index, x, y)
            logger.change_status(reward_messages[i])
            logger.add_daily_reward()
            time.sleep(1)

            # Reopen the daily rewards menu if it's not the last button
            if i < 2:
                # Click in the empty space to close menus/pop-ups
                click(vm_index, 10, 450, clicks=5, interval=1)
                click(vm_index, 41, 206)
                time.sleep(2)
            else:
                # Additional clicks in the empty space for the lucky drop
                click(vm_index, 15, 450, clicks=15, interval=0.33)

    # Check again if we are on the main menu
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            "Not on clash main after collect_challenge_rewards(). Returning False")
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


def collect_all_daily_rewards(vm_index, logger) -> bool:
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            "Not on clash main at start of collect_daily_rewards(). Returning False")
        return False

    if not check_if_daily_rewards_button_exists(vm_index):
        logger.change_status(
            "Daily rewards button doesn't exist. Assuming rewards already collected or not available.")
        return True

    rewards = check_which_rewards_are_available(vm_index, logger)
    if rewards is False:
        logger.change_status("Error checking which rewards are available")
        return False

    if not any(rewards):
        logger.change_status("No daily rewards available to collect")
        return True

    if not collect_challenge_rewards(vm_index, logger, rewards):
        logger.change_status("Failed to collect challenge rewards")
        return False

    return True


def check_which_rewards_are_available(vm_index, logger):
    logger.change_status("Checking which daily rewards are available")

    # if not on clash main, return False
    if check_if_on_clash_main_menu(vm_index) is not True:
        time.sleep(3)
        if check_if_on_clash_main_menu(vm_index) is not True:
            logger.change_status(
                "Not on clash main before check_which_rewards_are_available() "
            )

    # open daily rewards menu
    click(vm_index, 41, 206)
    time.sleep(2)

    # check which rewards are available
    rewards = check_rewards_menu_pixels(vm_index)

    # click deadspace a bunch
    click(vm_index, 15, 450, clicks=3, interval=0.33)
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
        iar[180][88],  # Position for button 1
        iar[180][186],  # Position for button 2
        iar[180][280],  # Position for button 3 (lucky drop)
    ]

    expected_color = [65, 209, 49]

    rewards_available = [pixel_is_equal(
        pixel, expected_color, tol=35) for pixel in pixels]
    return rewards_available


if __name__ == "__main__":
    bs = check_rewards_menu_pixels(12)
    for b in bs:
        print(b)
