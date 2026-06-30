"""Clan war state: ensure 4 decks, find + start a war battle, play it out, return to main."""

from __future__ import annotations

import random
import time

from pyclashbot.bot.coords import (
    EXIT_MAKE_WAR_DECK_PAGE,
    HAND_CARDS_COORDS,
    MAKE_RANDOM_WAR_DECK_BUTTON,
    MAKE_WAR_DECK_1,
    MAKE_WAR_DECK_2,
    MAKE_WAR_DECK_3,
    MAKE_WAR_DECK_4,
    OK_AFTER_WAR_BATTLE_COMPLETE_BUTTON_COORD,
    START_WAR_BATTLE_BUTTON_COORDS,
    WAR_BATTLE_PLAYFIELD_LTRB,
    WAR_DEADSPACE_COORD,
)
from pyclashbot.bot.find import find_post_battle_button, find_war_battle_icon
from pyclashbot.bot.nav import (
    PAGE_MAIN,
    PAGE_WAR,
    check_for_in_battle_with_delay,
    navigate_main_page,
    wait_for_battle_start,
)
from pyclashbot.bot.state_detect import (
    check_for_post_battle_button,
    check_if_battle_has_ended,
    check_if_can_war_battle,
    check_if_on_clash_main_menu,
    check_if_on_war,
    which_war_decks_exist,
)

_MAKE_WAR_DECK_COORDS = {
    1: MAKE_WAR_DECK_1,
    2: MAKE_WAR_DECK_2,
    3: MAKE_WAR_DECK_3,
    4: MAKE_WAR_DECK_4,
}

_WAR_BATTLE_LOOP_TIMEOUT_S = 300.0
_WAR_BATTLE_LOOP_STEP_SLEEP_S = 7.0
_SCROLL_X = 210
_SCROLL_UP_Y = (300, 500)
_SCROLL_DOWN_Y = (500, 300)
_FIND_BATTLE_MAX_LOOPS = 10
_WAIT_FOR_WAR_AFTER_BATTLE_S = 30.0
_WAR_BATTLE_START_TIMEOUT_S = 120
_WAR_POST_BATTLE_DISMISS_TIMEOUT_S = 60.0


def make_war_deck(emulator, logger, deck_index: int) -> bool:
    """Open empty war-deck slot `deck_index`, randomize it, exit. 1 <= index <= 4."""
    if deck_index not in _MAKE_WAR_DECK_COORDS:
        logger.change_status(f"Invalid war deck index: {deck_index}")
        return False

    logger.change_status(f"Making war deck #{deck_index}...")
    logger.log(f"Clicking war deck slot #{deck_index} at {_MAKE_WAR_DECK_COORDS[deck_index]}")
    emulator.click(*_MAKE_WAR_DECK_COORDS[deck_index])
    time.sleep(2)
    logger.log("Clicking randomize war deck button")
    emulator.click(*MAKE_RANDOM_WAR_DECK_BUTTON)
    time.sleep(1)
    logger.log("Clicking exit war deck page")
    emulator.click(*EXIT_MAKE_WAR_DECK_PAGE)
    time.sleep(1)
    return True


def war_battle_loop(emulator, logger) -> bool:
    """Drop a random card to a random playfield spot every 7s until the battle ends."""
    logger.change_status("In war battle — playing...")
    left, top, right, bottom = WAR_BATTLE_PLAYFIELD_LTRB
    start_time = time.time()
    battle_detection_lost_count = 0

    while True:
        logger.log("Checking if still in war battle")
        if not check_for_in_battle_with_delay(emulator):
            logger.log("Not detected in battle — checking if battle has ended")
            if check_if_battle_has_ended(emulator):
                break

            battle_detection_lost_count += 1
            logger.change_status(
                f"Lost war battle detection ({battle_detection_lost_count}) — waiting it out",
            )
            if battle_detection_lost_count >= 4:
                logger.change_status("Lost war battle detection repeatedly — assuming battle ended")
                break

            time.sleep(1)
            continue

        battle_detection_lost_count = 0
        if time.time() - start_time > _WAR_BATTLE_LOOP_TIMEOUT_S:
            logger.change_status("War battle timed out after 5 minutes")
            return False

        card = random.choice(HAND_CARDS_COORDS)
        play_x, play_y = random.randint(left, right), random.randint(top, bottom)
        logger.log(f"Selecting card at {card} and playing it at ({play_x}, {play_y})")
        emulator.click(card[0], card[1])
        emulator.click(play_x, play_y)
        time.sleep(_WAR_BATTLE_LOOP_STEP_SLEEP_S)

    logger.change_status("War battle complete")
    return True


