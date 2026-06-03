"""Switch between linked Supercell accounts from the main-menu burger menu."""

import time

from pyclashbot.bot.nav import (
    CLASH_MAIN_OPTIONS_BURGER_BUTTON,
    wait_for_clash_main_menu,
)
from pyclashbot.bot.state_detect import (
    check_if_on_clash_main_burger_button_options_menu,
    check_if_on_clash_main_menu,
)
from pyclashbot.utils.cancellation import interruptible_sleep
from pyclashbot.utils.logger import Logger

# 419x633 emulator resolution (same as CLASH_MAIN_OPTIONS_BURGER_BUTTON in nav.py).
SWITCH_ACCOUNT_BUTTON_COORD = (221, 468)
ACCOUNT_SLOT_CLICK_COORDS: dict[int, tuple[int, int]] = {
    1: (253, 380),
    2: (251, 476),
    3: (252, 572),
}

ACCOUNT_SWITCH_MAIN_WAIT_TIMEOUT = 180
ACCOUNT_PICKER_WAIT_TIMEOUT = 40
SWITCH_ACCOUNT_LOAD_SLEEP = 3.0

# Cold-start hardening (BlueStacks often needs an extra beat after main menu).
MAIN_MENU_SETTLE_BEFORE_FIRST_SWITCH = 2.5
BURGER_OPEN_ATTEMPTS = 2
BURGER_MENU_WAIT_PER_ATTEMPT = 8
SWITCH_ACCOUNT_ATTEMPTS = 2
PICKER_MIN_WAIT_BEFORE_BURGER_GONE = 1.0

_first_switch_this_process = True


def _settle_main_menu_if_first_switch(logger: Logger) -> None:
    global _first_switch_this_process
    if not _first_switch_this_process:
        return
    logger.change_status("Waiting for main menu to settle...")
    interruptible_sleep(MAIN_MENU_SETTLE_BEFORE_FIRST_SWITCH)
    _first_switch_this_process = False


def _open_burger_menu_with_retry(emulator, logger: Logger) -> bool:
    for attempt in range(1, BURGER_OPEN_ATTEMPTS + 1):
        if check_if_on_clash_main_burger_button_options_menu(emulator):
            return True
        if not check_if_on_clash_main_menu(emulator):
            logger.change_status("Not on Clash main menu — cannot open burger menu")
            return False
        logger.change_status(f"Opening burger menu (try {attempt}/{BURGER_OPEN_ATTEMPTS})...")
        emulator.click(*CLASH_MAIN_OPTIONS_BURGER_BUTTON)
        deadline = time.time() + BURGER_MENU_WAIT_PER_ATTEMPT
        while time.time() < deadline:
            if check_if_on_clash_main_burger_button_options_menu(emulator):
                return True
            interruptible_sleep(0.5)
    logger.change_status("Burger menu did not open")
    return False


def _click_switch_account_with_retry(emulator, logger: Logger) -> bool:
    for attempt in range(1, SWITCH_ACCOUNT_ATTEMPTS + 1):
        logger.change_status(f"Opening Switch Account (try {attempt}/{SWITCH_ACCOUNT_ATTEMPTS})...")
        emulator.click(*SWITCH_ACCOUNT_BUTTON_COORD)
        interruptible_sleep(SWITCH_ACCOUNT_LOAD_SLEEP)
        if not check_if_on_clash_main_burger_button_options_menu(emulator):
            return True
        if attempt < SWITCH_ACCOUNT_ATTEMPTS:
            logger.change_status("Still on burger menu — retrying Switch Account tap...")
    logger.change_status("Still on burger menu after Switch Account taps")
    return False


def _wait_for_account_picker(emulator, logger: Logger) -> bool:
    """Wait until burger menu pixels clear (Supercell ID list replaces that overlay)."""
    start = time.time()
    logger.change_status("Waiting for Supercell ID account list...")
    while time.time() - start < ACCOUNT_PICKER_WAIT_TIMEOUT:
        if (
            not check_if_on_clash_main_burger_button_options_menu(emulator)
            and (time.time() - start) >= PICKER_MIN_WAIT_BEFORE_BURGER_GONE
        ):
            logger.change_status("Supercell ID account list open")
            return True

        elapsed = int(time.time() - start)
        logger.change_status(f"Waiting for account list ({elapsed}s)...")
        interruptible_sleep(1)

    if check_if_on_clash_main_burger_button_options_menu(emulator):
        logger.change_status("Still on burger menu — Switch Account tap may be wrong")
    else:
        logger.change_status("Left burger menu but account list not confirmed")
    return False


def _click_account_slot(emulator, logger: Logger, slot: int) -> bool:
    """Click account row `slot` (1 = first linked account, 2 = second, etc.)."""
    if slot not in ACCOUNT_SLOT_CLICK_COORDS:
        logger.change_status(f"No click coordinates for account slot {slot}")
        return False
    emulator.click(*ACCOUNT_SLOT_CLICK_COORDS[slot])
    interruptible_sleep(2)
    return True


def switch_account_state(emulator, logger: Logger, account_slot: int) -> bool:
    """Open the account picker and switch to `account_slot` (1-based). Returns True on main menu."""
    if not check_if_on_clash_main_menu(emulator):
        logger.change_status("Not on Clash main menu — cannot switch accounts")
        return False

    _settle_main_menu_if_first_switch(logger)

    logger.change_status(f"Switching to account slot {account_slot}...")
    if not _open_burger_menu_with_retry(emulator, logger):
        return False

    if not _click_switch_account_with_retry(emulator, logger):
        return False

    if not _wait_for_account_picker(emulator, logger):
        return False

    logger.change_status(f"Tapping account row {account_slot}...")
    if not _click_account_slot(emulator, logger, account_slot):
        return False

    interruptible_sleep(2)
    logger.change_status("Waiting for main menu after account switch...")
    if not wait_for_clash_main_menu(
        emulator,
        logger,
        deadspace_click=True,
        timeout=ACCOUNT_SWITCH_MAIN_WAIT_TIMEOUT,
    ):
        logger.change_status("Timed out returning to main menu after account switch")
        return False

    logger.change_status(f"Now on account slot {account_slot}")
    return True
