import numpy
import time

from pyclashbot.bot.nav import (
    check_if_on_clash_main_menu,
    get_to_card_page_from_clash_main,
    wait_for_clash_main_menu,
)
from pyclashbot.detection.image_rec import (
    check_line_for_color,
    region_is_color,
    make_reference_image_list,
    get_file_count,
    find_references,
    get_first_location,
    pixel_is_equal,
)
from pyclashbot.memu.client import click, screenshot
from pyclashbot.utils.logger import Logger


def find_and_click_button_by_image(vm_index, folder_name):
    """
    Finds and clicks on a button based on image recognition.

    Args:
        vm_index (int): The index of the virtual machine.
        folder_name (str): The name of the folder containing reference images for the button.
    """
    # Create a list of reference image names from the folder
    names = make_reference_image_list(get_file_count(folder_name))

    # Find references in the screenshot
    locations = find_references(
        screenshot(vm_index),
        folder_name,
        names,
        tolerance=0.85,  # Adjust the tolerance as needed to improve accuracy
    )

    # Get the first location of the detected reference
    coord = get_first_location(locations)

    if coord is None:
        return False
    else:
        # Click on the detected button location
        click(vm_index, coord[1], coord[0])
        time.sleep(2)
        return True


def is_boosted_section_present(vm_index):
    """
    Checks if the 'boosted' section line is present by verifying specific pixels' color.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if the 'boosted' section is present, False otherwise.
    """
    # Convert screenshot to numpy array
    iar = numpy.asarray(screenshot(vm_index))

    # Target color for the 'boosted' section line
    target_color = (255, 171, 239)

    # Coordinates to check for the target color
    check_coords = [(100, 441), (312, 441)]

    # Check each coordinate for the target color
    for x, y in check_coords:
        # Get the pixel color at the specified coordinate
        pixel_color = iar[y][x]

        # Check if the pixel color matches the target color
        if not pixel_is_equal(target_color, pixel_color, tol=30):
            return False

    # If both coordinates have the target color, return True
    return True


def detect_arrow_color(vm_index: int, card_index: int, y_positions: list[int]) -> str:
    """
    Detect the color of the arrow on a card based on predefined pixel positions and colors.

    Args:
        vm_index (int): The index of the virtual machine.
        card_index (int): The index of the card (1-4).
        y_positions (list[int]): Y positions for color checks.

    Returns:
        str: The color of the arrow ('green', 'blue', 'yellow', or 'unknown').
    """
    # Convert screenshot to numpy array
    iar = numpy.asarray(screenshot(vm_index))

    # Base positions for the first point of the arrow on each card
    base_x_positions = [46, 133, 219, 306]  # X positions for card 1 to 4

    # Adjusted base X position for the specific card
    base_x = base_x_positions[card_index - 1]

    # Color checks for green, blue, and yellow arrows
    color_checks = {
        "green": [(86, 255, 11), (80, 246, 8)],
        "blue": [(255, 211, 0), (255, 181, 0)],
        "yellow": [(60, 232, 255), (35, 223, 255)],
    }

    # Iterate through each color to check the predefined pixels
    for color, rgb_values in color_checks.items():
        color_match = True
        for i, rgb in enumerate(rgb_values):
            # Adjusted position for the check
            if i < len(y_positions):  # Ensure we don't go out of bounds
                pixel = iar[y_positions[i]][base_x + 5]
                if not pixel_is_equal(rgb, pixel, tol=50):
                    color_match = False
                    break
        if color_match:
            return color

    return "unknown"


def detect_elixir_logo(vm_index: int) -> bool:
    """
    Detect if the elixir logo is present on the screen by checking a specific pixel color.

    Args:
        vm_index (int): The index of the virtual machine.

    Returns:
        bool: True if the elixir logo color is detected, False otherwise.
    """
    # Convert screenshot to numpy array
    iar = numpy.asarray(screenshot(vm_index))

    # Elixir logo color and position
    elixir_color = (195, 10, 202)
    elixir_pos = (40, 520)

    # Get the pixel color from the screenshot at the specified position
    pixel_color = iar[elixir_pos[1]][elixir_pos[0]]

    # Check if the pixel color matches the elixir color within the tolerance
    if pixel_is_equal(elixir_color, pixel_color, tol=40):
        return True
    else:
        return False


def reset_ui_state(vm_index):
    """
    Resets the UI state by clicking on an empty space multiple times.

    Args:
        vm_index (int): The index of the virtual machine.
    """
    for _ in range(5):  # Click five times to ensure the UI is reset
        click(vm_index, 21, 415)
        time.sleep(0.5)


