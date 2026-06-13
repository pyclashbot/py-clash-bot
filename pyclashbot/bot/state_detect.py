"""Pure state-detection helpers.

Every function here follows the same shape: take a screenshot, run a pixel or
image comparison, return a bool. No clicks, no waits, no orchestration — those
live in nav.py or the per-state modules that import from here.

This module is a leaf: the only pyclashbot.bot module it imports from is
`coords` (itself a leaf — pure data, no imports). No nav, fight, deck, etc.
"""

import numpy

from pyclashbot.bot.coords import MORE_CLAN_CHAT_CARD_OPTIONS_SUBCROP
from pyclashbot.detection.image_rec import (
    all_pixels_are_equal,
    check_line_for_color,
    find_image,
    pixel_is_equal,
)

# ===== Battle ==========================================================


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
        if pixel is None:
            return False
        return all(channel >= threshold for channel in pixel) or (
            150 <= pixel[0] <= 195 and 40 <= pixel[1] <= 60 and 40 <= pixel[2] <= 60
        )

    def is_filled_crown(pixel: list[int] | None) -> bool:
        """Check if pixel is a gold/yellow filled crown or UI accent."""
        if pixel is None:
            return False
        r, g, b = pixel
        return r >= 170 and g >= 130 and b <= 140

    def is_scoreboard_purple(pixel: list[int] | None) -> bool:
        if pixel is None:
            return False
        r, g, b = pixel
        return r >= 200 and b >= 200 and g <= 140

    def check_mode(coords: list[tuple[int, int]]) -> bool:
        pixels = [get_pixel(y, x) for y, x in coords]
        # Allow one of the "bright" UI pixels to change (crowns filling, overlays,
        # small rendering differences) while still requiring the purple scoreboard.
        bright_required = max(1, len(coords) - 2)
        bright_count = sum(1 for pixel in pixels[:-1] if is_bright(pixel) or is_filled_crown(pixel))
        return bright_count >= bright_required and is_scoreboard_purple(pixels[-1])

    # When the emote is closed these pixels are not considered bright:
    # (533, 80) RGB=[157, 44, 44] and (532, 77) RGB=[187, 55, 55]
    coords_1v1 = [(528, 49), (532, 77), (546, 52), (546, 77), (618, 115)]
    coords_2v2 = [(534, 53), (533, 80), (548, 52), (548, 76), (615, 114)]

    if check_mode(coords_1v1):
        return True
    if check_mode(coords_2v2):
        return True

    return False


def check_if_battle_has_ended(emulator) -> bool:
    """Best-effort confirmation that a battle ended (avoid false positives mid-fight)."""
    if check_if_on_clash_main_menu(emulator):
        return True

    if check_for_trophy_reward_menu(emulator):
        return True

    if check_for_post_battle_button(emulator):
        return True

    return False


def check_for_post_battle_button(emulator) -> bool:
    """Checks for the post-battle OK/Exit buttons (battle-end screen)."""
    image = emulator.screenshot()
    if image is None:
        return False

    if find_image(image, "ok_post_battle_button", tolerance=0.85) is not None:
        return True

    if find_image(image, "exit_battle_button", tolerance=0.9) is not None:
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


# ===== Fight in-progress / battle log ==================================

ELIXIR_COORDS = [
    [613, 149],
    [613, 165],
    [613, 188],
    [613, 212],
    [613, 240],
    [613, 262],
    [613, 287],
    [613, 314],
    [613, 339],
    [613, 364],
]
ELIXIR_COLOR = [240, 137, 244]


def count_elixir(emulator, elixir_count) -> bool:
    """Method to check for 4 elixir during a battle"""
    iar = emulator.screenshot()

    if pixel_is_equal(
        iar[ELIXIR_COORDS[elixir_count - 1][0], ELIXIR_COORDS[elixir_count - 1][1]],
        ELIXIR_COLOR,
        tol=65,
    ):
        return True
    return False


def check_pixels_for_win_in_battle_log(emulator) -> bool:
    """Method to check pixels that appear in the battle
    log to determine if the previous game was a win
    """
    line1 = check_line_for_color(
        emulator,
        x_1=47,
        y_1=135,
        x_2=109,
        y_2=154,
        color=(255, 51, 102),
    )
    line2 = check_line_for_color(
        emulator,
        x_1=46,
        y_1=152,
        x_2=115,
        y_2=137,
        color=(255, 51, 102),
    )
    line3 = check_line_for_color(
        emulator,
        x_1=47,
        y_1=144,
        x_2=110,
        y_2=147,
        color=(255, 51, 102),
    )

    if line1 and line2 and line3:
        return False
    return True


