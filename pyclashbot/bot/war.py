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
    emulator.click(*_MAKE_WAR_DECK_COORDS[deck_index])
    time.sleep(2)
    emulator.click(*MAKE_RANDOM_WAR_DECK_BUTTON)
    time.sleep(1)
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
        if not check_for_in_battle_with_delay(emulator):
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
        emulator.click(card[0], card[1])
        emulator.click(random.randint(left, right), random.randint(top, bottom))
        time.sleep(_WAR_BATTLE_LOOP_STEP_SLEEP_S)

    logger.change_status("War battle complete")
    return True


def _dismiss_war_post_battle(emulator, logger, timeout: float) -> bool:
    """Click post-battle OK until back on the war page."""
    start = time.time()
    clicked_ok = False
    while time.time() - start < timeout:
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
    decks = which_war_decks_exist(emulator)
    for di in (1, 2, 3, 4):
        if not decks.get(f"deck{di}", False):
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
        _scroll_war_page(emulator, direction)
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

    if not check_if_on_clash_main_menu(emulator):
        logger.change_status("Not on main menu — cannot run war state")
        return False

    if not navigate_main_page(emulator, logger, PAGE_MAIN, PAGE_WAR):
        logger.change_status("Failed to navigate to war page")
        return False
    time.sleep(1)
    if not check_if_on_war(emulator):
        logger.change_status("Did not land on war page")
        return False

    _ensure_all_war_decks(emulator, logger)

    if not _find_and_click_war_battle_icon(emulator, logger):
        return navigate_main_page(emulator, logger, PAGE_WAR, PAGE_MAIN)

    time.sleep(2)

    if not check_if_can_war_battle(emulator):
        logger.change_status("No more war battles available — exiting cleanly")
        emulator.click(*WAR_DEADSPACE_COORD)
        time.sleep(1)
        if not navigate_main_page(emulator, logger, PAGE_WAR, PAGE_MAIN):
            logger.change_status("Failed to return to main menu from war")
            return False
        time.sleep(1)
        return check_if_on_clash_main_menu(emulator)

    emulator.click(*START_WAR_BATTLE_BUTTON_COORDS)
    time.sleep(2)

    if not wait_for_battle_start(emulator, logger, timeout=_WAR_BATTLE_START_TIMEOUT_S):
        logger.change_status("War battle never started")
        return False

    if war_battle_loop(emulator, logger) is False:
        return False

    if not _dismiss_war_post_battle(emulator, logger, _WAR_POST_BATTLE_DISMISS_TIMEOUT_S):
        if not _wait_for_war_page(emulator, _WAIT_FOR_WAR_AFTER_BATTLE_S):
            logger.change_status("Did not return to war page within 30s")
            return False

    if not navigate_main_page(emulator, logger, PAGE_WAR, PAGE_MAIN):
        logger.change_status("Failed to return to main menu from war")
        return False
    time.sleep(1)
    return check_if_on_clash_main_menu(emulator)
