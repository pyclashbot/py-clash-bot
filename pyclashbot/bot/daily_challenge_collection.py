import time

import numpy

from pyclashbot.bot.nav import check_if_on_clash_main_menu
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.memu.client import click, screenshot
from pyclashbot.utils.logger import Logger

CLASH_MAIN_DEADSPACE_COORD = (240, 600)
CLASH_MAIN_DEADSPACE_COLOR = [255, 175, 78]


def collect_daily_rewards_state(vm_index, logger, next_state):
    # First check if all rewards have already been collected
    if check_if_rewards_collected(vm_index):
        logger.change_status("All daily rewards have been collected")
        return next_state

    if not collect_all_daily_rewards(vm_index, logger):
        logger.change_status("Failed to collect daily rewards")
        return "restart"

    return next_state


def check_if_rewards_collected(vm_index) -> bool:
    iar = numpy.asarray(screenshot(vm_index))
    checkmark_pixels = [
        (65, 187, [87, 247, 121]),
        (60, 191, [58, 238, 93]),
        (57, 196, [57, 236, 92]),
        (52, 199, [54, 234, 88]),
        (45, 195, [51, 231, 85]),
    ]

    # Check each specified pixel for the checkmark
    for x, y, expected_color in checkmark_pixels:
        # If a pixel does not match, the checkmark is not present
        if not pixel_is_equal(iar[y][x], expected_color, tol=10):
            return False

    # If all pixels match, the checkmark is present
    return True


def collect_challenge_rewards(vm_index, logger: Logger, rewards) -> bool:
    # Ensure we are on the main menu of Clash
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            "Not on clash main at start of collect_challenge_rewards(). Returning False",
        )
        return False

    # Open the daily rewards menu
    click(vm_index, 41, 206)
    time.sleep(2)

    # Collect rewards
    # Click positions to collect the rewards
    reward_positions = [(209, 310), (209, 427), (209, 540)]
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

            # Close reward confirmation pop-ups
            if i < 2:  # For first two rewards
                click(vm_index, 10, 450, clicks=10, interval=1)
                # Reopen the rewards menu only if necessary
                if i < len(rewards) - 1 and rewards[i + 1]:
                    click(vm_index, 41, 206)
                    time.sleep(2)
            else:  # For the "lucky drop" reward
                click(vm_index, 15, 450, clicks=15, interval=0.33)
                time.sleep(2)

    # Return to main menu by clicking close button
    iar = numpy.asarray(screenshot(vm_index))
    x, y = CLASH_MAIN_DEADSPACE_COORD
    expected_color = CLASH_MAIN_DEADSPACE_COLOR
    actual_color = iar[y][x]

    if pixel_is_equal(actual_color, expected_color, tol=35):
        logger.change_status("Closing reward menu")
        click(vm_index, x, y, clicks=1)
        time.sleep(2)
    else:
        logger.change_status(f"close button color mismatch at ({x},{y}) ")
        return False

    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            "Not on clash main after collect_challenge_rewards(). Returning False",
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


def collect_all_daily_rewards(vm_index, logger) -> bool:
    if not check_if_on_clash_main_menu(vm_index):
        logger.change_status(
            "Not on clash main at start of collect_daily_rewards(). Returning False",
        )
        return False

    if not check_if_daily_rewards_button_exists(vm_index):
        logger.change_status(
            "Daily rewards button doesn't exist. Assuming rewards already collected or not available.",
        )
        return True

    rewards = check_which_rewards_are_available(vm_index, logger)
    if rewards is False:
        logger.change_status("Error checking which rewards are available")
        return False

    if not any(rewards):
        logger.change_status("No daily rewards available to collect")
        return True

    rewardspage = check_rewards_menu_pixels(vm_index)

    if not any(rewardspage):
        logger.change_status("No daily rewards found")
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
                "Not on clash main before check_which_rewards_are_available() ",
            )

    # open daily rewards menu
    click(vm_index, 41, 206)
    time.sleep(2)

    # check which rewards are available
    rewards = check_rewards_menu_pixels(vm_index)

    time.sleep(2)

    # Return to main menu by clicking close button
    iar = numpy.asarray(screenshot(vm_index))
    x, y = CLASH_MAIN_DEADSPACE_COORD
    expected_color = CLASH_MAIN_DEADSPACE_COLOR
    actual_color = iar[y][x]

    if pixel_is_equal(actual_color, expected_color, tol=35):
        logger.change_status("Closing reward menu")
        click(vm_index, x, y, clicks=1)
        time.sleep(2)
    else:
        logger.change_status(f"close buttton color mismatch at ({x},{y}) ")
        return False

    # if not on clash main, return False
    if check_if_on_clash_main_menu(vm_index) is not True:
        logger.change_status(
            "Not on clash main after check_which_rewards_are_available()",
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

    pixel_coords = [
        (200, 323),
        (200, 465),
        (200, 544),
    ]

    expected_color = [44, 188, 255]
    rewards_available = []

    for i, (x, y) in enumerate(pixel_coords):
        actual_color = iar[y][x]
        match = pixel_is_equal(actual_color, expected_color, tol=35)
        rewards_available.append(match)

    return rewards_available


if __name__ == "__main__":
    bs = check_rewards_menu_pixels(12)
    for b in bs:
        print(b)
