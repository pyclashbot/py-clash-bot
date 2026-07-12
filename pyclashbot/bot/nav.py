import random
import time
from typing import Literal

from pyclashbot.bot.coords import (
    BATTLE_LOG_BUTTON,
    BATTLE_WAIT_DEADSPACE_COORD,
    BOTTOM_NAV_BATTLE_TAB_COORD,
    BOTTOM_NAV_CARD_TAB_COORD,
    BOTTOM_NAV_CARD_TAB_FROM_MAIN_COORD,
    BOTTOM_NAV_CARD_TAB_FROM_WAR_COORD,
    BOTTOM_NAV_CLAN_CHAT_TAB_COORD,
    BOTTOM_NAV_CLAN_CHAT_TAB_FROM_WAR_COORD,
    BOTTOM_NAV_MAIN_TAB_FROM_CARD_COORD,
    BOTTOM_NAV_MAIN_TAB_FROM_SHOP_COORD,
    BOTTOM_NAV_MAIN_TAB_FROM_WAR_COORD,
    BOTTOM_NAV_SHOP_TAB_COORD,
    BOTTOM_NAV_SHOP_TAB_FROM_WAR_COORD,
    BOTTOM_NAV_SOCIAL_TAB_COORD,
    CARD_PAGE_EXIT_BUTTON_COORDS,
    CARD_PAGE_ICON_FROM_CARD_PAGE,
    CARD_PAGE_ICON_FROM_CLASH_MAIN,
    CLAN_CHAT_EXIT_DEADSPACE_COORD,
    CLAN_CHAT_TO_SOCIAL_COORD,
    CLAN_VOYAGE_CLOSE_BUTTON_COORDS,
    CLAN_WAR_FINAL_RESULTS_POPUP_OK_BUTTON,
    CLASH_MAIN_OPTIONS_BURGER_BUTTON,
    DECK_TABS_REGION,
    DECKS_PAGE_BUTTON_COORDS,
    OK_BUTTON_COORDS_IN_TROPHY_REWARD_PAGE,
    WAR_BOOT_REWARD_COORD,
    WAR_EXIT_DEADSPACE_COORD,
    WAR_TAB_FROM_SOCIAL_COORD,
)
from pyclashbot.bot.coords import CLASH_MAIN_DEADSPACE_COORD as CLASH_MAIN_MENU_DEADSPACE_COORD
from pyclashbot.bot.find import find_fight_mode_icon, find_post_battle_button
from pyclashbot.bot.state_detect import (
    check_for_battle_days_started_popup,
    check_for_final_results_page,
    check_for_trophy_reward_menu,
    check_if_in_battle,
    check_if_on_battle_log_page,
    check_if_on_card_page,
    check_if_on_clan_chat,
    check_if_on_clan_voyage,
    check_if_on_clash_main_burger_button_options_menu,
    check_if_on_clash_main_menu,
    check_if_on_shop,
    check_if_on_social,
    check_if_on_war,
    check_if_on_war_boot,
)
from pyclashbot.detection.image_rec import find_image
from pyclashbot.utils.logger import Logger

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
    last_logged_second = -1
    while time.time() - start_time < timeout:
        elapsed_second = int(time.time() - start_time)
        if elapsed_second != last_logged_second:
            logger.change_status(
                status=f"Waiting for battle to start for {elapsed_second}s",
            )
            last_logged_second = elapsed_second

        # NOTE: Debug screenshot saving was intentionally removed from
        # the production flow. If you need screenshots for debugging,
        # use the recorder helpers directly in a temporary script or
        # enable a local-only change — do not commit such changes.

        battle_result = check_if_in_battle(emulator)

        if battle_result:  # True for any battle type
            logger.change_status("Battle detected")
            return True

        emulator.click(x_coord=BATTLE_WAIT_DEADSPACE_COORD[0], y_coord=BATTLE_WAIT_DEADSPACE_COORD[1])

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
        time.sleep(0.1)
    return False


