import time
import numpy

from pyclashbot.bot.nav import wait_for_clash_main_menu, check_if_on_path_of_legends_clash_main
from pyclashbot.bot.do_fight_state import check_both_1v1_modes_available
from pyclashbot.detection.image_rec import (
    pixel_is_equal,
)
from pyclashbot.memu.client import click, screenshot, scroll_up
from pyclashbot.utils.logger import Logger


def collect_bannerbox_rewards_state(vm_index: int, logger: Logger, next_state: str):
    """
    Attempts to collect Path of Legends rewards if available.

    Args:
        vm_index (int): Index of the virtual machine.
        logger (Logger): Logger instance for logging.
        next_state (str): The next state to transition to after attempting to collect rewards.

    Returns:
        str: The next state or "restart" if it fails to navigate or collect rewards.
    """
    # Check if already in the Clash main menu.
    if not wait_for_clash_main_menu(vm_index, logger):
        logger.change_status("Not in Clash main menu")
        return "restart"

    # Detect if both 1v1 modes are available, implying Path of Legends is accessible.
    if check_both_1v1_modes_available(vm_index):
        logger.change_status("Detected both 1v1 modes.")

        # Attempt to navigate to Path of Legends if not already there.
        if check_if_on_path_of_legends_clash_main(vm_index) != True:
            logger.change_status(
                "Not in Path of Legends, attempting to switch...")
            click(vm_index, 277, 400)
            time.sleep(2)  # Wait for UI to update.

            if check_if_on_path_of_legends_clash_main(vm_index) != True:
                logger.change_status("Failed to navigate to Path of Legends")
                return "restart"

        rewards_collected_result = 0
        # Collect rewards as long as Path of Legends rewards are detected.
        if check_for_path_of_legends_rewards(vm_index):
            logger.change_status(
                "Path of Legends rewards detected. Attempting to collect...")
            path_of_legends_state, rewards_collected = collect_path_of_legends_rewards(
                vm_index, logger)
            if not path_of_legends_state:
                logger.change_status(
                    "Failed to collect Path of Legends rewards.")
                return "restart"
            else:
                rewards_collected_result += rewards_collected

        if rewards_collected_result == 0:
            logger.change_status("No Path of Legends rewards detected.")
            time.sleep(2)
        else:
            logger.change_status(
                f"{rewards_collected_result} Path of Legends rewards collected.")
            time.sleep(2)
        return next_state
    else:
        logger.change_status("Path of Legends mode not available")
        time.sleep(2)
        return next_state


