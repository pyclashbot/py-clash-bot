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


# ===== Deck page game types ============================================
# The card/deck page looks different per game type (Trophy Road, Classic 1v1,
# Classic 2v2). These sample the mode banner so randomize_deck can route.
# emulator.screenshot() is BGR, so colors below are stored [B, G, R] (the
# captured values were r,g,b) and sampled image[y][x].


def check_if_on_trophy_road_deck_page(emulator) -> bool:
    """True if the card/deck page is showing the Trophy Road game type."""
    image = emulator.screenshot()
    pixels = [
        image[102][48],
        image[97][63],
        image[128][71],
        image[116][58],
        image[109][50],
    ]
    colors = [
        [255, 255, 255],
        [155, 63, 4],
        [237, 99, 0],
        [255, 255, 255],
        [255, 255, 255],
    ]
    return all_pixels_are_equal(pixels, colors, 25)


def check_if_on_classic_1v1_deck_page(emulator) -> bool:
    """True if the card/deck page is showing the Classic 1v1 game type."""
    image = emulator.screenshot()
    pixels = [
        image[101][23],
        image[107][92],
        image[101][49],
        image[109][51],
        image[116][51],
    ]
    colors = [
        [195, 45, 44],
        [190, 44, 41],
        [255, 255, 255],
        [255, 255, 255],
        [255, 255, 255],
    ]
    return all_pixels_are_equal(pixels, colors, 25)


def check_if_on_classic_2v2_deck_page(emulator) -> bool:
    """True if the card/deck page is showing the Classic 2v2 game type."""
    image = emulator.screenshot()
    pixels = [
        image[99][22],
        image[102][85],
        image[99][333],
        image[103][391],
        image[101][50],
        image[108][54],
        image[115][50],
    ]
    colors = [
        [197, 45, 45],
        [194, 45, 43],
        [197, 45, 45],
        [194, 45, 43],
        [255, 255, 255],
        [255, 255, 255],
        [255, 255, 255],
    ]
    return all_pixels_are_equal(pixels, colors, 25)


def check_if_on_confirm_randomize_deck_page(emulator) -> bool:
    """True if the "replace deck?" confirm dialog is up after randomizing a full deck."""
    image = emulator.screenshot()
    pixels = [
        image[379][105],
        image[388][252],
        image[344][247],
        image[261][101],
        image[416][80],
    ]
    colors = [
        [98, 95, 252],
        [255, 187, 104],
        [243, 238, 227],
        [243, 238, 227],
        [243, 238, 227],
    ]
    return all_pixels_are_equal(pixels, colors, 25)


# ===== Clan voyage =====================================================

# (x, y) screen coord -> expected RGB color for the clan voyage screen.
CLAN_VOYAGE_PIXELS: list[tuple[tuple[int, int], list[int]]] = [
    ((49, 603), [73, 87, 108]),
    ((175, 603), [78, 175, 255]),
    ((239, 605), [78, 175, 255]),
    ((30, 120), [20, 102, 223]),
    ((339, 121), [20, 102, 221]),
    ((240, 592), [102, 185, 251]),
    ((15, 608), [73, 87, 108]),
]


def check_if_on_clan_voyage(emulator) -> bool:
    """Checks if the user is on the clan voyage screen.

    Returns True if the expected clan-voyage UI pixels are present, else False.
    """
    iar_bgr = emulator.screenshot()
    if iar_bgr is None:
        return False

    # Flip to RGB so the expected colors read in natural (r, g, b) order.
    iar = iar_bgr[..., ::-1]

    pixels = [iar[y][x].tolist() for (x, y), _ in CLAN_VOYAGE_PIXELS]
    colors = [expected for _, expected in CLAN_VOYAGE_PIXELS]

    return all_pixels_are_equal(pixels, colors, 25)


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

    # Same 8 landmarks as colors1, but on some app/emulator layouts pixel [116][59]
    # is the orange banner (BGR ~[222,85,0]) instead of white. Sampled off a live
    # card page that colors1/colors2 missed on that one pixel.
    colors3 = [
        [222, 0, 235],
        [222, 85, 0],
        [203, 137, 44],
        [195, 126, 34],
        [255, 255, 255],
        [255, 255, 255],
        [177, 103, 15],
        [178, 104, 15],
    ]

    if all_pixels_are_equal(pixels, colors1, tol=25):
        return True

    if all_pixels_are_equal(pixels, colors2, tol=25):
        return True

    if all_pixels_are_equal(pixels, colors3, tol=25):
        return True

    return False