# ===== Clash main menu =================================================


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

    # post Clash Royale app update colors
    colors_3 = [
        [57, 151, 206],
        [21, 148, 42],
        [36, 17, 1],
        [231, 190, 123],
        [140, 105, 74],
        [140, 105, 74],
        [156, 121, 82],
    ]

    for colors in [colors_1, colors_2, colors_3]:
        if all_pixels_are_equal(
            pixels,
            colors,
            25,
        ):
            return True

    return False


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

    coord = find_image(
        emulator.screenshot(),
        look_folder,
        tolerance=0.9,
        subcrop=(270, 455, 350, 533),
    )

    return coord is not None


# ===== Sub-pages =======================================================


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

    if all_pixels_are_equal(pixels, colors1, tol=25):
        return True

    if all_pixels_are_equal(pixels, colors2, tol=25):
        return True

    return False


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


def check_if_on_shop(emulator) -> bool:
    iar = emulator.screenshot()
    pixels = [
        iar[589][16],
        iar[609][19],
        iar[14][212],
        iar[15][331],
        iar[600][128],
    ]
    colors = [
        [140, 107, 73],
        [151, 116, 77],
        [57, 160, 214],
        [22, 186, 59],
        [255, 225, 137],
    ]
    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=25):
            return False
    return True


def check_if_on_social(emulator) -> bool:
    iar = emulator.screenshot()
    pixels = [
        iar[601][218],
        iar[577][342],
        iar[620][299],
    ]
    colors = [
        [255, 226, 138],
        [142, 108, 75],
        [155, 120, 82],
    ]
    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=25):
            return False
    return True


def check_if_on_war(emulator) -> bool:
    iar = emulator.screenshot()
    pixels = [
        iar[18][146],
        iar[598][177],
        iar[613][237],
        iar[605][396],
        iar[604][26],
        iar[22][270],
        iar[609][24],
        iar[619][406],
        iar[9][260],
        iar[33][280],
    ]
    colors = [
        [253, 90, 182],
        [255, 187, 104],
        [255, 175, 78],
        [110, 88, 74],
        [110, 88, 74],
        [243, 78, 170],
        [109, 88, 74],
        [107, 86, 73],
        [255, 160, 212],
        [227, 61, 154],
    ]
    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=25):
            return False
    return True


_WAR_DECK_INDICATOR_TOL = 15

# Indicator pixels for each war-deck slot (r, g, b, x, y). When ALL 4 pixels for a
# slot match the empty-slot fingerprint, that slot is unused. Any diverging pixel
# means the deck exists.
_WAR_DECK_INDICATORS: dict[int, tuple[tuple[int, int, int, int, int], ...]] = {
    1: (
        (0, 94, 207, 68, 540),
        (0, 108, 211, 64, 502),
        (255, 255, 255, 78, 519),
        (0, 93, 207, 89, 540),
    ),
    2: (
        (0, 108, 211, 153, 502),
        (255, 255, 255, 167, 518),
        (0, 109, 211, 180, 500),
        (0, 101, 209, 151, 520),
    ),
    3: (
        (0, 109, 211, 241, 502),
        (255, 255, 255, 254, 518),
        (0, 94, 207, 267, 537),
        (0, 109, 211, 268, 501),
    ),
    4: (
        (0, 109, 211, 329, 500),
        (255, 255, 255, 343, 520),
        (0, 94, 207, 352, 538),
        (0, 109, 211, 354, 501),
    ),
}


def which_war_decks_exist(emulator) -> dict[str, bool]:
    """Return {"deck1": bool, ..., "deck4": bool}.

    Each deck has 4 indicator pixels. If ALL 4 match (the empty/placeholder look),
    the deck slot is unused → False. If any pixel diverges, the deck exists → True.
    """
    iar = emulator.screenshot()
    result: dict[str, bool] = {}
    for di in sorted(_WAR_DECK_INDICATORS.keys()):
        all_match = True
        for r, g, b, x, y in _WAR_DECK_INDICATORS[di]:
            bgr = iar[y][x]
            actual = [int(bgr[2]), int(bgr[1]), int(bgr[0])]
            if not pixel_is_equal(actual, [r, g, b], tol=_WAR_DECK_INDICATOR_TOL):
                all_match = False
                break
        result[f"deck{di}"] = not all_match
    return result