def handle_trophy_reward_menu(
    emulator,
    logger: Logger,
    printmode=False,
) -> Literal["good"]:
    if printmode:
        logger.change_status(status="Handling trophy reward popup")
    else:
        logger.log("Handling trophy reward menu")
    emulator.click(
        OK_BUTTON_COORDS_IN_TROPHY_REWARD_PAGE[0],
        OK_BUTTON_COORDS_IN_TROPHY_REWARD_PAGE[1],
    )
    time.sleep(1)

    return "good"


def handle_clan_voyage_page(emulator) -> None:
    """Dismiss the clan voyage popup by clicking its close button."""
    emulator.click(*CLAN_VOYAGE_CLOSE_BUTTON_COORDS)


def wait_for_clash_main_menu(
    emulator,
    logger: Logger,
    deadspace_click=True,
    timeout: float | None = None,
) -> bool:
    """Waits for the user to be on the clash main menu.
    Returns True if on main menu, prints the pixels if False then return False
    """
    wait_timeout = CLASH_MAIN_WAIT_TIMEOUT if timeout is None else timeout
    start_time: float = time.time()
    while check_if_on_clash_main_menu(emulator) is not True:
        # timeout check
        if time.time() - start_time > wait_timeout:
            logger.change_status("Timed out waiting for main menu")
            break

        # handle geting stuck on trophy road screen
        if check_for_trophy_reward_menu(emulator):
            print("Handling trophy reward menu")
            handle_trophy_reward_menu(emulator, logger)
            time.sleep(2)
            continue

        # handle the clan voyage popup blocking the main menu
        if check_if_on_clan_voyage(emulator):
            logger.change_status("Closing clan voyage page")
            handle_clan_voyage_page(emulator)
            time.sleep(2)
            continue

        # click deadspace
        if deadspace_click and random.randint(0, 1) == 0:
            emulator.click(
                CLASH_MAIN_MENU_DEADSPACE_COORD[0],
                CLASH_MAIN_MENU_DEADSPACE_COORD[1],
            )
        time.sleep(1)

    time.sleep(1)
    if check_if_on_clash_main_menu(emulator) is not True:
        print("Failed to get to clash main! Saw these pixels before restarting:")
        return False

    return True


def get_to_card_page_from_clash_main(
    emulator,
    logger: Logger,
) -> Literal["restart", "good"]:
    start_time = time.time()

    logger.change_status(status="Opening card page from main menu")

    # click card page icon
    emulator.click(
        CARD_PAGE_ICON_FROM_CLASH_MAIN[0],
        CARD_PAGE_ICON_FROM_CLASH_MAIN[1],
    )
    time.sleep(2.5)

    # while not on the card page, cycle the card page
    while not check_if_on_card_page(emulator):
        time_taken = time.time() - start_time
        if time_taken > 30:
            return "restart"

        emulator.click(
            CARD_PAGE_ICON_FROM_CARD_PAGE[0],
            CARD_PAGE_ICON_FROM_CARD_PAGE[1],
        )
        time.sleep(3)

    logger.change_status(status="Made it to card page")

    return "good"


def return_to_clash_main_from_card_page(emulator, logger: Logger) -> bool:
    """Click the card page exit button and verify the bot is on the main menu."""
    logger.change_status("Returning to main menu...")
    emulator.click(*CARD_PAGE_EXIT_BUTTON_COORDS)
    time.sleep(1)
    if not check_if_on_clash_main_menu(emulator):
        logger.change_status("Failed to return to main menu from card page")
        return False
    return True


def open_clash_main_options_menu(emulator, logger: Logger, printmode: bool = False) -> bool:
    """Open the burger menu from the Clash main screen. Returns False if not on main or menu never opens."""
    if check_if_on_clash_main_menu(emulator) is not True:
        logger.change_status(status="Not on main menu")
        return False

    if printmode:
        logger.change_status(status="Opening burger menu")
    else:
        logger.log("Opening burger menu")
    emulator.click(
        CLASH_MAIN_OPTIONS_BURGER_BUTTON[0],
        CLASH_MAIN_OPTIONS_BURGER_BUTTON[1],
    )
    if wait_for_clash_main_burger_button_options_menu(emulator, logger, printmode) == "restart":
        logger.change_status(status="Timed out waiting for burger menu")
        return False
    return True