def check_for_card_page_ok_button(emulator) -> bool:
    """True when the card-page 'OK' button is on screen (orange button, white text).

    BGR pixels sampled off a live card page (values are reversed from the RGB the
    /show-emulator-image skill reports).
    """
    iar = emulator.screenshot()

    pixels = [
        iar[606][171],
        iar[607][188],
        iar[609][212],
        iar[613][231],
        iar[613][243],
    ]

    colors = [
        [255, 175, 78],
        [255, 175, 78],
        [255, 255, 254],
        [255, 175, 78],
        [255, 175, 78],
    ]

    return all_pixels_are_equal(pixels, colors, tol=25)


def check_for_champion_card_upgrade_position(emulator) -> bool:
    """True when the card being upgraded is a champion (its upgrade button sits in a
    different position than normal cards).

    BGR pixels sampled off a live champion card (values reversed from the RGB the
    /show-emulator-image skill reports) — the green champion upgrade button.
    """
    iar = emulator.screenshot()

    pixels = [
        iar[530][203],
        iar[532][273],
        iar[565][212],
        iar[565][250],
        iar[565][274],
    ]

    colors = [
        [119, 235, 107],
        [119, 235, 107],
        [41, 149, 21],
        [41, 149, 21],
        [41, 149, 21],
    ]

    return all_pixels_are_equal(pixels, colors, tol=25)


# Princess card overlay fingerprints. Coords are (y, x) to match iar[y][x];
# colors are BGR (reversed from the RGB the /show-emulator-image skill reports).
# Exposed as data so debug tooling can report which pixel failed and why.
PRINCESS_FINGERPRINT_TOL = 25
PRINCESS_FINGERPRINTS: dict[str, tuple[list[tuple[int, int]], list[list[int]]]] = {
    "info location #1": (
        [(512, 306), (515, 340), (515, 369), (523, 343), (523, 329), (523, 363)],
        [[255, 187, 105], [255, 187, 105], [255, 187, 105], [255, 255, 255], [255, 254, 254], [255, 175, 78]],
    ),
    "info location #2": (
        [(320, 308), (332, 307), (333, 311), (330, 364), (318, 369), (318, 371)],
        [[255, 187, 105], [255, 175, 78], [255, 175, 78], [255, 175, 78], [255, 187, 105], [255, 187, 105]],
    ),
    # Blue info button at the top position (same spot upgrade location #1 occupies
    # when the card is upgradable); includes a white-text pixel for distinctiveness.
    "info location #3": (
        [(296, 310), (308, 307), (311, 372), (303, 367), (297, 342), (305, 330)],
        [[255, 187, 105], [255, 175, 78], [255, 175, 78], [255, 187, 105], [255, 187, 105], [255, 255, 255]],
    ),
    "upgrade location #1": (
        [(296, 311), (296, 330), (298, 374), (296, 358), (297, 367)],
        [[119, 235, 107], [98, 194, 89], [119, 235, 107], [250, 254, 250], [201, 226, 198]],
    ),
    "upgrade location #2": (
        [(510, 308), (513, 371), (513, 378), (513, 320), (518, 351), (513, 362)],
        [[119, 235, 107], [119, 235, 107], [119, 235, 107], [254, 255, 254], [255, 255, 255], [248, 253, 248]],
    ),
}


def _princess_fingerprint_matches(emulator, name: str) -> bool:
    """True when every sampled pixel of the named princess fingerprint matches."""
    coords, colors = PRINCESS_FINGERPRINTS[name]
    iar = emulator.screenshot()
    pixels = [iar[y][x] for y, x in coords]
    return all_pixels_are_equal(pixels, colors, tol=PRINCESS_FINGERPRINT_TOL)


def check_for_princess_card_info_button_location_1(emulator) -> bool:
    """True when the princess card's info button is on screen (blue button, white text)."""
    return _princess_fingerprint_matches(emulator, "info location #1")


def check_for_princess_card_info_button_location_2(emulator) -> bool:
    """True when the princess card's info button is in its alternate (upper) position."""
    return _princess_fingerprint_matches(emulator, "info location #2")


def check_for_princess_card_info_button_location_3(emulator) -> bool:
    """True when the princess card's info button is at the top position (blue button)."""
    return _princess_fingerprint_matches(emulator, "info location #3")


def check_for_princess_upgrade_location_1(emulator) -> bool:
    """True when the princess card's upgrade button is in its first position."""
    return _princess_fingerprint_matches(emulator, "upgrade location #1")