def check_if_can_war_battle(emulator) -> bool:
    """False when the 'Start War Battle' button shows the greyed-out (no battles left) look."""
    iar = emulator.screenshot()
    pixels = [
        (iar[400][230], (202, 202, 202)),
        (iar[401][302], (202, 202, 202)),
        (iar[432][306], (193, 193, 193)),
        (iar[430][229], (193, 193, 193)),
    ]
    for bgr, (r, g, b) in pixels:
        actual = [int(bgr[2]), int(bgr[1]), int(bgr[0])]
        if not pixel_is_equal(actual, [r, g, b], tol=15):
            return True
    return False


def clan_button_pixel_is_active_green(pixel) -> bool:
    """Active Claim/Donate buttons (BGR). Grayscale templates still need a color gate."""
    b, g, r = int(pixel[0]), int(pixel[1]), int(pixel[2])
    return g > 100 and g > r + 15 and g > b + 15


def clan_button_pixel_is_active_yellow(pixel) -> bool:
    """Active Request footer / confirm buttons (BGR)."""
    b, g, r = int(pixel[0]), int(pixel[1]), int(pixel[2])
    return r > 160 and g > 120 and r > b + 40 and g > b + 20


def check_for_more_clan_chat_card_options(emulator) -> bool:
    """True if the 'scroll up for more requests' indicator is visible above the chat feed."""
    coord = find_image(
        emulator.screenshot(),
        "more_clan_chat_card_options",
        tolerance=0.9,
        subcrop=MORE_CLAN_CHAT_CARD_OPTIONS_SUBCROP,
    )
    return coord is not None


def check_if_on_clan_chat(emulator) -> bool:
    iar = emulator.screenshot()
    pixels = [
        iar[5][5],
        iar[628][415],
        iar[612][177],
        iar[44][322],
        iar[19][321],
        iar[620][254],
        iar[612][161],
        iar[584][204],
    ]
    colors = [
        [141, 85, 69],
        [105, 85, 71],
        [255, 175, 78],
        [237, 215, 201],
        [245, 231, 222],
        [107, 86, 72],
        [109, 87, 73],
        [160, 128, 108],
    ]
    for i, p in enumerate(pixels):
        if not pixel_is_equal(p, colors[i], tol=25):
            return False
    return True


# ===== Popups ==========================================================

CARD_MASTERY_COORD = (340, 440)
CARD_MASTERY_BGR = (95, 214, 251)
CARD_MASTERY_PIXEL_TOLERANCE = 15


def card_mastery_rewards_exist(emulator):
    screenshot = emulator.screenshot()

    x, y = CARD_MASTERY_COORD
    pixel = screenshot[y][x]

    return pixel_is_equal(pixel, CARD_MASTERY_BGR, CARD_MASTERY_PIXEL_TOLERANCE)


def check_for_inventory_full_popup(emulator):
    iar = emulator.screenshot()
    pixels = [
        iar[410][220],
        iar[420][225],
        iar[416][225],
        iar[418][230],
        iar[420][240],
        iar[430][250],
        iar[435][260],
        iar[427][270],
        iar[429][280],
        iar[435][290],
    ]
    colors = [
        [255, 187, 105],
        [255, 187, 105],
        [255, 187, 105],
        [244, 233, 220],
        [60, 52, 43],
        [255, 175, 78],
        [255, 175, 78],
        [255, 255, 255],
        [241, 165, 74],
        [255, 175, 78],
    ]
    for i, c in enumerate(colors):
        if not pixel_is_equal(c, pixels[i], tol=15):
            return False
    return True


# ===== Deck ============================================================


def is_deck_full(emulator) -> bool:
    iar = numpy.asarray(emulator.screenshot())
    pixels = [
        iar[172][43],
        iar[172][130],
        iar[172][216],
        iar[172][302],
        iar[310][43],
        iar[311][130],
        iar[309][216],
        iar[309][302],
    ]
    valid_colors = [
        [175, 5, 179],
        [178, 5, 182],
        [178, 5, 183],
        [188, 2, 194],
        [185, 4, 191],
        [197, 2, 209],
        [193, 2, 203],
    ]
    return all(any(pixel_is_equal(valid_color, p, tol=40) for valid_color in valid_colors) for p in pixels)


def is_single_deck_layout_by_pixel(emulator) -> bool:
    iar = numpy.asarray(emulator.screenshot())
    pixel_coords = [(99, 165), (117, 166), (99, 313), (117, 313)]
    expected_colors = [[141, 29, 0], [147, 34, 0], [145, 31, 4], [149, 34, 3]]
    return all(
        pixel_is_equal(expected, actual, tol=45)
        for (x, y), expected in zip(pixel_coords, expected_colors)
        for actual in [iar[y][x]]
    )


# ===== Upgrade ========================================================


def pixel_indicates_upgradable(bgr):
    b, g, r = bgr
    return g >= 240 and b <= 120 and r <= 40