def get_to_activity_log(
    emulator,
    logger: Logger,
    printmode: bool = False,
) -> Literal["restart", "good"]:
    if printmode:
        logger.change_status(status="Getting to activity log")
    else:
        logger.log("Getting to activity log")

    if not open_clash_main_options_menu(emulator, logger, printmode):
        return "restart"

    # click battle log button
    if printmode:
        logger.change_status(status="Clicking activity log button")
    else:
        logger.log("Clicking activity log button")
    emulator.click(BATTLE_LOG_BUTTON[0], BATTLE_LOG_BUTTON[1])
    if wait_for_battle_log_page(emulator, logger, printmode) == "restart":
        logger.change_status(status="Timed out waiting for battle log page")
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
            logger.change_status(status="Timed out waiting for battle log page")
            return "restart"

    if printmode:
        logger.change_status(status="Done waiting for battle log page to appear")
    else:
        logger.log("Done waiting for battle log page to appear")

    return "good"


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
        logger.change_status(status="Waiting for burger menu to appear")
    else:
        logger.log("Waiting for burger menu to appear")
    while not check_if_on_clash_main_burger_button_options_menu(emulator):
        time_taken = time.time() - start_time
        if time_taken > 20:
            logger.change_status(status="Timed out waiting for burger menu")
            return "restart"
    if printmode:
        logger.change_status(status="Burger menu open")
    else:
        logger.log("Burger menu open")
    return "good"


def select_mode(emulator, mode: str, logger: Logger | None = None):
    # Check if the mode is valid
    expected_mode_types = ["Classic 1v1", "Classic 2v2", "Trophy Road"]
    if type(mode) is not str:
        msg = f'[!] Warning: Mode "{mode}" is not a string. Expected a string.'
        if logger is not None:
            logger.change_status(msg)
        else:
            print(msg)
        return False

    # Check if the mode is valid
    if mode not in expected_mode_types:
        msg = f'[!] Warning: Mode "{mode}" is not a valid mode type. Expected one of {expected_mode_types}.'
        if logger is not None:
            logger.change_status(msg)
        else:
            print(msg)
        return False

    # must be on clash main
    if not check_if_on_clash_main_menu(emulator):
        msg = "Not on main menu — cannot select battle mode"
        if logger is not None:
            logger.change_status(msg)
        else:
            print(f"[!] {msg}")
        return False

    if logger is not None:
        logger.change_status(f"Selecting {mode}...")

    # open fight type selection menu
    game_mode_coord = [308, 485]

    # click select mode button
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
    start_time = time.time()

    # Use a fixed start time so we actually time out correctly instead of
    # comparing two moving time.time() values (which would never time out).
    while time.time() - start_time < search_timeout:
        coord = find_fight_mode_icon(emulator, mode)
        if coord is not None:
            emulator.click(*coord)
            time.sleep(3)

            # After choosing a mode, the mode panel may remain open on some
            # devices/emulators. Click a safe deadspace coord to ensure the
            # selection panel closes and the main menu is active again so
            # subsequent actions (like pressing Start) work reliably.
            try:
                emulator.click(CLASH_MAIN_MENU_DEADSPACE_COORD[0], CLASH_MAIN_MENU_DEADSPACE_COORD[1])
            except Exception:
                # Don't fail if the click doesn't work; best-effort only.
                pass

            if logger is not None:
                logger.change_status(f"Selected {mode}")
            return True

        scroll_down_in_fight_mode_panel(emulator)

    if logger is not None:
        logger.change_status(f"Failed to find {mode} in mode panel")
    return False


# ===== Main-page navigation system =====================================

PAGE_MAIN = "main"
PAGE_CARD = "card_page"
PAGE_SHOP = "shop"
PAGE_SOCIAL = "social"
PAGE_CLAN_CHAT = "clan-chat"
PAGE_WAR = "war"


