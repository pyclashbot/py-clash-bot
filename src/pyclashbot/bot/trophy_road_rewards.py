import time
import numpy
import random

from pyclashbot.bot.nav import wait_for_clash_main_menu, check_if_on_path_of_legends_clash_main, check_if_on_clash_main_menu
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.memu.client import click, screenshot
from pyclashbot.utils.logger import Logger


def collect_bannerbox_rewards_state(vm_index: int, logger: Logger, next_state: str):
    # Verify if already in the clash main menu.
    if not wait_for_clash_main_menu(vm_index, logger):
        logger.change_status("Not in clash main menu")
        return "restart"

    # Check if in Path of Legends mode, attempting to navigate back to Trophy Road if so.
    if check_if_on_path_of_legends_clash_main(vm_index) is True:
        logger.change_status(
            "Detected Path of Legends, attempting to navigate back to Trophy Road...")
        # Click on the specified coordinates to attempt to switch views.
        click(vm_index, 277, 400)
        time.sleep(2)  # Wait for the UI to possibly update.

        # Re-check if successfully navigated back to Trophy Road.
        if check_if_on_path_of_legends_clash_main(vm_index) is True:
            logger.change_status(
                "Failed to navigate back to Trophy Road from Path of Legends")
            # Return "restart" if still in Path of Legends after clicking.
            return "restart"
    rewards_collected_result = 0
    # Checks if Trophy Road rewards are available and attempts to collect them.
    while check_for_trophy_road_rewards(vm_index):
        logger.change_status(
            "Trophy Road rewards detected. Attempting to collect...")
        trophy_road_state, rewards_collected = collect_trophy_road_rewards(
            vm_index, logger)
        if trophy_road_state is not True:
            logger.change_status("Failed to collect Trophy Road rewards.")
            return "restart"
        rewards_collected_result += rewards_collected
        # Check if in Path of Legends mode, attempting to navigate back to Trophy Road if so.
        if check_if_on_path_of_legends_clash_main(vm_index) is True:
            logger.change_status(
                "Detected Path of Legends, attempting to navigate back to Trophy Road...")
            # Click on the specified coordinates to attempt to switch views.
            click(vm_index, 277, 400)
            time.sleep(2)  # Wait for the UI to possibly update.

            # Re-check if successfully navigated back to Trophy Road.
            if check_if_on_path_of_legends_clash_main(vm_index) is True:
                logger.change_status(
                    "Failed to navigate back to Trophy Road from Path of Legends")
                # Return "restart" if still in Path of Legends after clicking.
                return "restart"

    if rewards_collected_result == 0:
        logger.change_status("No Trophy Road rewards detected.")
    else:
        logger.change_status(
            f"{rewards_collected_result} Trophy Road rewards collected.")
    return next_state


def check_for_trophy_road_rewards(vm_index):
    """
    Checks if Trophy Road rewards are available by looking for specific pixel colors
    on the Trophy Road button. If the expected colors are found, it indicates
    that there are unclaimed rewards.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if Trophy Road rewards are available, False otherwise.
    """
    # Take a screenshot and convert to a numpy array for pixel access.
    iar = numpy.asarray(screenshot(vm_index))

    # Coordinates and expected colors for the Trophy Road rewards indicator.
    # Multiple colors are checked to accommodate different visual states.
    pixels_and_colors = [
        # Color for possibly one state of the reward indicator.
        ((279, 347), (58, 202, 255)),
        # Another possible color for the reward indicator.
        ((279, 347), (82, 226, 255)),
    ]

    # Check each specified pixel against its expected color.
    for (x, y), expected_color in pixels_and_colors:
        # Access the pixel from the image array.
        # Note: Numpy arrays use row-major order, so y comes before x.
        pixel = iar[y][x]

        # Check if the pixel color matches the expected color within a tolerance.
        if pixel_is_equal(pixel, expected_color, tol=35):
            return True  # Return True immediately if a match is found.

    # If none of the specified pixels match the expected colors, assume no rewards are available.
    return False


def collect_trophy_road_rewards(vm_index, logger):
    """
    Attempts to collect Trophy Road rewards by navigating to the Trophy Road rewards menu
    and claiming available rewards.

    Args:
        vm_index (int): The index of the virtual machine.
        logger (Logger): Logger for status updates.

    Returns:
        bool: True if rewards collection was successful or no rewards were available, False if an error occurred.
    """
    rewards_collected = 0
    # Click to potentially open the Trophy Road rewards menu.
    click(vm_index, 210, 250)
    time.sleep(2)  # Wait for the menu to potentially open.

    # Check if successfully entered the Trophy Road rewards menu.
    if check_if_on_trophy_road_rewards_menu(vm_index):
        logger.change_status("Successfully entered Trophy Road rewards menu.")
        time.sleep(2)

        # Loop until no more collect buttons are found or limit is reached
        while find_collect_button(vm_index) != None:
            collecting_attempts = 0
            collect_side = find_collect_button(vm_index)
            if collect_side == "left":
                click(vm_index, 170, 337)
            elif collect_side == "right":
                click(vm_index, 307, 337)
            logger.add_bannerbox_collect()
            rewards_collected += 1
            time.sleep(1)
            logger.change_status("Collecting rewards...")
            # Randomly click left or right to collect rewards et go back to trophy road rewards menu
            while not check_if_on_trophy_road_rewards_menu(vm_index) and collecting_attempts < 30:
                if random.randint(0, 1):
                    click(vm_index, 138, 186)  # Left
                else:
                    click(vm_index, 281, 186)  # Right
                time.sleep(0.5)
                click(vm_index, 391, 407)  # Deadspace
                time.sleep(1)
                collecting_attempts += 1
                if check_if_on_clash_main_menu(vm_index) is True:
                    ("Back to main menu.")
                    return True, rewards_collected
                if collecting_attempts >= 30:
                    logger.change_status("Collected too much.")
                    return False, rewards_collected
                if strikes_detected(vm_index) is True:
                    click(vm_index, 210, 580)
                    time.sleep(1)

        # Attempt to return to the main menu after collecting or attempting to collect rewards
        click(vm_index, 210, 608)
        if wait_for_clash_main_menu(vm_index, logger):
            logger.change_status(
                "Successfully returned to clash main menu after collecting rewards.")
            return True, rewards_collected
        else:
            logger.change_status(
                "Failed to return to clash main menu after collecting rewards.")
            return False, rewards_collected
    else:
        logger.change_status("Failed to enter Trophy Road rewards menu.")
        return False, rewards_collected


