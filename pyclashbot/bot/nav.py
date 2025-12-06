import random
import time
from typing import Literal

from pyclashbot.detection.image_rec import (
    all_pixels_are_equal,
    find_image,
    pixel_is_equal,
)
from pyclashbot.utils.cancellation import interruptible_sleep
from pyclashbot.utils.logger import Logger

CLASH_MAIN_OPTIONS_BURGER_BUTTON = (390, 62)
BATTLE_LOG_BUTTON = (241, 43)
CARD_PAGE_ICON_FROM_CLASH_MAIN = (108, 598)
CARD_PAGE_ICON_FROM_CARD_PAGE = (147, 598)
OK_BUTTON_COORDS_IN_TROPHY_REWARD_PAGE = (209, 599)
CLASH_MAIN_MENU_DEADSPACE_COORD = (32, 520)
CLASH_MAIN_WAIT_TIMEOUT = 240  # s


def wait_for_battle_start(emulator, logger, timeout: int = 120) -> bool:
    """Waits for any battle to start (1v1 or 2v2).

    Args:
    ----
        emulator: The emulator controller.
        logger: The logger object.
        timeout: Maximum time to wait in seconds

    Returns:
    -------
        bool: True if battle started, False if timed out.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        time_taken = str(time.time() - start_time)[:4]
        logger.change_status(
            status=f"Waiting for battle to start for {time_taken}s",
        )

        # NOTE: Debug screenshot saving was intentionally removed from
        # the production flow. If you need screenshots for debugging,
        # use the recorder helpers directly in a temporary script or
        # enable a local-only change — do not commit such changes.

        battle_result = check_if_in_battle(emulator)

        if battle_result:  # True for any battle type
            logger.change_status("Detected an ongoing battle!")
            return True

        emulator.click(x_coord=20, y_coord=200)

    return False


def check_for_in_battle_with_delay(emulator) -> bool:
    """Checks if the virtual machine is in any battle with a delay.

    Args:
    ----
        emulator: The emulator controller.

    Returns:
    -------
        bool: True if the virtual machine is in any battle, False otherwise.

    """
    timeout = 3  # s
    start_time = time.time()
    while time.time() - start_time < timeout:
        battle_result = check_if_in_battle(emulator)
        if battle_result:  # True for any battle type ("1v1", "2v2")
            return True
    return False


def check_if_in_battle(emulator):
    iar_bgr = emulator.screenshot()
    if iar_bgr is None:
        return False

    # Convert to RGB for easier reasoning about expected colors.
    iar = iar_bgr[..., ::-1]

    def get_pixel(y: int, x: int) -> list[int] | None:
        if y >= iar.shape[0] or x >= iar.shape[1]:
            return None
        return iar[y][x].tolist()

    def is_bright(pixel: list[int] | None, threshold: int = 180) -> bool:
        return pixel is not None and all(channel >= threshold for channel in pixel)

    def is_scoreboard_purple(pixel: list[int] | None) -> bool:
        if pixel is None:
            return False
        r, g, b = pixel
        return r >= 200 and b >= 200 and g <= 140

    def check_mode(coords: list[tuple[int, int]]) -> bool:
        pixels = [get_pixel(y, x) for y, x in coords]
        bright_required = len(coords) - 1
        bright_count = sum(1 for pixel in pixels[:-1] if is_bright(pixel))
        return bright_count >= bright_required and is_scoreboard_purple(pixels[-1])

    coords_1v1 = [(528, 49), (532, 77), (546, 52), (546, 77), (618, 115)]
    coords_2v2 = [(534, 53), (533, 80), (548, 52), (548, 76), (615, 114)]

    if check_mode(coords_1v1):
        return True
    if check_mode(coords_2v2):
        return True

    return False


def check_for_trophy_reward_menu(emulator) -> bool:
    iar = emulator.screenshot()

    pixels = [
        iar[592][172],
        iar[617][180],
        iar[607][190],
        iar[603][200],
        iar[596][210],
        iar[593][220],
        iar[600][230],
        iar[610][235],
        iar[623][246],
    ]
    colors = [
        [255, 184, 68],
        [255, 175, 78],
        [255, 175, 78],
        [248, 239, 227],
        [255, 187, 104],
        [255, 176, 79],
        [255, 187, 104],
        [255, 175, 78],
        [253, 135, 39],
    ]

    for i, pixel in enumerate(pixels):
        if not pixel_is_equal(pixel, colors[i], tol=25):
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
    interruptible_sleep(1)

    return "good"


def wait_for_clash_main_menu(emulator, logger: Logger, deadspace_click=True) -> bool:
    """Waits for the user to be on the clash main menu.
    Returns True if on main menu, prints the pixels if False then return False
    """
    start_time: float = time.time()
    while check_if_on_clash_main_menu(emulator) is not True:
        # timeout check
        if time.time() - start_time > CLASH_MAIN_WAIT_TIMEOUT:
            logger.change_status("Timed out waiting for clash main")
            break

        # handle geting stuck on trophy road screen
        if check_for_trophy_reward_menu(emulator):
            print("Handling trophy reward menu")
            handle_trophy_reward_menu(emulator, logger)
            interruptible_sleep(2)
            continue

        # click deadspace
        if deadspace_click and random.randint(0, 1) == 0:
            emulator.click(
                CLASH_MAIN_MENU_DEADSPACE_COORD[0],
                CLASH_MAIN_MENU_DEADSPACE_COORD[1],
            )
        interruptible_sleep(1)

    interruptible_sleep(1)
    if check_if_on_clash_main_menu(emulator) is not True:
        print("Failed to get to clash main! Saw these pixels before restarting:")
        return False

    return True


def check_if_on_clash_main_menu(emulator) -> bool:
    """Checks if the user is on the clash main menu.
    Returns True if on main menu, False if not.
    """
    image = emulator.screenshot()
    pixels = [
        image[14][209],  # white
        image[14][325],  # white
        image[19][298],  # yellow
        image[17][399],  # green
        image[581][261],  # green
        image[584][166],  # bluegrey
        image[621][166],  # bluegrey
    ]

    # google play colors
    colors_1 = [
        [255, 255, 255],
        [255, 255, 255],
        [53, 199, 233],
        [25, 198, 65],
        [138, 105, 71],
        [139, 105, 72],
        [155, 120, 82],
    ]

    # memu colors
    colors_2 = [
        [255, 255, 255],
        [255, 255, 255],
        [53, 200, 233],
        [24, 199, 65],
        [138, 105, 71],
        [139, 105, 72],
        [155, 120, 81],
    ]

    # print("{:^15} | {:^15} | {:^15}".format("Seen", "Google", "Memu"))
    # for seen_pixel, google_play_color, memu_color in zip(pixels, colors_1, colors_2):
    #     seen_pixel =str(seen_pixel[0])+ ' '+ str(seen_pixel[1])+ ' '+ str(seen_pixel[2])
    #     google_play_color = (
    #         str(google_play_color[0]) + ' ' +
    #         str(google_play_color[1]) + ' ' +
    #         str(google_play_color[2])
    #     )
    #     memu_color = str(memu_color[0]) + ' ' + str(memu_color[1]) + ' ' + str(memu_color[2])
    #     print(
    #         "{:^15} | {:^15} | {:^15}".format(seen_pixel, google_play_color, memu_color)
    #     )

    for colors in [colors_1, colors_2]:
        if all_pixels_are_equal(
            pixels,
            colors,
            25,
        ):
            return True

    return False


def get_to_card_page_from_clash_main(
    emulator,
    logger: Logger,
) -> Literal["restart", "good"]:
    start_time = time.time()

    logger.change_status(status="Getting to card page from clash main")

    # click card page icon
    emulator.click(
        CARD_PAGE_ICON_FROM_CLASH_MAIN[0],
        CARD_PAGE_ICON_FROM_CLASH_MAIN[1],
    )
    interruptible_sleep(2.5)

    # while not on the card page, cycle the card page
    while not check_if_on_card_page(emulator):
        time_taken = time.time() - start_time
        if time_taken > 30:
            return "restart"

        emulator.click(
            CARD_PAGE_ICON_FROM_CARD_PAGE[0],
            CARD_PAGE_ICON_FROM_CARD_PAGE[1],
        )
        interruptible_sleep(3)

    logger.change_status(status="Made it to card page")

    return "good"


def check_if_on_card_page(emulator) -> bool:
    iar = emulator.screenshot()

    pixels = [
        iar[433][58],
        iar[116][59],
        iar[58][82],
        iar[64][179],
        iar[62][108],
        iar[67][146],
        iar[77][185],
        iar[77][84],
    ]

    colors1 = [
        [222, 0, 235],
        [255, 255, 255],
        [203, 137, 44],
        [195, 126, 34],
        [255, 255, 255],
        [255, 255, 255],
        [177, 103, 15],
        [178, 104, 15],
    ]

    colors2 = [
        [220, 0, 234],
        [255, 255, 255],
        [209, 68, 41],
        [202, 64, 41],
        [255, 255, 255],
        [255, 255, 255],
        [185, 52, 41],
        [185, 52, 41],
    ]

    def pixel_to_string(pixel):
        return f"[{pixel[0]},{pixel[1]},{pixel[2]}],"

    # print("{:^17} {:^17} {:^17}".format("pixel", "color1", "color2"))
    # for pixel, color1, color2 in zip(pixels, colors1, colors2):
    #     print(
    #         "{:^17} {:^17} {:^17}".format(
    #             pixel_to_string(pixel), pixel_to_string(color1), pixel_to_string(color2)
    #         )
    #     )

    if all_pixels_are_equal(pixels, colors1, tol=25):
        return True

    if all_pixels_are_equal(pixels, colors2, tol=25):
        return True

    return False


def get_to_activity_log(
    emulator,
    logger: Logger,
    printmode: bool = False,
) -> Literal["restart", "good"]:
    if printmode:
        logger.change_status(status="Getting to activity log")
    else:
        logger.log("Getting to activity log")

    # if not on main return restart
    if check_if_on_clash_main_menu(emulator) is not True:
        logger.change_status(
            status="Eror 08752389 Not on clash main menu, restarting vm",
        )
        return "restart"

    # click clash main burger options button
    if printmode:
        logger.change_status(status="Opening clash main options menu")
    else:
        logger.log("Opening clash main options menu")
    emulator.click(
        CLASH_MAIN_OPTIONS_BURGER_BUTTON[0],
        CLASH_MAIN_OPTIONS_BURGER_BUTTON[1],
    )
    if wait_for_clash_main_burger_button_options_menu(emulator, logger) == "restart":
        logger.change_status(
            status="Error 99993 Waited too long for clash main options menu, restarting vm",
        )
        return "restart"

    # click battle log button
    if printmode:
        logger.change_status(status="Clicking activity log button")
    else:
        logger.log("Clicking activity log button")
    emulator.click(BATTLE_LOG_BUTTON[0], BATTLE_LOG_BUTTON[1])
    if wait_for_battle_log_page(emulator, logger, printmode) == "restart":
        logger.change_status(
            status="Error 923593 Waited too long for battle log page, restarting vm",
        )
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


def check_if_battle_mode_is_selected(emulator, mode: str):
    """Checks if the given battle mode is selected on the clash main menu.

    Args:
        emulator: The emulator controller.
        mode: The battle mode to check for.

    Returns:
        True if the mode is selected, False otherwise.
    """
    expected_mode_types = ["Classic 1v1", "Classic 2v2", "Trophy Road"]

    # Check if the mode is valid
    if mode not in expected_mode_types:
        print(f'[!] Fatal error: Mode "{mode}" is not a valid mode type. Expected one of {expected_mode_types}.')
        return None

    mode2folder = {
        "Classic 1v1": "selected_1v1_on_main",
        "Classic 2v2": "selected_2v2_on_main",
        "Trophy Road": "selected_trophy_road_on_main",
    }

    look_folder = mode2folder[mode]

    print(f"[DEBUG] Checking if {mode} is selected...")
    print(f"[DEBUG] Looking in folder: {look_folder}")
    print("[DEBUG] Subcrop: (270, 455, 350, 533)")

    # find image on screen
    coord = find_image(
        emulator.screenshot(),
        look_folder,
        tolerance=0.9,
        subcrop=(270, 455, 350, 533),
    )

    print(f"[DEBUG] Found at: {coord}")

    return coord is not None


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
        tolerance=0.9,
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
    interruptible_sleep(2)

    def scroll_down_in_fight_mode_panel(emulator):
        start_y = 400
        end_y = 350
        x = 400
        emulator.swipe(x, start_y, x, end_y)
        interruptible_sleep(1)

    # scroll and search, until we find the mode in question
    search_timeout = 15  # s
    start_time = time.time()

    # Use a fixed start time so we actually time out correctly instead of
    # comparing two moving time.time() values (which would never time out).
    while time.time() - start_time < search_timeout:
        coord = find_fight_mode_icon(emulator, mode)
        if coord is not None:
            print(f'Located the "{mode}" button, clicking it.')
            emulator.click(*coord)
            interruptible_sleep(3)

            # After choosing a mode, the mode panel may remain open on some
            # devices/emulators. Click a safe deadspace coord to ensure the
            # selection panel closes and the main menu is active again so
            # subsequent actions (like pressing Start) work reliably.
            try:
                emulator.click(CLASH_MAIN_MENU_DEADSPACE_COORD[0], CLASH_MAIN_MENU_DEADSPACE_COORD[1])
            except Exception:
                # Don't fail if the click doesn't work; best-effort only.
                pass

            return True

        scroll_down_in_fight_mode_panel(emulator)

    return False


if __name__ == "__main__":
    # from pyclashbot.emulators.memu import MemuEmulatorController
    # from pyclashbot.utils.logger import Logger
    # import cv2
    # import os

    # print("Creating logger...")
    # logger = Logger()

    # print("Creating MEmu emulator controller in DEBUG mode (no restart)...")
    # emulator = MemuEmulatorController(logger, render_mode="directx", debug_mode=True)

    # # Save a screenshot for debugging
    # print("\nSaving screenshot for debugging...")
    # os.makedirs("debug_screenshots", exist_ok=True)
    # screenshot = emulator.screenshot()
    # cv2.imwrite("debug_screenshots/current_screen.png", screenshot)
    # print(f"Screenshot saved to: debug_screenshots/current_screen.png")
    # print(f"Screenshot size: {screenshot.shape}")

    # print("\nTesting find_fight_mode_icon...")
    # x = check_if_battle_mode_is_selected(emulator, "Classic 2v2")
    # print(f"Result: Is Classic 2v2 selected? {x}")

    # select_mode(emulator, "Classic 1v1")

    # here matt if you want to test this and see debug info
    pass