MAIN_PAGE_CHECKS = {
    PAGE_MAIN: check_if_on_clash_main_menu,
    PAGE_CARD: check_if_on_card_page,
    PAGE_SHOP: check_if_on_shop,
    PAGE_SOCIAL: check_if_on_social,
    PAGE_CLAN_CHAT: check_if_on_clan_chat,
    PAGE_WAR: check_if_on_war,
}


NAV_CLICKS: dict[tuple[str, str], list[tuple[int, int]]] = {
    (PAGE_MAIN, PAGE_CARD): [BOTTOM_NAV_CARD_TAB_FROM_MAIN_COORD],
    (PAGE_MAIN, PAGE_SHOP): [BOTTOM_NAV_SHOP_TAB_COORD],
    (PAGE_MAIN, PAGE_SOCIAL): [BOTTOM_NAV_SOCIAL_TAB_COORD],
    (PAGE_MAIN, PAGE_CLAN_CHAT): [BOTTOM_NAV_SOCIAL_TAB_COORD, BOTTOM_NAV_CLAN_CHAT_TAB_COORD],
    (PAGE_MAIN, PAGE_WAR): [BOTTOM_NAV_SOCIAL_TAB_COORD, WAR_TAB_FROM_SOCIAL_COORD],
    (PAGE_CARD, PAGE_MAIN): [BOTTOM_NAV_MAIN_TAB_FROM_CARD_COORD],
    (PAGE_CARD, PAGE_SHOP): [BOTTOM_NAV_SHOP_TAB_COORD],
    (PAGE_CARD, PAGE_SOCIAL): [BOTTOM_NAV_SOCIAL_TAB_COORD],
    (PAGE_CARD, PAGE_CLAN_CHAT): [BOTTOM_NAV_SOCIAL_TAB_COORD, BOTTOM_NAV_CLAN_CHAT_TAB_COORD],
    (PAGE_CARD, PAGE_WAR): [BOTTOM_NAV_SOCIAL_TAB_COORD, WAR_TAB_FROM_SOCIAL_COORD],
    (PAGE_SHOP, PAGE_MAIN): [BOTTOM_NAV_MAIN_TAB_FROM_SHOP_COORD],
    (PAGE_SHOP, PAGE_CARD): [BOTTOM_NAV_BATTLE_TAB_COORD],
    (PAGE_SHOP, PAGE_SOCIAL): [BOTTOM_NAV_SOCIAL_TAB_COORD],
    (PAGE_SHOP, PAGE_CLAN_CHAT): [BOTTOM_NAV_SOCIAL_TAB_COORD, BOTTOM_NAV_CLAN_CHAT_TAB_COORD],
    (PAGE_SHOP, PAGE_WAR): [BOTTOM_NAV_SOCIAL_TAB_COORD, WAR_TAB_FROM_SOCIAL_COORD],
    (PAGE_SOCIAL, PAGE_MAIN): [BOTTOM_NAV_BATTLE_TAB_COORD],
    (PAGE_SOCIAL, PAGE_CARD): [BOTTOM_NAV_CARD_TAB_COORD],
    (PAGE_SOCIAL, PAGE_SHOP): [BOTTOM_NAV_SHOP_TAB_COORD],
    (PAGE_SOCIAL, PAGE_CLAN_CHAT): [BOTTOM_NAV_CLAN_CHAT_TAB_COORD],
    (PAGE_SOCIAL, PAGE_WAR): [WAR_TAB_FROM_SOCIAL_COORD],
    (PAGE_CLAN_CHAT, PAGE_MAIN): [CLAN_CHAT_EXIT_DEADSPACE_COORD, BOTTOM_NAV_BATTLE_TAB_COORD],
    (PAGE_CLAN_CHAT, PAGE_CARD): [CLAN_CHAT_EXIT_DEADSPACE_COORD, BOTTOM_NAV_CARD_TAB_COORD],
    (PAGE_CLAN_CHAT, PAGE_SHOP): [CLAN_CHAT_EXIT_DEADSPACE_COORD, BOTTOM_NAV_SHOP_TAB_COORD],
    (PAGE_CLAN_CHAT, PAGE_SOCIAL): [CLAN_CHAT_TO_SOCIAL_COORD],
    (PAGE_CLAN_CHAT, PAGE_WAR): [CLAN_CHAT_EXIT_DEADSPACE_COORD, WAR_TAB_FROM_SOCIAL_COORD],
    (PAGE_WAR, PAGE_MAIN): [WAR_EXIT_DEADSPACE_COORD, BOTTOM_NAV_MAIN_TAB_FROM_WAR_COORD],
    (PAGE_WAR, PAGE_CARD): [WAR_EXIT_DEADSPACE_COORD, BOTTOM_NAV_CARD_TAB_FROM_WAR_COORD],
    (PAGE_WAR, PAGE_SHOP): [WAR_EXIT_DEADSPACE_COORD, BOTTOM_NAV_SHOP_TAB_FROM_WAR_COORD],
    (PAGE_WAR, PAGE_SOCIAL): [WAR_EXIT_DEADSPACE_COORD],
    (PAGE_WAR, PAGE_CLAN_CHAT): [WAR_EXIT_DEADSPACE_COORD, BOTTOM_NAV_CLAN_CHAT_TAB_FROM_WAR_COORD],
}