def handle_tower_troops(vm_index, logger: Logger):
    """
    Handles the detection and upgrade of Tower Troops cards if a green arrow is detected,
    restarting the detection from the first card after every successful upgrade. The UI
    is reset if the process needs to skip a card.

    Args:
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object to use for logging.
    """
    # Define Y positions for arrow color checks on Tower Troops cards
    y_positions_tower_troops = [348, 353]

    # Coordinates to click on the Tower Troops cards and the upgrade button
    tower_troops_card_click_coords = [(80, 293), (165, 293), (254, 293)]
    tower_troops_upgrade_button_coords = [(80, 362), (165, 362), (254, 362)]

    upgraded = True
    while upgraded:
        upgraded = False  # Reset upgrade flag for each cycle
        for card_index in range(1, 4):  # Iterate through the 3 Tower Troops cards
            color = detect_arrow_color(vm_index, card_index, y_positions_tower_troops)
            if color == "green":
                logger.change_status(
                    status=f"Detected green arrow for Tower Troops card {card_index}. Upgrading..."
                )
                click(vm_index, *tower_troops_card_click_coords[card_index - 1])
                time.sleep(2)

                click(vm_index, *tower_troops_upgrade_button_coords[card_index - 1])
                time.sleep(2)

                if not find_and_click_button_by_image(vm_index, "upgrade_button"):
                    logger.change_status(
                        "Failed to find the second upgrade button. Skipping this card."
                    )
                    reset_ui_state(vm_index)
                    continue  # Move to the next card

                if check_for_missing_gold_popup(vm_index):
                    logger.change_status(
                        "Missing gold popup exists. Skipping this upgradable card."
                    )
                    reset_ui_state(vm_index)
                    continue  # Move to the next card

                if not find_and_click_button_by_image(vm_index, "confirm_button"):
                    logger.change_status(
                        "Failed to find the confirm button. Upgrade may not have been completed."
                    )
                    reset_ui_state(vm_index)
                    continue  # Move to the next card

                # Successfully upgraded a card
                upgraded = True
                prev_card_upgrades = logger.get_card_upgrades()
                logger.add_card_upgraded()
                card_upgrades = logger.get_card_upgrades()
                logger.log(
                    f"Incremented cards upgraded from {prev_card_upgrades} to {card_upgrades}"
                )
                logger.change_status("Successfully upgraded the card")

                reset_ui_state(vm_index)
                break  # Restart detection from the first card


def detect_and_upgrade(vm_index, logger, y_positions):
    """
    Detects, upgrades, and redetects colors if a card was upgraded.

    Args:
        vm_index (int): The index of the virtual machine.
        logger (Logger): The logger object for logging messages.
        y_positions (list[int]): Y positions for color checks.
    """
    while True:
        upgraded_this_cycle = False
        for card_index in range(1, 5):  # Assuming card_index goes from 1 to 4
            color = detect_arrow_color(vm_index, card_index, y_positions)
            if color == "green":
                logger.log(f"Upgrading card {card_index} with green arrow.")
                if upgrade_card(vm_index, logger, card_index):
                    upgraded_this_cycle = True
                    break  # Restart detection from the first card if an upgrade was made
        if not upgraded_this_cycle:
            break  # Exit loop if no cards were upgraded in this cycle