def _dismiss_war_post_battle(emulator, logger, timeout: float) -> bool:
    """Click post-battle OK until back on the war page."""
    start = time.time()
    clicked_ok = False
    while time.time() - start < timeout:
        logger.log("Checking if back on war page after battle")
        if check_if_on_war(emulator):
            return True

        if not clicked_ok:
            coord = find_post_battle_button(emulator)
            if coord is not None:
                logger.change_status("Clicking post-war-battle OK")
                emulator.click(*coord)
                clicked_ok = True
                time.sleep(2)
                continue

            if check_for_post_battle_button(emulator):
                logger.change_status("Clicking post-war-battle OK (fallback coord)")
                emulator.click(*OK_AFTER_WAR_BATTLE_COMPLETE_BUTTON_COORD)
                clicked_ok = True
                time.sleep(2)
                continue

        time.sleep(1)

    return check_if_on_war(emulator)


def _ensure_all_war_decks(emulator, logger) -> None:
    logger.log("Checking which war decks already exist")
    decks = which_war_decks_exist(emulator)
    logger.log(f"War decks present: {decks}")
    for di in (1, 2, 3, 4):
        if not decks.get(f"deck{di}", False):
            logger.log(f"War deck #{di} missing — making it")
            make_war_deck(emulator, logger, di)


def _scroll_war_page(emulator, direction: str) -> None:
    if direction == "up":
        start_y, end_y = _SCROLL_UP_Y
    else:
        start_y, end_y = _SCROLL_DOWN_Y
    emulator.swipe(_SCROLL_X, start_y, _SCROLL_X, end_y)
    time.sleep(1)


def _find_and_click_war_battle_icon(emulator, logger) -> bool:
    for i in range(_FIND_BATTLE_MAX_LOOPS):
        direction = "up" if i % 2 == 0 else "down"
        logger.log(f"Scrolling war page {direction} (scroll {i + 1}/{_FIND_BATTLE_MAX_LOOPS})")
        _scroll_war_page(emulator, direction)
        logger.log("Looking for a war battle icon")
        coord = find_war_battle_icon(emulator)
        if coord is not None:
            x, y = coord
            logger.change_status(f"Found war battle icon at {coord}")
            emulator.click(x, y)
            return True
    logger.change_status("Could not find a war battle icon after 10 scrolls")
    return False


def _wait_for_war_page(emulator, timeout: float) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        if check_if_on_war(emulator):
            return True
        time.sleep(1)
    return False


def war_state(emulator, logger) -> bool:
    """Full war flow: main → war → fill decks → find+start battle → play → exit → main."""
    logger.change_status("Running war state...")

    logger.log("Checking if on clash main menu")
    if not check_if_on_clash_main_menu(emulator):
        logger.change_status("Not on main menu — cannot run war state")
        return False

    logger.log("Navigating from main page to war page")
    if not navigate_main_page(emulator, logger, PAGE_MAIN, PAGE_WAR):
        logger.change_status("Failed to navigate to war page")
        return False
    time.sleep(1)
    logger.log("Verifying war page is visible")
    if not check_if_on_war(emulator):
        logger.change_status("Did not land on war page")
        return False

    _ensure_all_war_decks(emulator, logger)

    logger.log("Searching for a war battle icon to click")
    if not _find_and_click_war_battle_icon(emulator, logger):
        logger.log("No war battle icon found — returning to main page")
        return navigate_main_page(emulator, logger, PAGE_WAR, PAGE_MAIN)

    time.sleep(2)

    logger.log("Checking if a war battle can be started")
    if not check_if_can_war_battle(emulator):
        logger.change_status("No more war battles available — exiting cleanly")
        logger.log("Clicking war deadspace to dismiss the battle dialog")
        emulator.click(*WAR_DEADSPACE_COORD)
        time.sleep(1)
        logger.log("Navigating from war page back to main page")
        if not navigate_main_page(emulator, logger, PAGE_WAR, PAGE_MAIN):
            logger.change_status("Failed to return to main menu from war")
            return False
        time.sleep(1)
        logger.log("Verifying back on main menu")
        return check_if_on_clash_main_menu(emulator)

    logger.log("Clicking start war battle button")
    emulator.click(*START_WAR_BATTLE_BUTTON_COORDS)
    time.sleep(2)

    logger.log("Waiting for the war battle to start")
    if not wait_for_battle_start(emulator, logger, timeout=_WAR_BATTLE_START_TIMEOUT_S):
        logger.change_status("War battle never started")
        return False

    logger.log("Entering war battle play loop")
    if war_battle_loop(emulator, logger) is False:
        return False

    logger.log("Dismissing post-battle screens")
    if not _dismiss_war_post_battle(emulator, logger, _WAR_POST_BATTLE_DISMISS_TIMEOUT_S):
        logger.log("Post-battle dismiss timed out — waiting for war page")
        if not _wait_for_war_page(emulator, _WAIT_FOR_WAR_AFTER_BATTLE_S):
            logger.change_status("Did not return to war page within 30s")
            return False

    logger.log("Navigating from war page back to main page")
    if not navigate_main_page(emulator, logger, PAGE_WAR, PAGE_MAIN):
        logger.change_status("Failed to return to main menu from war")
        return False
    time.sleep(1)
    logger.log("Verifying back on main menu")
    return check_if_on_clash_main_menu(emulator)
