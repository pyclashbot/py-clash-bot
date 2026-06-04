"""Clan chat actions: donate, claim Pass Royale gifts, and request cards."""

from __future__ import annotations

import os
import time
from os.path import abspath, dirname, join

import cv2
import numpy as np

from pyclashbot.bot.nav import (
    PAGE_CLAN_CHAT,
    PAGE_MAIN,
    PAGE_SOCIAL,
    handle_trophy_reward_menu,
    navigate_main_page,
)
from pyclashbot.bot.state_detect import (
    check_for_trophy_reward_menu,
    check_if_on_clan_chat,
    check_if_on_clash_main_menu,
    check_if_on_social,
    clan_button_pixel_is_active_green,
    clan_button_pixel_is_active_yellow,
)
from pyclashbot.detection.image_rec import find_image
from pyclashbot.utils.cancellation import interruptible_sleep

REFERENCE_ROOT = abspath(join(dirname(__file__), "..", "detection", "reference_images"))

# Visible clan chat feed (no scrolling in v1). Keep above bottom nav (~y=600).
CHAT_FEED_SUBCROP = (0, 60, 419, 500)
CLAN_FOOTER_SUBCROP = (0, 470, 280, 600)
REQUEST_PICKER_SUBCROP = (0, 70, 419, 600)

MAX_FEED_ACTIONS = 10
TEMPLATE_TOLERANCE = 0.88
PICKER_OPEN_TIMEOUT = 8.0
# Blue request arrow sits on the left of a card tile; click the card body.
REQUEST_CARD_CLICK_OFFSET = (48, -40)


def _load_template(folder: str) -> np.ndarray | None:
    path = join(REFERENCE_ROOT, folder)
    names = [n for n in os.listdir(path) if n.endswith(".png")]
    if not names:
        return None
    return cv2.imread(join(path, names[0]))


def _template_size(folder: str) -> tuple[int, int]:
    template = _load_template(folder)
    if template is None:
        return (40, 20)
    h, w = template.shape[:2]
    return w, h


def _sample_pixel(image: np.ndarray, x: int, y: int) -> np.ndarray:
    height, width = image.shape[:2]
    sx = min(max(x, 0), width - 1)
    sy = min(max(y, 0), height - 1)
    return image[sy][sx]