def navigate_main_page(emulator, logger: Logger, start_page: str, end_page: str) -> bool:
    """Navigate from start_page to end_page using the recorded click sequence.

    Caller must ensure the bot is on start_page before calling. Sleeps 2 s after
    every click (between clicks AND between the last click and the destination
    check). Returns True iff check_if_on_<end_page>(emulator) is True.
    """
    if start_page == end_page:
        return MAIN_PAGE_CHECKS[end_page](emulator)

    clicks = NAV_CLICKS.get((start_page, end_page))
    if clicks is None:
        raise ValueError(f"no recorded navigation for {start_page!r} -> {end_page!r}")

    logger.log(f"navigate_main_page: {start_page} -> {end_page} via {len(clicks)} click(s)")
    for i, (x, y) in enumerate(clicks, 1):
        logger.log(f"  step {i}/{len(clicks)}: clicking ({x}, {y})")
        emulator.click(x, y)
        time.sleep(2)

    # The war page flashes up before the clan-war results popup ("war boot") lands
    # on top of it, so let it settle before checking — otherwise we'd test during
    # the flash, see the war page (popup not up yet), miss it, and get stuck behind
    # the popup. Then click through it before the destination check.
    if end_page == PAGE_WAR:
        logger.log("  war page: waiting 5s for the popup to settle")
        time.sleep(5)
        # Battle-days-started popup FIRST: it fronts the war page before the
        # final-results / war-boot popups when a new battle day begins.
        logger.log("  checking for battle-days-started popup...")
        if check_for_battle_days_started_popup(emulator):
            logger.change_status("Battle-days-started popup detected, handling it")
            handle_battle_days_started_popup(emulator, logger)
        else:
            logger.log("  no battle-days-started popup")
        # Final-results check next: it's the more specific fingerprint (magenta title
        # band), whereas the war-boot check shares the bottom button bar and would
        # false-positive on the final-results page. Handle the specific one, then war boot.
        logger.log("  checking for final-results page...")
        if check_for_final_results_page(emulator):
            logger.change_status("War final-results page detected, handling it")
            handle_final_results_page(emulator, logger)
        else:
            logger.log("  no final-results page")
        logger.log("  checking for war-boot popup...")
        if check_if_on_war_boot(emulator):
            logger.change_status("War boot popup detected, handling it")
            handle_war_boot(emulator, logger)
        else:
            logger.log("  no war-boot popup")

    arrived = MAIN_PAGE_CHECKS[end_page](emulator)
    logger.log(f"  arrival check: on {end_page}? {arrived}")
    return arrived


_WAR_BOOT_HANDLE_TIMEOUT_S = 30.0


