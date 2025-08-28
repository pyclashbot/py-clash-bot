import random
import time
from typing import Literal

from pyclashbot.detection.image_rec import (
    all_pixels_are_equal,
    find_image,
    pixel_is_equal,
)
from pyclashbot.utils.logger import Logger

CLASH_MAIN_OPTIONS_BURGER_BUTTON = (390, 62)
BATTLE_LOG_BUTTON = (241, 43)
CARD_PAGE_ICON_FROM_CLASH_MAIN = (108, 598)
CARD_PAGE_ICON_FROM_CARD_PAGE = (147, 598)
OK_BUTTON_COORDS_IN_TROPHY_REWARD_PAGE = (209, 599)
CLASH_MAIN_MENU_DEADSPACE_COORD = (32, 520)
CLASH_MAIN_WAIT_TIMEOUT = 240  # s


def wait_for_battle_start(emulator, logger, timeout: int = 120) -> bool:
    """Wait for battle to start with periodic deadspace clicking."""
    start_time = time.time()

    while time.time() - start_time < timeout:
        elapsed = time.time() - start_time
        logger.change_status(f"Waiting for battle ({elapsed:.1f}s)")

        if check_if_in_battle(emulator):
            logger.change_status("Battle started!")
            return True

        emulator.click(20, 200)  # Deadspace click
        time.sleep(1)

    return False


def check_for_in_battle_with_delay(emulator) -> bool:
    """Check if in battle with 3-second sampling delay."""
    timeout = 3
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if check_if_in_battle(emulator):
            return True
        time.sleep(0.1)  # Small delay between checks
    
    return False