def find_collect_button(vm_index):
    """
    Checks the screen for the presence of a collect button on the Trophy Road rewards menu.
    It determines if the button is on the left or right side of the screen.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        str: "left" if the collect button is on the left side, "right" if on the right side, or None if not found.
    """
    # Capture the current screen of the VM as a numpy array.
    iar = numpy.asarray(screenshot(vm_index))

    # Define the positions to check for the collect button and their expected colors.
    left_position = (170, 347)
    right_position = (307, 347)
    # Both colors could indicate a collect button.
    expected_colors = [(113, 255, 98), (75, 230, 60)]

    # Check the left position for expected colors.
    left_pixel_color = iar[left_position[1]][left_position[0]]
    if any(pixel_is_equal(left_pixel_color, color, tol=35) for color in expected_colors):
        # Return "left" if a matching color is found at the left position.
        return "left"

    # Check the right position for expected colors.
    right_pixel_color = iar[right_position[1]][right_position[0]]
    if any(pixel_is_equal(right_pixel_color, color, tol=35) for color in expected_colors):
        # Return "right" if a matching color is found at the right position.
        return "right"

    return None  # Return None if no collect button is detected on either side.


def strikes_detected(vm_index):
    """
    Checks if the screen indicates that strikes are detected during the Trophy Road rewards collection process.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if strikes are detected on the screen, indicating a special condition or warning during reward collection. False otherwise.
    """
    # Capture the current screen of the VM as a numpy array.
    iar = numpy.asarray(screenshot(vm_index))

    # Define the pixel positions and their expected colors for detecting strikes.
    pixels_positions_and_colors = [
        ((112, 380), (165, 52, 119)),
        ((354, 522), (136, 38, 87)),
        ((349, 382), (43, 190, 255)),
        ((175, 574), (255, 187, 104)),
        ((245, 591), (255, 175, 78)),
    ]

    # Iterate through the defined pixels, checking if the actual colors match the expected ones within a tolerance.
    for position, expected_color in pixels_positions_and_colors:
        # Access the color in the format (Y, X) because numpy arrays use row-major order.
        pixel_color = iar[position[1]][position[0]]

        # Compare the pixel color with the expected color, allowing for a small variance.
        if pixel_is_equal(pixel_color, expected_color, tol=35):
            # If any of the specified pixels match the expected colors, return True.
            return True

    # If none of the specified pixels match the expected colors, assume no strikes are detected.
    return False


def check_if_on_trophy_road_rewards_menu(vm_index):
    """
    Checks if the current screen is the Trophy Road rewards menu based on specific pixel colors.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if the current screen is the Trophy Road rewards menu, False otherwise.
    """
    # Capture the current screen of the VM as a numpy array.
    iar = numpy.asarray(screenshot(vm_index))

    # Define the pixel positions and their expected colors.
    pixels_positions = [
        (40, 620),  # X: 40 Y: 620
        (400, 620),  # X: 400 Y: 620
        (180, 600),  # X: 180 Y: 600
        (240, 619),  # X: 240 Y: 619
        (214, 607),  # X: 214 Y: 607
    ]

    expected_colors = [
        (107, 86, 73),  # Corresponding to X: 40 Y: 620
        (107, 86, 72),  # Corresponding to X: 400 Y: 620
        (255, 187, 104),  # Corresponding to X: 180 Y: 600
        (255, 175, 78),  # Corresponding to X: 240 Y: 619
        (255, 255, 255),  # Corresponding to X: 214 Y: 607
    ]

    # Iterate through each pixel position and check if the color matches the expected color.
    for index, position in enumerate(pixels_positions):
        # Accessing the color in format (Y, X).
        pixel_color = iar[position[1]][position[0]]
        expected_color = expected_colors[index]

        # Use a function to compare the pixel color with the expected color with a tolerance.
        if not pixel_is_equal(pixel_color, expected_color, tol=35):
            return False  # If any pixel does not match, return False.

    # If all pixels match their expected colors, return True.
    return True


if __name__ == "__main__":
    pass