def check_for_path_of_legends_rewards(vm_index):
    """
    Checks if Path of Legends rewards are available by looking for specific pixel colors.
    If the expected colors are found, it indicates
    that there are unclaimed rewards.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if Trophy Road rewards are available, False otherwise.
    """
    # Take a screenshot and convert to a numpy array for pixel access.
    iar = numpy.asarray(screenshot(vm_index))

    # Coordinates and expected colors for the Path of Legends rewards indicator.
    # Multiple colors are checked to accommodate different visual states.
    pixels_and_colors = [
        # Color for possibly one state of the reward indicator.
        ((236, 326), (59, 199, 255)),
        # Another possible color for the reward indicator.
        ((236, 326), (82, 226, 255)),
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


def collect_path_of_legends_rewards(vm_index, logger):
    """
    Tries to collect Path of Legends rewards by opening the Path of Legends rewards menu
    and claiming available rewards. It handles both scenarios: being an Ultimate Champion and not.

    Args:
        vm_index (int): Index of the virtual machine.
        logger (Logger): Logger object for status updates.

    Returns:
        Tuple[bool, int]: Tuple indicating whether the collection was successful and the number of rewards collected.
    """
    rewards_collected = 0
    # Attempt to open the Path of Legends rewards menu.
    click(vm_index, 210, 250)
    time.sleep(2)  # Wait a bit for the menu to open.

    if check_if_on_path_of_legends_rewards_menu(vm_index):
        logger.change_status(
            "Successfully entered the Path of Legends rewards menu.")
        time.sleep(1.5)

        def claim_rewards_sequence():
            nonlocal rewards_collected
            button = find_claim_rewards_buttons(vm_index)
            print(f"{button}")
            while button:
                logger.change_status("Claiming reward...")
                # Click on the found "Claim Rewards" button.
                click(vm_index, *button)
                time.sleep(1)  # Allow time for reward claim animation.
                collecting_attempts = 0
                while not check_if_on_path_of_legends_rewards_menu(vm_index) and collecting_attempts < 30:
                    # Click on deadspace to ensure staying in the menu.
                    click(vm_index, 20, 395)
                    time.sleep(0.5)
                    collecting_attempts += 1
                    if collecting_attempts >= 30:
                        logger.change_status(
                            "Excessive collection attempts; returning False.")
                        return False
                logger.add_bannerbox_collect()
                rewards_collected += 1
                time.sleep(1.5)
                # Re-check for more buttons after each claim.
                button = find_claim_rewards_buttons(vm_index)
            return True

        if check_if_ultimate_champion(vm_index):
            logger.change_status(
                "Identified as Ultimate Champion; bypassing crown search.")
            while not check_last_door(vm_index):
                if not claim_rewards_sequence():
                    return False, rewards_collected
                logger.change_status("Scrolling to look for more rewards...")
                scroll_up(vm_index)
                time.sleep(2)
        else:
            while not (check_current_step(vm_index) or check_last_door(vm_index)):
                if not claim_rewards_sequence():
                    return False, rewards_collected
                logger.change_status("Scrolling to look for more rewards...")
                scroll_up(vm_index)
                time.sleep(2)

        logger.change_status("Reached the end of rewards.")
        click(vm_index, 210, 606)  # Click to go back to the main menu.
        time.sleep(2)

        if wait_for_clash_main_menu(vm_index, logger):
            logger.change_status(
                "Successfully returned to Clash main menu after collecting rewards.")
            return True, rewards_collected
        else:
            logger.change_status("Failed to return to Clash main menu.")
            return False, rewards_collected
    else:
        logger.change_status(
            "Failed to enter the Path of Legends rewards menu.")
        return False, rewards_collected


def check_last_door(vm_index):
    """
    Checks for the last door in Path of Legends by looking for a specific group of pixels,
    indicating the door's position. This method checks for a fixed pattern of colors that
    may shift vertically but stay grouped together.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if the door's pixel group is detected, False otherwise.
    """
    iar = numpy.asarray(screenshot(vm_index))
    screen_height = iar.shape[0]  # Height of the screen

    # Define a baseline Y coordinate and the relative positions and colors
    baseline_y = 141
    pixel_offsets_and_colors = [
        ((16, 0), (82, 170, 253)),
        ((32, 0), (91, 0, 55)),
        ((48, 0), (73, 148, 240)),
        ((66, 0), (91, 0, 55)),
        ((80, 0), (84, 171, 253)),
        ((337, 0), (86, 173, 253)),
        ((369, 0), (72, 150, 243)),
        ((388, 0), (91, 0, 55)),
        ((31, 12), (206, 230, 246)),
        ((63, 22), (234, 213, 225)),
        ((210, 47), (118, 119, 147)),
        ((217, -53), (255, 238, 255)),
        ((201, -45), (220, 56, 197)),
        ((198, -41), (92, 29, 74)),
    ]
    tolerance = 35

    # For each Y position from the top of the screen to the bottom,
    # check if the group of pixels matches the pattern at any vertical position
    for y_shift in range(screen_height - baseline_y):
        all_match = True
        for (x_offset, y_offset), expected_color in pixel_offsets_and_colors:
            # Calculate actual position based on the current Y shift
            x = x_offset
            y = baseline_y + y_shift + y_offset
            if y >= screen_height:
                continue  # Skip if the calculated Y position is outside the screen

            pixel_color = iar[y, x]
            if not pixel_is_equal(pixel_color, expected_color, tolerance):
                all_match = False
                break  # Stop checking this group if any pixel doesn't match

        if all_match:
            return True  # Return True if all pixels in the group match

    return False  # Return False if the door's pixel group wasn't found anywhere


def find_claim_rewards_buttons(vm_index):
    """
    Searches for the lowest "Claim Rewards" button in Path of Legends by scanning the entire screen
    for a specific pattern of colors. This approach allows for vertical variations in the button's position.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        tuple[int, int] | None: The coordinates of the lowest "Claim Rewards" button found, or None if not found.
    """
    iar = numpy.asarray(screenshot(vm_index))
    screen_height = iar.shape[0]  # Height of the screen

    # Define the relative positions and colors for the "Claim Rewards" button pattern
    color_offsets_and_patterns = [
        ((373, 30), (48, 209, 255)),  # Light Blue
        ((373, 13), (71, 222, 56)),   # Green
        ((373, 37), (24, 165, 231)),  # Blue
        ((373, 0), (88, 205, 72)),    # Light Green
    ]
    tolerance = 55

    # Initialize a list to keep track of found button Y positions
    found_button_ys = []

    # Scan from top to bottom of the screen to match the entire pattern
    for y in range(screen_height):
        match_count = 0
        for (x_offset, y_offset), expected_color in color_offsets_and_patterns:
            actual_y = y + y_offset
            if actual_y < 0 or actual_y >= screen_height:
                continue  # Skip if the adjusted Y is outside the screen bounds
            pixel_color = iar[actual_y, x_offset]
            if pixel_is_equal(pixel_color, expected_color, tolerance):
                match_count += 1
        if match_count == len(color_offsets_and_patterns):
            found_button_ys.append(y)  # Add this Y position to the list

    # Find the lowest Y position from the found buttons, if any
    if found_button_ys:
        # Adjust for actual button position
        lowest_button_y = max(found_button_ys) + 60
        return (346, lowest_button_y)  # Return the adjusted coordinates

    return None  # Return None if no button was found


def check_current_step(vm_index):
    """
    Checks for the presence of specific crown colors in Path of Legends, indicating the current step.
    This function scans from top to bottom of the screen to accommodate vertical variations in crown position.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if the sequence of crown colors is detected, False otherwise.
    """
    iar = numpy.asarray(screenshot(vm_index))
    screen_height = iar.shape[0]  # Height of the screen

    # Define the X coordinates and expected colors for the crown sequence
    crown_colors_positions = [
        (209, (230, 151, 38)),  # Gold
        (209, (236, 32, 194)),  # Pink
        (209, (0, 146, 209)),   # Blue
        (245, (223, 28, 182)),  # Purple
        (211, (175, 5, 156))    # Darker Pink
    ]
    tolerance = 35

    # Function to check if a specific color is found at the given X coordinate and any Y within the screen height
    def color_found_at_x(x, expected_color):
        for y in range(screen_height):
            pixel_color = iar[y, x]
            if pixel_is_equal(pixel_color, expected_color, tolerance):
                return True
        return False

    # Check each color in the sequence. If any color is not found, return False.
    for x, expected_color in crown_colors_positions:
        if not color_found_at_x(x, expected_color):
            return False

    # If all colors are found in their respective X coordinates, return True
    return True


def check_if_ultimate_champion(vm_index):
    """
    Checks if the user has reached the Ultimate Champion tier in Path of Legends
    by examining specific pixel colors on the screen.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: False if detected pixel colors match, True otherwise.
    """
    # Capture the current screen of the VM as a numpy array.
    iar = numpy.asarray(screenshot(vm_index))

    # Define the pixel positions and their expected colors.
    pixels_positions_and_colors = [
        ((312, 555), (215, 55, 132)),
        ((379, 555), (214, 54, 131)),
        ((345, 559), (20, 174, 225)),
        ((345, 543), (245, 217, 217)),
    ]

    # Check each specified pixel against its expected color.
    for (x, y), expected_color in pixels_positions_and_colors:
        pixel_color = iar[y][x]  # Access the color at (Y, X).
        # Check for color match with a tolerance of 35.
        if pixel_is_equal(pixel_color, expected_color, tol=35):
            # If any pixel matches, the user is not an Ultimate Champion.
            return False

    # If no pixels match, the user is an Ultimate Champion.
    return True


def check_if_on_path_of_legends_rewards_menu(vm_index):
    """
    Checks if the current screen is the Path of Legends rewards menu based on specific pixel colors.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if the current screen is the Path of Legends rewards menu, False otherwise.
    """
    # Capture the current screen of the VM as a numpy array.
    iar = numpy.asarray(screenshot(vm_index))

    # Define the pixel positions and their expected colors.
    pixels_positions_and_colors = [
        ((40, 620), (107, 86, 73)),
        ((400, 620), (107, 86, 72)),
        ((180, 600), (255, 187, 104)),
        ((240, 619), (255, 175, 78)),
        ((214, 607), (255, 255, 255)),
        ((73, 534), (25, 109, 159)),
        ((48, 521), (255, 234, 244)),
        ((73, 570), (217, 66, 140))
    ]

    # Iterate through each pixel position and check if the color matches the expected color with a tolerance of 35.
    for (x, y), expected_color in pixels_positions_and_colors:
        pixel_color = iar[y][x]  # Access the color in format (Y, X).
        if not pixel_is_equal(pixel_color, expected_color, tol=35):
            # Return False if any pixel does not match the expected color.
            return False

    # Return True if all pixels match their expected colors.
    return True


if __name__ == "__main__":
    pass