def check_if_in_battle(emulator):
    """Check if currently in a battle (1v1 or 2v2) using UI indicators."""
    screenshot = emulator.screenshot()
    
    # Test patterns for both battle types
    battle_patterns = {
        "1v1": {
            "pixels": [(515, 49), (518, 77), (530, 52), (530, 77), (618, 115)],
            "colors": [[255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [232, 63, 242]]
        },
        "2v2": {
            "pixels": [(515, 53), (518, 80), (531, 52), (514, 76), (615, 114)],
            "colors": [[255, 255, 255], [255, 255, 255], [255, 255, 255], [255, 255, 255], [231, 57, 242]]
        }
    }
    
    # Check each battle type pattern
    for battle_type, pattern in battle_patterns.items():
        pixels = [screenshot[y][x] for y, x in pattern["pixels"]]
        if all_pixels_are_equal(pattern["colors"], pixels, tol=35):
            return True
    
    return False


def check_for_trophy_reward_menu(emulator) -> bool:
    """Check if trophy reward menu is visible using color pattern matching."""
    screenshot = emulator.screenshot()
    
    # Trophy reward UI detection points and expected colors
    test_points = [(592, 172), (617, 180), (607, 190), (603, 200), (596, 210), 
                   (593, 220), (600, 230), (610, 235), (623, 246)]
    expected_colors = [[255, 184, 68], [255, 175, 78], [255, 175, 78], [248, 239, 227],
                      [255, 187, 104], [255, 176, 79], [255, 187, 104], [255, 175, 78], [253, 135, 39]]
    
    for (y, x), expected_color in zip(test_points, expected_colors):
        if not pixel_is_equal(screenshot[y][x], expected_color, tol=25):
            return False
    
    return True


def handle_trophy_reward_menu(
    emulator,
    logger: Logger,
    printmode=False,
) -> Literal["good"]:
    if printmode:
        logger.change_status(status="Handling trophy reward menu")
    else:
        logger.log("Handling trophy reward menu")
    emulator.click(
        OK_BUTTON_COORDS_IN_TROPHY_REWARD_PAGE[0],
        OK_BUTTON_COORDS_IN_TROPHY_REWARD_PAGE[1],
    )
    time.sleep(1)

    return "good"


def wait_for_clash_main_menu(emulator, logger: Logger, deadspace_click=True) -> bool:
    """Wait for main menu, handling popups and timeouts."""
    start_time = time.time()
    
    while not check_if_on_clash_main_menu(emulator):
        # Check timeout
        if time.time() - start_time > CLASH_MAIN_WAIT_TIMEOUT:
            logger.change_status("Timeout waiting for main menu")
            return False

        # Handle trophy reward popup
        if check_for_trophy_reward_menu(emulator):
            handle_trophy_reward_menu(emulator, logger)
            time.sleep(2)
            continue

        # Random deadspace clicking to clear popups
        if deadspace_click and random.randint(0, 1) == 0:
            emulator.click(*CLASH_MAIN_MENU_DEADSPACE_COORD)
        
        time.sleep(1)
    
    return True


def check_if_on_clash_main_menu(emulator) -> bool:
    """Check if on main menu using emulator-specific color patterns."""
    screenshot = emulator.screenshot()
    
    # Test pixel locations
    test_points = [(14, 209), (14, 325), (19, 298), (17, 399), (581, 261), (584, 166), (621, 166)]
    pixels = [screenshot[y][x] for y, x in test_points]
    
    # Color patterns for different emulators
    emulator_patterns = [
        [[255, 255, 255], [255, 255, 255], [53, 199, 233], [25, 198, 65], 
         [138, 105, 71], [139, 105, 72], [155, 120, 82]],  # Google Play
        [[255, 255, 255], [255, 255, 255], [53, 200, 233], [24, 199, 65], 
         [138, 105, 71], [139, 105, 72], [155, 120, 81]]   # Memu
    ]
    
    # Check if pixels match any emulator pattern
    return any(all_pixels_are_equal(pixels, pattern, 25) for pattern in emulator_patterns)


def get_to_card_page_from_clash_main(emulator, logger: Logger) -> Literal["restart", "good"]:
    """Navigate from main menu to card page with timeout."""
    logger.change_status("Navigating to card page")
    start_time = time.time()
    timeout = 30
    
    # Initial click to card page
    emulator.click(*CARD_PAGE_ICON_FROM_CLASH_MAIN)
    time.sleep(2.5)
    
    # Keep clicking until we reach card page or timeout
    while not check_if_on_card_page(emulator):
        if time.time() - start_time > timeout:
            return "restart"
        
        emulator.click(*CARD_PAGE_ICON_FROM_CARD_PAGE)
        time.sleep(3)
    
    logger.change_status("Reached card page")
    return "good"


def check_if_on_card_page(emulator) -> bool:
    """Check if currently on the card page using UI color patterns."""
    screenshot = emulator.screenshot()
    
    # Sample key UI pixels
    test_points = [(433, 58), (116, 59), (58, 82), (64, 179), 
                   (62, 108), (67, 146), (77, 185), (77, 84)]
    pixels = [screenshot[y][x] for y, x in test_points]
    
    # Two possible color patterns for card page
    patterns = [
        [[222, 0, 235], [255, 255, 255], [203, 137, 44], [195, 126, 34],
         [255, 255, 255], [255, 255, 255], [177, 103, 15], [178, 104, 15]],
        [[220, 0, 234], [255, 255, 255], [209, 68, 41], [202, 64, 41],
         [255, 255, 255], [255, 255, 255], [185, 52, 41], [185, 52, 41]]
    ]
    
    return any(all_pixels_are_equal(pixels, pattern, tol=25) for pattern in patterns)


def get_to_activity_log(emulator, logger: Logger, printmode: bool = False) -> Literal["restart", "good"]:
    """Navigate to activity log from main menu."""
    log_func = logger.change_status if printmode else logger.log
    log_func("Navigating to activity log")
    
    # Verify we're on main menu
    if not check_if_on_clash_main_menu(emulator):
        logger.change_status("Not on main menu, cannot access activity log")
        return "restart"
    
    # Open options menu
    log_func("Opening options menu")
    emulator.click(*CLASH_MAIN_OPTIONS_BURGER_BUTTON)
    
    if wait_for_clash_main_burger_button_options_menu(emulator, logger) == "restart":
        logger.change_status("Failed to open options menu")
        return "restart"
    
    # Click battle log
    log_func("Opening battle log")
    emulator.click(*BATTLE_LOG_BUTTON)
    
    if wait_for_battle_log_page(emulator, logger, printmode) == "restart":
        logger.change_status("Failed to open battle log")
        return "restart"
    
    return "good"


def wait_for_battle_log_page(
    emulator,
    logger: Logger,
    printmode=False,
) -> Literal["restart", "good"]:
    start_time = time.time()
    if printmode:
        logger.change_status(status="Waiting for battle log page to appear")
    else:
        logger.log("Waiting for battle log page to appear")
    while not check_if_on_battle_log_page(emulator):
        time_taken = time.time() - start_time
        if time_taken > 20:
            logger.change_status(
                status="Error 2457245645 Waiting too long for battle log page",
            )
            return "restart"

    if printmode:
        logger.change_status(status="Done waiting for battle log page to appear")
    else:
        logger.log("Done waiting for battle log page to appear")

    return "good"


def check_if_on_battle_log_page(emulator) -> bool:
    iar = emulator.screenshot()

    pixels = [
        iar[72][160],
        iar[71][187],
        iar[71][197],
        iar[72][231],
        iar[73][258],
        iar[64][366],
        iar[79][365],
        iar[70][365],
        iar[62][92],
        iar[77][316],
    ]
    colors = [
        [255, 255, 255],
        [255, 255, 255],
        [255, 255, 255],
        [255, 255, 255],
        [255, 255, 255],
        [147, 135, 254],
        [38, 38, 240],
        [255, 255, 255],
        [138, 122, 115],
        [124, 106, 99],
    ]

    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=25):
            return False
    return True