def handle_war_boot(emulator, logger: Logger) -> bool:
    """Clear the clan-war results popup ("war boot") by clicking its reward until
    the war page is reached.

    Mirrors the requested "while 1: click reward; break if on war page" flow but is
    timeout-bounded — bot/AGENTS forbids unbounded retry loops.
    """
    logger.change_status("Handling war boot popup...")
    start_time = time.time()
    while time.time() - start_time < _WAR_BOOT_HANDLE_TIMEOUT_S:
        logger.log(f"  war-boot: clicking reward at {WAR_BOOT_REWARD_COORD}")
        emulator.click(*WAR_BOOT_REWARD_COORD)
        time.sleep(2)
        if check_if_on_war(emulator):
            logger.change_status("Cleared war boot popup, now on war page")
            return True
    logger.change_status("Timed out handling war boot popup")
    return check_if_on_war(emulator)


def handle_final_results_page(emulator, logger: Logger) -> bool:
    """Clear the clan-war final-results page by clicking its OK button twice.

    Detected by state_detect.check_for_final_results_page after the war boot popup.
    Two OK clicks (3s apart) dismiss the results popup and any follow-up it raises.
    """
    logger.change_status("Handling war final-results page...")
    for i in range(2):
        logger.log(f"  final-results: click {i + 1}/2 OK at {CLAN_WAR_FINAL_RESULTS_POPUP_OK_BUTTON}")
        emulator.click(*CLAN_WAR_FINAL_RESULTS_POPUP_OK_BUTTON)
        time.sleep(3)
    return True


def handle_battle_days_started_popup(emulator, logger: Logger) -> bool:
    """Clear the clan-war "battle days started" popup with a single OK click.

    Detected by state_detect.check_for_battle_days_started_popup before the
    final-results / war-boot checks. Clicks the same button the final-results handler
    uses (CLAN_WAR_FINAL_RESULTS_POPUP_OK_BUTTON), once.
    """
    logger.change_status("Handling battle-days-started popup...")
    logger.log(f"  battle-days-started: clicking OK at {CLAN_WAR_FINAL_RESULTS_POPUP_OK_BUTTON}")
    emulator.click(*CLAN_WAR_FINAL_RESULTS_POPUP_OK_BUTTON)
    time.sleep(3)
    return True


# ===== Card-page / deck-page navigation primitives ===================


def _navigate_to_deck_selection(emulator, logger: Logger) -> bool:
    logger.change_status("Navigating to the deck selection page...")
    if not get_to_card_page_from_clash_main(emulator, logger):
        logger.change_status("Failed to get to card page from main.")
        return False
    emulator.click(*DECKS_PAGE_BUTTON_COORDS)
    time.sleep(0.1)
    return True


def switch_deck_page(emulator, logger: Logger) -> bool:
    logger.change_status("Switching deck page...")
    switch_button_coord = find_image(
        emulator.screenshot(), "deck_tabs/switch_deck", subcrop=DECK_TABS_REGION, tolerance=0.98
    )
    if switch_button_coord is not None:
        emulator.click(*switch_button_coord)
        time.sleep(1)
        return True
    logger.change_status("Could not find switch deck page button.")
    return False


# ===== Post-battle navigation =========================================


def get_to_main_after_fight(emulator, logger):
    timeout = 120  # s
    start_time = time.time()
    clicked_ok_or_exit = False

    logger.change_status("Returning to main menu after fight...")

    while time.time() - start_time < timeout:
        if check_if_on_clash_main_menu(emulator) is True:
            time.sleep(3)

            if check_for_trophy_reward_menu(emulator):
                handle_trophy_reward_menu(emulator, logger, printmode=True)
                time.sleep(2)

            logger.change_status("Returned to main menu after fight")
            return True

        if check_for_trophy_reward_menu(emulator):
            handle_trophy_reward_menu(emulator, logger, printmode=True)
            time.sleep(3)
            continue

        if not clicked_ok_or_exit:
            button_coord = find_post_battle_button(emulator)
            if button_coord is not None:
                logger.change_status("Clicking post-battle button")
                emulator.click(button_coord[0], button_coord[1])
                clicked_ok_or_exit = True
                continue

        time.sleep(1)
        emulator.click(CLASH_MAIN_MENU_DEADSPACE_COORD[0], CLASH_MAIN_MENU_DEADSPACE_COORD[1])

    return False


if __name__ == "__main__":
    pass