def check_for_princess_upgrade_location_2(emulator) -> bool:
    """True when the princess card's upgrade button is in its second (lower) position."""
    return _princess_fingerprint_matches(emulator, "upgrade location #2")


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


def check_for_free_offer_confirmation_condition_1(emulator) -> bool:
    """True if the free-offer confirmation popup is open (e.g. "Get Gems? FREE!").

    Fingerprints the green FREE button, the red close X, and the popup's light
    border. emulator.screenshot() is BGR, so colors are stored [B, G, R] (the
    captured values were r,g,b).
    """
    iar = emulator.screenshot()
    pixels = [
        iar[390][178],
        iar[387][203],
        iar[391][241],
        iar[401][179],
        iar[407][238],
        iar[213][343],
        iar[207][348],
        iar[253][78],
        iar[394][316],
        iar[283][340],
    ]
    colors = [
        [119, 235, 107],
        [119, 235, 107],
        [119, 235, 107],
        [73, 228, 58],
        [73, 228, 58],
        [49, 53, 254],
        [249, 249, 249],
        [243, 238, 227],
        [243, 238, 227],
        [243, 238, 227],
    ]
    return all_pixels_are_equal(pixels, colors, 25)


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


def _matches_war_original(iar) -> bool:
    """Original war-page fingerprint (pink river-race banner + bottom-of-page nav).

    Pixels compared in raw screenshot/BGR order.
    """
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


# Alternate war-page fingerprint, sampled with the click picker on the green
# "Training Day" river-race variant that the original pink-banner palette misses.
# (x, y, r, g, b) in RGB; each sampled pixel is flipped from BGR before comparing.
_WAR_PAGE_ALT_PIXELS: tuple[tuple[int, int, int, int, int], ...] = (
    (357, 53, 152, 117, 254),
    (379, 57, 154, 119, 253),
    (396, 41, 162, 129, 255),
    (380, 30, 129, 161, 177),
    (21, 606, 74, 88, 110),
    (68, 606, 74, 88, 110),
    (113, 608, 74, 88, 109),
    (156, 604, 75, 89, 110),
    (186, 604, 104, 187, 255),
    (225, 607, 78, 175, 255),
    (258, 608, 74, 88, 109),
    (315, 613, 73, 87, 108),
    (367, 612, 73, 87, 109),
    (399, 612, 73, 87, 109),
    (202, 604, 255, 255, 255),
)


def _matches_war_alt(iar) -> bool:
    """Alternate war-page fingerprint (see _WAR_PAGE_ALT_PIXELS)."""
    for x, y, r, g, b in _WAR_PAGE_ALT_PIXELS:
        bgr = iar[y][x]
        actual = [int(bgr[2]), int(bgr[1]), int(bgr[0])]
        if not pixel_is_equal(actual, [r, g, b], tol=25):
            return False
    return True


# A third war-page fingerprint, sampled with the click picker on a blue river-race
# variant the original and alt palettes miss: the blue-grey banner edge plus the
# purple banner left/right edges. (x, y, r, g, b) in RGB; flipped from BGR to compare.
_WAR_PAGE_ALT2_PIXELS: tuple[tuple[int, int, int, int, int], ...] = (
    (238, 601, 75, 111, 146),
    (238, 609, 77, 115, 150),
    (319, 614, 79, 117, 152),
    (316, 605, 77, 113, 148),
    (322, 585, 73, 106, 139),
    (18, 47, 124, 79, 255),
    (18, 37, 141, 101, 255),
    (19, 24, 145, 107, 255),
    (20, 18, 147, 110, 255),
    (398, 53, 136, 96, 254),
    (400, 42, 144, 108, 255),
    (400, 33, 157, 124, 255),
)


def _matches_war_alt2(iar) -> bool:
    """Third war-page fingerprint (see _WAR_PAGE_ALT2_PIXELS)."""
    for x, y, r, g, b in _WAR_PAGE_ALT2_PIXELS:
        bgr = iar[y][x]
        actual = [int(bgr[2]), int(bgr[1]), int(bgr[0])]
        if not pixel_is_equal(actual, [r, g, b], tol=25):
            return False
    return True


def check_if_on_war(emulator) -> bool:
    """True when on the clan-war / river-race page.

    Independent pixel fingerprints are OR'd: any one matching confirms the war
    page, all must fail to rule it out. The river-race banner color varies by day,
    so add new palettes here rather than tightening existing ones.
    """
    iar = emulator.screenshot()
    return _matches_war_original(iar) or _matches_war_alt(iar) or _matches_war_alt2(iar)