def upgrade_all_cards_state(vm_index, logger: Logger, next_state):
    logger.change_status(status="Upgrade cards state")
    logger.add_card_upgrade_attempt()

    # If not on clash main, return restart
    clash_main_check = check_if_on_clash_main_menu(vm_index)
    if clash_main_check is not True:
        logger.change_status("Not on clash main at the start of upgrade_cards_state()")
        logger.log("These are the pixels the bot saw after failing to find clash main:")
        for pixel in clash_main_check:
            logger.log(f"   {pixel}")
        return "restart"

    # Get to card page
    logger.change_status(status="Getting to card page")
    if get_to_card_page_from_clash_main(vm_index, logger) == "restart":
        logger.change_status(
            status="Error 0751389 Failure getting to card page from clash main in Upgrade State"
        )
        return "restart"

    # Click the collection button
    logger.change_status(status="Clicking the collection button")
    click(vm_index, 290, 69)
    logger.log("Clicked on the collection button to view all cards.")
    time.sleep(2)

    handle_tower_troops(vm_index, logger)
    time.sleep(1)
    if is_boosted_section_present(vm_index):
        # If the "Boosted" section is present
        logger.change_status("Navigating to the 'Boosted' section of the cards.")
        click(vm_index, 80, 520)  # Click to reach the "Boosted" section
        time.sleep(1)
        click(vm_index, 21, 415)  # Click empty space
        time.sleep(1)

        detect_and_upgrade(vm_index, logger, [465, 471])

        # Then navigate to the "Found" section of the cards
        logger.change_status("Navigating to the 'Found' section of the cards.")
        click(vm_index, 166, 561)  # Click to reach the "Found" section
        time.sleep(1)
        click(vm_index, 21, 415)  # Click empty space
        time.sleep(1)

        detect_and_upgrade(vm_index, logger, [465, 471])

    else:
        # If the "Boosted" section is not present, directly navigate to the "Found" section
        logger.change_status("Navigating to the 'Found' section of the cards.")
        # Adjust if necessary to correctly target the "Found" section directly
        click(vm_index, 80, 520)
        time.sleep(1)
        click(vm_index, 21, 415)  # Click empty space
        time.sleep(1)

        detect_and_upgrade(vm_index, logger, [465, 471])

    # Repeat detection and actions if the elixir logo is present
    while detect_elixir_logo(vm_index):
        logger.log("Next line")
        click(vm_index, 80, 550)  # Move to the next line of cards
        time.sleep(1)
        click(vm_index, 21, 415)  # Click empty space
        time.sleep(1)

        # Re-detect and upgrade after moving to the next line
        detect_and_upgrade(vm_index, logger, [465, 471])

    # Click on empty space before returning to clash main
    for _ in range(5):
        click(vm_index, 21, 415)
        time.sleep(0.5)

    # Return to clash main
    logger.change_status("Returning to clash main")
    click(vm_index, 243, 600)
    time.sleep(3)

    # Wait for main
    if wait_for_clash_main_menu(vm_index, logger, deadspace_click=False) is False:
        logger.change_status("Failed to wait for clash main after upgrading cards")
        return "restart"

    logger.update_time_of_last_card_upgrade(time.time())
    return next_state


def upgrade_card(vm_index, logger: Logger, card_index):
    """
    Upgrades a card with a green arrow detected, ensuring not to proceed if a gold missing popup appears.

    Args:
        vm_index (int): The index of the virtual machine to perform the upgrade on.
        logger (Logger): The logger object to use for logging.
        card_index (int): The index of the card to upgrade, starting from 1.

    Returns:
        None
    """
    logger.change_status(status=f"Upgrading card index: {card_index}")

    # Coordinates for clicking on the card and the first upgrade button
    card_click_coords = [(81, 412), (164, 412), (252, 412), (339, 412)]
    upgrade_button_coords = [(81, 482), (164, 482), (252, 482), (339, 482)]

    # Click on the card
    click(vm_index, *card_click_coords[card_index - 1])
    time.sleep(2)

    # Click on the Upgrade button
    click(vm_index, *upgrade_button_coords[card_index - 1])
    time.sleep(2)

    # Use find_and_click_second_upgrade_button to find and click the second Upgrade button
    if not find_and_click_button_by_image(vm_index, "upgrade_button"):
        logger.log("Failed to find the second upgrade button. Skipping this card.")
        # Click on empty space to ensure the UI is not stuck in an unexpected state
        reset_ui_state(vm_index)
        return False

    # Check for the presence of the "missing gold" popup before confirming the upgrade
    if check_for_missing_gold_popup(vm_index):
        logger.log("Missing gold popup exists. Skipping this upgradable card.")
        # Click on empty space to close the popup and return
        reset_ui_state(vm_index)
        return False

    # Use find_and_click_confirm_button to find and click the Confirm button
    if not find_and_click_button_by_image(vm_index, "confirm_button"):
        logger.log(
            "Failed to find the confirm button. Upgrade may not have been completed."
        )
        return False

    # Click on empty space to close the upgrade window
    reset_ui_state(vm_index)

    # Update the logger for the successful upgrade
    prev_card_upgrades = logger.get_card_upgrades()
    logger.add_card_upgraded()
    card_upgrades = logger.get_card_upgrades()
    logger.log(
        f"Incremented cards upgraded from {prev_card_upgrades} to {card_upgrades}"
    )
    logger.change_status("Successfully upgraded the card")
    return True


def check_for_missing_gold_popup(vm_index):
    if not check_line_for_color(
        vm_index, x_1=338, y_1=215, x_2=361, y_2=221, color=(153, 20, 17)
    ):
        return False
    if not check_line_for_color(
        vm_index, x_1=124, y_1=201, x_2=135, y_2=212, color=(255, 255, 255)
    ):
        return False

    if not check_line_for_color(vm_index, 224, 368, 236, 416, (56, 228, 72)):
        return False

    if not region_is_color(vm_index, [70, 330, 60, 70], (227, 238, 243)):
        return False

    return True


if __name__ == "__main__":
    click(12, 209, 466)