def check_if_on_clash_main_burger_button_options_menu(emulator) -> bool:
    iar = emulator.screenshot()
    pixels = [
        iar[42][256],
        iar[41][275],
        iar[41][282],
        iar[42][293],
        iar[44][325],
        iar[32][239],
        iar[34][336],
        iar[50][248],
        iar[49][336],
    ]
    colors = [
        [255, 255, 255],
        [255, 255, 255],
        [255, 255, 255],
        [255, 255, 254],
        [255, 255, 255],
        [255, 187, 105],
        [255, 187, 105],
        [255, 175, 78],
        [255, 175, 78],
    ]
    for i, color in enumerate(colors):
        if not pixel_is_equal(pixels[i], color, tol=25):
            return False
    return True


def wait_for_clash_main_burger_button_options_menu(
    emulator,
    logger: Logger,
    printmode: bool = False,
) -> Literal["restart", "good"]:
    """Waits for the virtual machine to be on the clash main burger button options menu.

    Args:
    ----
        emulator (int): The index of the virtual machine.
        logger (Logger): The logger object to use for logging.
        printmode (bool, optional): Whether to print status messages. Defaults to False.

    Returns:
    -------
        Literal["restart", "good"]: "restart" if the function timed
        out and needs to be restarted, "good" otherwise.

    """
    start_time = time.time()

    if printmode:
        logger.change_status(status="Waiting for clash main options menu to appear")
    else:
        logger.log("Waiting for clash main options menu to appear")
    while not check_if_on_clash_main_burger_button_options_menu(emulator):
        time_taken = time.time() - start_time
        if time_taken > 20:
            logger.change_status(
                status="Error 57245645362 Waiting too long for clash main options menu to appear",
            )
            return "restart"
    if printmode:
        logger.change_status(
            status="Done waiting for clash main options menu to appear",
        )
    else:
        logger.log("Done waiting for clash main options menu to appear")
    return "good"


def find_fight_mode_icon(emulator, mode: str):
    expected_mode_types = ["Classic 1v1", "Classic 2v2", "Trophy Road"]

    # Check if the mode is valid
    if mode not in expected_mode_types:
        print(f'[!] Fatal error: Mode "{mode}" is not a valid mode type. Expected one of {expected_mode_types}.')
        return None

    mode2folder = {
        "Classic 1v1": "fight_mode_1v1",
        "Classic 2v2": "fight_mode_2v2",
        "Trophy Road": "fight_mode_trophy_road",
    }

    look_folder = mode2folder[mode]

    image = emulator.screenshot()

    # os.makedirs('select_mode_images', exist_ok=True)
    # file_name = f'{random.randint(0,100000)}.png'
    # file_path = os.path.join('select_mode_images', file_name)
    # cv2.imwrite(file_path, image)

    fight_mode_1v1_button_location = find_image(
        image,
        look_folder,
        tolerance=0.85,
        subcrop=(27, 158, 206, 582),
        show_image=False,
    )
    if fight_mode_1v1_button_location is not None:
        return fight_mode_1v1_button_location
    return None


def select_mode(emulator, mode: str):
    # Check if the mode is valid
    expected_mode_types = ["Classic 1v1", "Classic 2v2", "Trophy Road"]
    if type(mode) is not str:
        print(f'[!] Warning: Mode "{mode}" is not a string. Expected a string.')
        return False

    # Check if the mode is valid
    if mode not in expected_mode_types:
        print(f'[!] Warning: Mode "{mode}" is not a valid mode type. Expected one of {expected_mode_types}.')
        return False

    # must be on clash main
    if not check_if_on_clash_main_menu(emulator):
        print("[!] Not on clash main menu, cannot select a fight mode")
        return False

    # open fight type selection menu
    game_mode_coord = [308, 485]

    # click select mode button
    print("Clicking mode selection button")
    emulator.click(game_mode_coord[0], game_mode_coord[1])
    time.sleep(2)

    def scroll_down_in_fight_mode_panel(emulator):
        start_y = 400
        end_y = 350
        x = 400
        emulator.swipe(x, start_y, x, end_y)
        time.sleep(1)

    # scroll and search, until we find the mode in question
    search_timeout = 15  # s
    while time.time() < time.time() + search_timeout:
        coord = find_fight_mode_icon(emulator, mode)
        if coord is not None:
            print(f'Located the "{mode}" button, clicking it.')
            emulator.click(*coord)
            time.sleep(3)
            return True

        scroll_down_in_fight_mode_panel(emulator)

    return False


if __name__ == "__main__":
    pass
