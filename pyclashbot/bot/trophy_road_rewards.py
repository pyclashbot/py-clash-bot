import time

import numpy

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    check_if_on_path_of_legends_clash_main,
    wait_for_clash_main_menu,
)
from pyclashbot.detection.image_rec import (
    find_references,
    get_file_count,
    get_first_location,
    make_reference_image_list,
    pixel_is_equal,
)
from pyclashbot.utils.logger import Logger


def collect_trophy_road_rewards_state(vm_index: int, logger: Logger, next_state: str):
    # Verify if already in the clash main menu.
    if not wait_for_clash_main_menu(vm_index, logger):
        logger.change_status("Not in clash main menu")
        return "restart"

    # Check if in Path of Legends mode, attempting to navigate back to Trophy Road if so.
    if check_if_on_path_of_legends_clash_main(vm_index) is True:
        logger.change_status(
            "Detected Path of Legends, attempting to navigate back to Trophy Road...",
        )
        # Click on the specified coordinates to attempt to switch views.
        emulator.click(277, 400)
        time.sleep(2)  # Wait for the UI to possibly update.

        # Re-check if successfully navigated back to Trophy Road.
        if check_if_on_path_of_legends_clash_main(vm_index) is True:
            logger.change_status(
                "Failed to navigate back to Trophy Road from Path of Legends",
            )
            # Return "restart" if still in Path of Legends after clicking.
            return "restart"

    # Checks if Trophy Road rewards are available and attempts to collect them.
    while check_for_trophy_road_rewards(vm_index):
        logger.change_status("Trophy Road rewards detected. Attempting to collect...")
        trophy_road_state = collect_trophy_road_rewards(
            vm_index,
            logger,
        )

        if trophy_road_state is not True:
            logger.change_status("Failed to collect Trophy Road rewards.")
            return "restart"
        # Check if in Path of Legends mode, attempting to navigate back to Trophy Road if so.
        if check_if_on_path_of_legends_clash_main(vm_index) is True:
            logger.change_status(
                "Detected Path of Legends, attempting to navigate back to Trophy Road...",
            )
            # Click on the specified coordinates to attempt to switch views.
            emulator.click(277, 400)
            time.sleep(2)  # Wait for the UI to possibly update.

            # Re-check if successfully navigated back to Trophy Road.
            if check_if_on_path_of_legends_clash_main(vm_index) is True:
                logger.change_status(
                    "Failed to navigate back to Trophy Road from Path of Legends",
                )
                # Return "restart" if still in Path of Legends after clicking.
                return "restart"

    return next_state


def check_for_trophy_road_rewards(vm_index):
    """Checks if Trophy Road rewards are available by looking for specific pixel colors
    on the Trophy Road button. If the expected colors are found, it indicates
    that there are unclaimed rewards.

    Args:
    ----
        vm_index (int): The index of the virtual machine.

    Returns:
    -------
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


def collect_trophy_road_rewards(vm_index: int, logger: Logger):
    """Attempts to collect Trophy Road rewards by navigating to the Trophy Road rewards menu
    and claiming available rewards.

    Args:
    ----
        vm_index (int): The index of the virtual machine.
        logger (Logger): Logger for status updates.

    Returns:
    -------
        bool: True if rewards collection was successful or no rewards were available, False if an error occurred.

    """
    # if not on main return False
    if not check_if_on_clash_main_menu(emulator):
        logger.change_status(
            "Not on main to start collect_trophy_road_rewards()! Returning False"
        )
        return False

    deadspace_coord = [19, 502]

    def get_to_main_after_claim(vm_index):
        timeout = 30  # s
        start_time = time.time()
        while time.time() - start_time < timeout:
            if check_if_on_clash_main_menu(emulator):
                return True
            emulator.click(deadspace_coord[0], deadspace_coord[1])
            time.sleep(1)
        return False

    def specific_coord_click_claim_button(vm_index):
        # search for the button
        coord = find_trophy_road_reward_claim_button(vm_index)

        # if we got a button
        if coord is not None:
            # collect it
            emulator.click(coord[0], coord[1])
            # handle strikes appearing
            time.sleep(1)
            if strikes_detected(vm_index):
                emulator.click(210, 580)
                time.sleep(1)

            # back to main for next loop
            if get_to_main_after_claim(vm_index) is False:
                return False

            return True

        # if we didnt get a button
        return False

    def pixel_coord_click_claim_button(vm_index):
        # search for the button
        lrn = find_collect_button(vm_index)  # left,right,none

        # if we didnt get a button
        if lrn is None:
            return False

        # if left
        if lrn == "left":
            emulator.click(170, 337)
            # handle strikes appearing
            time.sleep(1)
            if strikes_detected(vm_index):
                emulator.click(210, 580)
                time.sleep(1)

        # else right
        else:
            emulator.click(307, 337)
            # handle strikes appearing
            time.sleep(1)
            if strikes_detected(vm_index):
                emulator.click(210, 580)
                time.sleep(1)

        # back to main
        if get_to_main_after_claim(vm_index) is False:
            return False

        # good collect loop
        return True

    # collect until there are no more rewards
    while 1:
        logger.change_status("Attempting to collect another reward!")

        # Open the Trophy Road rewards menu.
        emulator.click(210, 250)
        time.sleep(2)  # Wait for the menu to potentially open.
        if not check_if_on_trophy_road_rewards_menu(vm_index):
            logger.change_status("Failed to enter trophy road menu. Returning False")
            return False

        if specific_coord_click_claim_button(
            vm_index
        ) or pixel_coord_click_claim_button(vm_index):
            continue

        break


def find_collect_button(vm_index):
    """Checks the screen for the presence of a collect button on the Trophy Road rewards menu.
    It determines if the button is on the left or right side of the screen.

    Args:
    ----
        vm_index (int): The index of the virtual machine.

    Returns:
    -------
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
    # print('left_pixel_color',left_pixel_color)
    if any(
        pixel_is_equal(left_pixel_color, color, tol=35) for color in expected_colors
    ):
        # Return "left" if a matching color is found at the left position.
        return "left"

    # Check the right position for expected colors.
    right_pixel_color = iar[right_position[1]][right_position[0]]
    print("right_pixel_color", right_pixel_color)
    if any(
        pixel_is_equal(right_pixel_color, color, tol=35) for color in expected_colors
    ):
        # Return "right" if a matching color is found at the right position.
        return "right"

    return None  # Return None if no collect button is detected on either side.


def strikes_detected(vm_index) -> bool:
    """Checks if the screen indicates that strikes are detected during the Trophy Road rewards collection process.

    Args:
    ----
        vm_index (int): The index of the virtual machine.

    Returns:
    -------
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


def check_if_on_trophy_road_rewards_menu(vm_index) -> bool:
    """Checks if the current screen is the Trophy Road rewards menu based on specific pixel colors.

    Args:
    ----
        vm_index (int): The index of the virtual machine.

    Returns:
    -------
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


def find_trophy_road_reward_claim_button(vm_index, delay=2):
    def to_wrap():
        image = screenshot(vm_index)

        folder = "trophy_road_reward_claim_button"

        names = make_reference_image_list(get_file_count(folder))

        locations: list[list[int] | None] = find_references(
            image,
            folder,
            names,
            tolerance=0.88,
        )

        coord = get_first_location(locations)

        if coord is None:
            return None

        return [coord[1], coord[0]]

    timeout = delay
    start_time = time.time()
    while time.time() - start_time < timeout:
        coord = to_wrap()
        if coord is not None:
            return coord


if __name__ == "__main__":
    print("\n" * 50)

    c = find_trophy_road_reward_claim_button(1, 2)