# (x, y, r, g, b) sampled from the clan-war results popup ("war boot") — e.g. the
# "Your Clan didn't finish!" screen with a reward chest. This modal covers the main
# menu and intercepts navigation to the war page, so it is detected after the nav
# clicks and then clicked through (see nav.handle_war_boot).
_WAR_BOOT_PIXELS: tuple[tuple[int, int, int, int, int], ...] = (
    (23, 601, 75, 89, 111),
    (60, 599, 75, 89, 111),
    (123, 608, 74, 88, 109),
    (277, 608, 74, 88, 109),
    (333, 609, 74, 88, 109),
    (407, 613, 73, 87, 108),
    (180, 608, 78, 175, 255),
    (206, 606, 111, 134, 153),
    (232, 606, 78, 175, 255),
    (148, 390, 255, 190, 43),
    (217, 390, 255, 190, 43),
    (225, 371, 255, 196, 54),
)


# A second war-boot variant fingerprint (RGB, same convention as above): gold reward
# text, white highlights, and the dark bottom button bar of the results popup.
_WAR_BOOT_PIXELS_ALT: tuple[tuple[int, int, int, int, int], ...] = (
    (148, 392, 255, 190, 43),
    (165, 393, 255, 190, 43),
    (178, 394, 255, 190, 43),
    (151, 423, 255, 190, 43),
    (157, 406, 224, 167, 38),
    (165, 411, 255, 255, 254),
    (178, 411, 255, 255, 255),
    (203, 416, 255, 255, 255),
    (132, 608, 74, 88, 109),
    (274, 606, 74, 88, 110),
    (299, 606, 74, 88, 110),
    (184, 600, 104, 187, 255),
)


def _war_boot_pixels_match(iar, pixels: tuple[tuple[int, int, int, int, int], ...]) -> bool:
    """All `pixels` (x, y, r, g, b) match the BGR screenshot (flipped to RGB, tol 25)."""
    for x, y, r, g, b in pixels:
        bgr = iar[y][x]
        actual = [int(bgr[2]), int(bgr[1]), int(bgr[0])]
        if not pixel_is_equal(actual, [r, g, b], tol=25):
            return False
    return True


def check_if_on_war_boot(emulator) -> bool:
    """True when the clan-war results popup ("war boot") is covering the screen.

    Two fingerprint sets are kept for different popup variants; either set fully
    matching returns True.
    """
    iar = emulator.screenshot()
    return _war_boot_pixels_match(iar, _WAR_BOOT_PIXELS) or _war_boot_pixels_match(iar, _WAR_BOOT_PIXELS_ALT)


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


def check_if_on_card_upgrade_menu(emulator) -> bool:
    """True if the card-upgrade popup is open.

    Multi-point fingerprint of the popup's chrome -- the red X close button
    (top-right) and the blue cost/level rail down each side -- sampled off live
    open menus. A previous single-pixel check sat on the white X glyph in the
    middle of the close button and read black, so it never detected the open
    menu; sampling several stable points avoids that.
    """
    iar = emulator.screenshot()

    pixels = [
        iar[177][345],
        iar[183][345],
        iar[186][354],
        iar[180][354],
        iar[177][358],
        iar[188][350],
        iar[526][366],
        iar[483][367],
        iar[412][369],
        iar[344][369],
        iar[261][370],
        iar[210][369],
        iar[539][50],
        iar[506][49],
        iar[467][51],
    ]

    colors = [
        [135, 133, 253],
        [70, 67, 252],
        [4, 4, 4],
        [213, 213, 213],
        [135, 133, 253],
        [38, 40, 240],
        [110, 53, 19],
        [112, 54, 19],
        [116, 58, 20],
        [116, 58, 20],
        [120, 59, 21],
        [117, 58, 20],
        [123, 61, 22],
        [126, 64, 22],
        [120, 59, 21],
    ]

    if all_pixels_are_equal(pixels, colors, tol=30):
        return True

    # Alternate layout (e.g. champion cards): red X close button (top-right) plus
    # the dark-blue bottom rail and its gold accent. BGR, sampled off a live menu.
    pixels2 = [
        iar[36][344],
        iar[36][353],
        iar[30][349],
        iar[30][357],
        iar[596][61],
        iar[601][206],
        iar[608][356],
        iar[604][258],
    ]

    colors2 = [
        [32, 34, 225],
        [38, 37, 225],
        [251, 250, 251],
        [67, 66, 245],
        [76, 24, 21],
        [76, 24, 21],
        [76, 24, 21],
        [0, 108, 207],
    ]

    return all_pixels_are_equal(pixels2, colors2, tol=30)