def _region_passes_color_check(
    image: np.ndarray,
    x: int,
    y: int,
    tw: int,
    th: int,
    color_check,
) -> bool:
    """Sample around the template box — text crops are white on green/grey, not solid fill."""
    height, width = image.shape[:2]
    probes = [
        (x + 2, y + 2),
        (x + tw - 2, y + 2),
        (x + 2, y + th - 2),
        (x + tw - 2, y + th - 2),
        (x + tw // 2, y + th // 2),
        (min(x + tw + 3, width - 1), y + th // 2),
    ]
    return any(color_check(_sample_pixel(image, px, py)) for px, py in probes)


def _find_all_template_coords(
    image: np.ndarray,
    folder: str,
    *,
    subcrop: tuple[int, int, int, int],
    tolerance: float,
) -> list[tuple[int, int]]:
    """All template hits in subcrop (full-image x,y), best scores first. Masks grey duplicates."""
    template = _load_template(folder)
    if template is None:
        return []

    x1, y1, x2, y2 = subcrop
    region = image[y1:y2, x1:x2]
    th, tw = template.shape[:2]
    if th > region.shape[0] or tw > region.shape[1]:
        return []

    region_work = region.copy()
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    coords: list[tuple[int, int]] = []

    for _ in range(MAX_FEED_ACTIONS * 3):
        region_gray = cv2.cvtColor(region_work, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(region_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        _min_val, max_val, _min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val < tolerance:
            break
        local_x, local_y = int(max_loc[0]), int(max_loc[1])
        coords.append((x1 + local_x, y1 + local_y))
        pad = 4
        y_a = max(local_y - pad, 0)
        y_b = min(local_y + th + pad, region_work.shape[0])
        x_a = max(local_x - pad, 0)
        x_b = min(local_x + tw + pad, region_work.shape[1])
        region_work[y_a:y_b, x_a:x_b] = 0

    return coords


def _click_active_templates(
    emulator,
    logger,
    folder: str,
    *,
    subcrop: tuple[int, int, int, int],
    color_check,
    action_label: str,
    on_success,
) -> int:
    clicks = 0
    for _ in range(MAX_FEED_ACTIONS):
        image = emulator.screenshot()
        tw, th = _template_size(folder)
        clicked = False
        for x, y in _find_all_template_coords(
            image,
            folder,
            subcrop=subcrop,
            tolerance=TEMPLATE_TOLERANCE,
        ):
            if not _region_passes_color_check(image, x, y, tw, th, color_check):
                continue
            emulator.click(x + tw // 2, y + th // 2)
            clicks += 1
            on_success()
            logger.change_status(f"{action_label} ({clicks})")
            interruptible_sleep(1.5)
            clicked = True
            break
        if not clicked:
            break
    return clicks


def _open_request_picker(emulator, logger) -> bool:
    image = emulator.screenshot()
    tw, th = _template_size("clan_chat/request_footer_text")
    footer = None
    for x, y in _find_all_template_coords(
        image,
        "clan_chat/request_footer_text",
        subcrop=CLAN_FOOTER_SUBCROP,
        tolerance=TEMPLATE_TOLERANCE,
    ):
        if _region_passes_color_check(image, x, y, tw, th, clan_button_pixel_is_active_yellow):
            footer = (x, y)
            break

    if footer is None:
        if _find_all_template_coords(
            image,
            "clan_chat/request_footer_text",
            subcrop=CLAN_FOOTER_SUBCROP,
            tolerance=TEMPLATE_TOLERANCE,
        ):
            logger.change_status("Request Cards on cooldown")
        else:
            logger.change_status("Request Cards button not found")
        return False

    fx, fy = footer
    emulator.click(fx + tw // 2, fy + th // 2)
    logger.change_status("Opening card request picker...")
    interruptible_sleep(2)

    start = time.time()
    while time.time() - start < PICKER_OPEN_TIMEOUT:
        if (
            find_image(
                emulator.screenshot(),
                "clan_chat/request_arrow",
                tolerance=0.85,
                subcrop=REQUEST_PICKER_SUBCROP,
            )
            is not None
        ):
            return True
        interruptible_sleep(0.5)

    logger.change_status("Card request picker did not open")
    return False


def _request_cards_from_picker(emulator, logger) -> bool:
    image = emulator.screenshot()
    arrow = find_image(
        image,
        "clan_chat/request_arrow",
        tolerance=0.85,
        subcrop=REQUEST_PICKER_SUBCROP,
    )
    if arrow is None:
        logger.change_status("No requestable card (blue arrow) on screen")
        return False

    ax, ay = arrow
    emulator.click(ax + REQUEST_CARD_CLICK_OFFSET[0], ay + REQUEST_CARD_CLICK_OFFSET[1])
    interruptible_sleep(1)

    image = emulator.screenshot()
    tw, th = _template_size("clan_chat/request_confirm")
    confirm = None
    for x, y in _find_all_template_coords(
        image,
        "clan_chat/request_confirm",
        subcrop=REQUEST_PICKER_SUBCROP,
        tolerance=TEMPLATE_TOLERANCE,
    ):
        if _region_passes_color_check(image, x, y, tw, th, clan_button_pixel_is_active_yellow):
            confirm = (x, y)
            break

    if confirm is None:
        logger.change_status("Request confirm not active")
        return False

    cx, cy = confirm
    emulator.click(cx + tw // 2, cy + th // 2)
    logger.add_request()
    logger.change_status("Requested cards from clan")
    interruptible_sleep(2)
    return True


def _ensure_clan_chat(emulator, logger) -> bool:
    if check_if_on_clan_chat(emulator):
        return True
    if not check_if_on_clash_main_menu(emulator):
        logger.change_status("Not on main menu — cannot open clan chat")
        return False
    if not navigate_main_page(emulator, logger, PAGE_MAIN, PAGE_CLAN_CHAT):
        logger.change_status("Failed to navigate to clan chat")
        return False
    interruptible_sleep(1)
    return check_if_on_clan_chat(emulator)


def _tap_battle_tab(emulator, logger) -> None:
    """Center/battle bottom-nav tab — returns to main from Social hub or clan chat."""
    logger.change_status("Tapping battle tab to reach main menu...")
    emulator.click(170, 600)
    interruptible_sleep(2)


def _open_clan_chat_via_bottom_nav(emulator, logger) -> bool:
    """Social tab then clan chat sub-tab (matches main -> clan-chat nav clicks)."""
    logger.change_status("Opening clan chat via bottom nav...")
    emulator.click(315, 600)
    interruptible_sleep(1.5)
    emulator.click(280, 600)
    interruptible_sleep(2)
    return check_if_on_clan_chat(emulator)


def _recover_clan_chat_from_social(emulator, logger) -> bool:
    """Clan chat lives under the Social bottom-nav tab; mis-clicks can land here without chat open."""
    if check_if_on_clan_chat(emulator):
        return True
    if check_if_on_social(emulator):
        logger.change_status("On Social tab — reopening clan chat...")
        if navigate_main_page(emulator, logger, PAGE_SOCIAL, PAGE_CLAN_CHAT):
            interruptible_sleep(1)
            return check_if_on_clan_chat(emulator)
    return _open_clan_chat_via_bottom_nav(emulator, logger)


def _wait_for_main_after_clan(emulator, logger, timeout: float = 25) -> bool:
    """Return to main from clan/social without generic wait (trophy check false-positives there)."""
    start = time.time()
    while time.time() - start < timeout:
        if check_if_on_clash_main_menu(emulator):
            return True

        if check_if_on_clan_chat(emulator):
            if navigate_main_page(emulator, logger, PAGE_CLAN_CHAT, PAGE_MAIN):
                interruptible_sleep(1)
            continue

        if check_if_on_social(emulator):
            logger.change_status("On Social tab — returning to main menu...")
            if navigate_main_page(emulator, logger, PAGE_SOCIAL, PAGE_MAIN):
                interruptible_sleep(1)
            continue

        if (
            not check_if_on_social(emulator)
            and not check_if_on_clan_chat(emulator)
            and check_for_trophy_reward_menu(emulator)
        ):
            handle_trophy_reward_menu(emulator, logger)
            interruptible_sleep(1)
            continue

        _tap_battle_tab(emulator, logger)

    return check_if_on_clash_main_menu(emulator)


def _return_to_main(emulator, logger) -> bool:
    if check_if_on_clash_main_menu(emulator):
        return True

    if check_if_on_clan_chat(emulator):
        if navigate_main_page(emulator, logger, PAGE_CLAN_CHAT, PAGE_MAIN):
            interruptible_sleep(1)
            if check_if_on_clash_main_menu(emulator):
                return True

    if check_if_on_social(emulator):
        logger.change_status("On Social tab — returning to main menu...")
        if navigate_main_page(emulator, logger, PAGE_SOCIAL, PAGE_MAIN):
            interruptible_sleep(1)
            if check_if_on_clash_main_menu(emulator):
                return True

    _tap_battle_tab(emulator, logger)
    if check_if_on_clash_main_menu(emulator):
        return True

    return _wait_for_main_after_clan(emulator, logger)


def clan_chat_state(
    emulator,
    logger,
    *,
    donate_enabled: bool,
    claim_enabled: bool,
    request_enabled: bool,
) -> bool:
    if not donate_enabled and not claim_enabled and not request_enabled:
        return True

    logger.change_status("Running clan chat jobs...")
    if not _ensure_clan_chat(emulator, logger):
        return False

    if claim_enabled:
        count = _click_active_templates(
            emulator,
            logger,
            "clan_chat/claim_active",
            subcrop=CHAT_FEED_SUBCROP,
            color_check=clan_button_pixel_is_active_green,
            action_label="Claiming clan gift",
            on_success=logger.add_clan_gift_claim,
        )
        if count == 0:
            logger.change_status("No claimable clan gifts visible")

    if donate_enabled:
        count = _click_active_templates(
            emulator,
            logger,
            "clan_chat/donate_active",
            subcrop=CHAT_FEED_SUBCROP,
            color_check=clan_button_pixel_is_active_green,
            action_label="Donating",
            on_success=logger.add_donate,
        )
        if count == 0:
            logger.change_status("No active donate buttons visible")
        if not _recover_clan_chat_from_social(emulator, logger):
            return _return_to_main(emulator, logger)

    if request_enabled:
        if _open_request_picker(emulator, logger):
            _request_cards_from_picker(emulator, logger)

    return _return_to_main(emulator, logger)
