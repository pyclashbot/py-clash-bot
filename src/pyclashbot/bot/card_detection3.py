import random
import math
import numpy
from pyclashbot.detection.image_rec import pixel_is_equal
from pyclashbot.memu.client import screenshot

card_color_data = {
    # checked
    "arrows": {
        "Red": 1,
        "Orange": 1621,
        "Yellow": 651,
        "Green": 10,
        "Blue": 8,
        "Indigo": 498,
        "Violet": 475,
    },
    "barb_hut": {
        "Red": 1,
        "Orange": 494,
        "Yellow": 152,
        "Green": 420,
        "Blue": 41,
        "Indigo": 1383,
        "Violet": 773,
    },
    "barb_barrel": {
        "Red": 0,
        "Orange": 409,
        "Yellow": 205,
        "Green": 64,
        "Blue": 270,
        "Indigo": 1598,
        "Violet": 718,
    },
    "bomb_tower": {
        "Red": 1,
        "Orange": 66,
        "Yellow": 84,
        "Green": 29,
        "Blue": 263,
        "Indigo": 2123,
        "Violet": 698,
    },
    "battle_ram": {
        "Red": 1,
        "Orange": 601,
        "Yellow": 182,
        "Green": 711,
        "Blue": 0,
        "Indigo": 1626,
        "Violet": 143,
    },
    "cannon": {
        "Red": 1,
        "Orange": 184,
        "Yellow": 125,
        "Green": 389,
        "Blue": 0,
        "Indigo": 1621,
        "Violet": 944,
    },
    "furnace": {
        "Red": 1,
        "Orange": 35,
        "Yellow": 97,
        "Green": 292,
        "Blue": 24,
        "Indigo": 2331,
        "Violet": 484,
    },
    "freeze": {
        "Red": 0,
        "Orange": 840,
        "Yellow": 1961,
        "Green": 118,
        "Blue": 0,
        "Indigo": 240,
        "Violet": 105,
    },
    "goblin_drill": {
        "Red": 0,
        "Orange": 192,
        "Yellow": 150,
        "Green": 309,
        "Blue": 0,
        "Indigo": 2196,
        "Violet": 417,
    },
    "goblin_cage": {
        "Red": 0,
        "Orange": 193,
        "Yellow": 104,
        "Green": 1009,
        "Blue": 53,
        "Indigo": 1476,
        "Violet": 429,
    },
    "graveyard": {
        "Red": 19,
        "Orange": 49,
        "Yellow": 167,
        "Green": 28,
        "Blue": 0,
        "Indigo": 2345,
        "Violet": 656,
    },
    "goblin_barrel": {
        "Red": 1,
        "Orange": 6,
        "Yellow": 641,
        "Green": 968,
        "Blue": 10,
        "Indigo": 1213,
        "Violet": 425,
    },
    "miner": {
        "Red": 24,
        "Orange": 233,
        "Yellow": 131,
        "Green": 169,
        "Blue": 1,
        "Indigo": 1859,
        "Violet": 847,
    },
    "skeleton_barrel": {
        "Red": 1,
        "Orange": 513,
        "Yellow": 995,
        "Green": 81,
        "Blue": 0,
        "Indigo": 1411,
        "Violet": 263,
    },
    "wall_breakers": {
        "Red": 2,
        "Orange": 508,
        "Yellow": 116,
        "Green": 476,
        "Blue": 0,
        "Indigo": 1799,
        "Violet": 363,
    },
    "snowball": {
        "Red": 0,
        "Orange": 1046,
        "Yellow": 929,
        "Green": 253,
        "Blue": 0,
        "Indigo": 948,
        "Violet": 88,
    },
    "princess": {
        "Red": 14,
        "Orange": 496,
        "Yellow": 129,
        "Green": 178,
        "Blue": 0,
        "Indigo": 1790,
        "Violet": 657,
    },
    "tombstone": {
        "Red": 0,
        "Orange": 889,
        "Yellow": 370,
        "Green": 1466,
        "Blue": 0,
        "Indigo": 445,
        "Violet": 94,
    },
    "royal_delivery": {
        "Red": 16,
        "Orange": 222,
        "Yellow": 184,
        "Green": 169,
        "Blue": 94,
        "Indigo": 2043,
        "Violet": 536,
    },
    "hog": {
        "Red": 1,
        "Orange": 176,
        "Yellow": 87,
        "Green": 233,
        "Blue": 0,
        "Indigo": 2360,
        "Violet": 407,
    },
    "earthquake": {
        "Red": 0,
        "Orange": 31,
        "Yellow": 88,
        "Green": 472,
        "Blue": 3,
        "Indigo": 2518,
        "Violet": 152,
    },
    "mortar": {
        "Red": 1,
        "Orange": 1046,
        "Yellow": 401,
        "Green": 691,
        "Blue": 73,
        "Indigo": 837,
        "Violet": 215,
    },
    "log": {
        "Red": 31,
        "Orange": 510,
        "Yellow": 559,
        "Green": 182,
        "Blue": 2,
        "Indigo": 1455,
        "Violet": 525,
    },
    "tesla": {
        "Red": 115,
        "Orange": 1590,
        "Yellow": 273,
        "Green": 32,
        "Blue": 144,
        "Indigo": 911,
        "Violet": 199,
    },
    "poison": {
        "Red": 0,
        "Orange": 1,
        "Yellow": 13,
        "Green": 0,
        "Blue": 894,
        "Indigo": 2012,
        "Violet": 344,
    },
    "royal_hogs": {
        "Red": 10,
        "Orange": 82,
        "Yellow": 102,
        "Green": 663,
        "Blue": 0,
        "Indigo": 1884,
        "Violet": 523,
    },
    "ram_rider": {
        "Red": 36,
        "Orange": 133,
        "Yellow": 50,
        "Green": 27,
        "Blue": 308,
        "Indigo": 1709,
        "Violet": 1001,
    },
    "inferno_tower": {
        "Red": 1,
        "Orange": 104,
        "Yellow": 113,
        "Green": 71,
        "Blue": 57,
        "Indigo": 1916,
        "Violet": 1002,
    },
    "goblin_hut": {
        "Red": 1,
        "Orange": 225,
        "Yellow": 359,
        "Green": 181,
        "Blue": 20,
        "Indigo": 1946,
        "Violet": 532,
    },
    "lightning": {
        "Red": 129,
        "Orange": 1386,
        "Yellow": 1014,
        "Green": 33,
        "Blue": 0,
        "Indigo": 520,
        "Violet": 182,
    },
    "rocket": {
        "Red": 1,
        "Orange": 428,
        "Yellow": 687,
        "Green": 221,
        "Blue": 30,
        "Indigo": 933,
        "Violet": 964,
    },
    "xbow": {
        "Red": 1,
        "Orange": 1034,
        "Yellow": 88,
        "Green": 114,
        "Blue": 10,
        "Indigo": 1349,
        "Violet": 668,
    },
    "rage": {
        "Red": 1,
        "Orange": 1,
        "Yellow": 358,
        "Green": 9,
        "Blue": 0,
        "Indigo": 946,
        "Violet": 1949,
    },
    "zap": {
        "Red": 115,
        "Orange": 2227,
        "Yellow": 232,
        "Green": 165,
        "Blue": 0,
        "Indigo": 420,
        "Violet": 105,
    },
    # cards that dont matter
    "electro_spirit": {
        "Red": 745,
        "Orange": 609,
        "Yellow": 471,
        "Green": 128,
        "Blue": 0,
        "Indigo": 518,
        "Violet": 793,
    },
    "bomber": {
        "Red": 1,
        "Orange": 523,
        "Yellow": 181,
        "Green": 467,
        "Blue": 314,
        "Indigo": 1335,
        "Violet": 443,
    },
    "ice_spirit": {
        "Red": 13,
        "Orange": 1290,
        "Yellow": 924,
        "Green": 186,
        "Blue": 0,
        "Indigo": 761,
        "Violet": 90,
    },
    "heal_spirit": {
        "Red": 0,
        "Orange": 1,
        "Yellow": 114,
        "Green": 113,
        "Blue": 2110,
        "Indigo": 422,
        "Violet": 504,
    },
    # "fire_spirit": {
    #     "Red": 1,
    #     "Orange": 0,
    #     "Yellow": 210,
    #     "Green": 225,
    #     "Blue": 680,
    #     "Indigo": 1245,
    #     "Violet": 903,
    # },
    "skeletons": {
        "Red": 2,
        "Orange": 277,
        "Yellow": 224,
        "Green": 459,
        "Blue": 0,
        "Indigo": 1582,
        "Violet": 720,
    },
    "bats": {
        "Red": 1,
        "Orange": 440,
        "Yellow": 189,
        "Green": 423,
        "Blue": 0,
        "Indigo": 1873,
        "Violet": 338,
    },
    "goblins": {
        "Red": 0,
        "Orange": 71,
        "Yellow": 180,
        "Green": 1330,
        "Blue": 6,
        "Indigo": 1181,
        "Violet": 496,
    },
    "ice_golem": {
        "Red": 72,
        "Orange": 1569,
        "Yellow": 679,
        "Green": 291,
        "Blue": 0,
        "Indigo": 422,
        "Violet": 231,
    },
    "goblin_gang": {
        "Red": 35,
        "Orange": 66,
        "Yellow": 157,
        "Green": 1592,
        "Blue": 1,
        "Indigo": 945,
        "Violet": 468,
    },
    "firecraker": {
        "Red": 117,
        "Orange": 333,
        "Yellow": 111,
        "Green": 656,
        "Blue": 12,
        "Indigo": 1395,
        "Violet": 640,
    },
    "guards": {
        "Red": 10,
        "Orange": 260,
        "Yellow": 225,
        "Green": 568,
        "Blue": 0,
        "Indigo": 1966,
        "Violet": 235,
    },
    "skeleton_army": {
        "Red": 1,
        "Orange": 5,
        "Yellow": 186,
        "Green": 244,
        "Blue": 0,
        "Indigo": 1498,
        "Violet": 1330,
    },
    "royal_ghost": {
        "Red": 4,
        "Orange": 1073,
        "Yellow": 1085,
        "Green": 13,
        "Blue": 281,
        "Indigo": 237,
        "Violet": 571,
    },
    "mega_minion": {
        "Red": 7,
        "Orange": 366,
        "Yellow": 205,
        "Green": 573,
        "Blue": 0,
        "Indigo": 1841,
        "Violet": 272,
    },
    "spear_goblins": {
        "Red": 67,
        "Orange": 521,
        "Yellow": 226,
        "Green": 1356,
        "Blue": 87,
        "Indigo": 773,
        "Violet": 234,
    },
    "mini_pekka": {
        "Red": 1,
        "Orange": 1125,
        "Yellow": 245,
        "Green": 173,
        "Blue": 104,
        "Indigo": 1506,
        "Violet": 110,
    },
    "dart_goblin": {
        "Red": 2,
        "Orange": 126,
        "Yellow": 128,
        "Green": 1035,
        "Blue": 259,
        "Indigo": 1550,
        "Violet": 164,
    },
    "night_witch": {
        "Red": 23,
        "Orange": 403,
        "Yellow": 195,
        "Green": 699,
        "Blue": 0,
        "Indigo": 1617,
        "Violet": 327,
    },
    "minions": {
        "Red": 119,
        "Orange": 615,
        "Yellow": 305,
        "Green": 994,
        "Blue": 0,
        "Indigo": 1154,
        "Violet": 77,
    },
    "archers": {
        "Red": 1,
        "Orange": 18,
        "Yellow": 110,
        "Green": 197,
        "Blue": 5,
        "Indigo": 1698,
        "Violet": 1235,
    },
    "dark_knight": {
        "Red": 1,
        "Orange": 117,
        "Yellow": 363,
        "Green": 759,
        "Blue": 6,
        "Indigo": 1778,
        "Violet": 240,
    },
    "ice_wizard": {
        "Red": 24,
        "Orange": 809,
        "Yellow": 242,
        "Green": 415,
        "Blue": 0,
        "Indigo": 1185,
        "Violet": 589,
    },
    "knight": {
        "Red": 1,
        "Orange": 274,
        "Yellow": 250,
        "Green": 189,
        "Blue": 134,
        "Indigo": 1487,
        "Violet": 929,
    },
    "battle_healer": {
        "Red": 1,
        "Orange": 14,
        "Yellow": 218,
        "Green": 118,
        "Blue": 28,
        "Indigo": 1159,
        "Violet": 1726,
    },
    "lumberjack": {
        "Red": 10,
        "Orange": 538,
        "Yellow": 359,
        "Green": 140,
        "Blue": 416,
        "Indigo": 1086,
        "Violet": 715,
    },
    "skeleton_dragons": {
        "Red": 14,
        "Orange": 717,
        "Yellow": 337,
        "Green": 582,
        "Blue": 0,
        "Indigo": 1016,
        "Violet": 598,
    },
    "baby_dragon": {
        "Red": 0,
        "Orange": 1032,
        "Yellow": 593,
        "Green": 1066,
        "Blue": 106,
        "Indigo": 315,
        "Violet": 152,
    },
    "magic_archer": {
        "Red": 21,
        "Orange": 118,
        "Yellow": 295,
        "Green": 365,
        "Blue": 7,
        "Indigo": 1642,
        "Violet": 816,
    },
    "electro_wizard": {
        "Red": 4,
        "Orange": 223,
        "Yellow": 303,
        "Green": 939,
        "Blue": 7,
        "Indigo": 1180,
        "Violet": 608,
    },
    "musketeer": {
        "Red": 1,
        "Orange": 625,
        "Yellow": 446,
        "Green": 138,
        "Blue": 1,
        "Indigo": 1705,
        "Violet": 348,
    },
    "flying_machine": {
        "Red": 0,
        "Orange": 282,
        "Yellow": 166,
        "Green": 164,
        "Blue": 33,
        "Indigo": 1900,
        "Violet": 719,
    },
    "valkyrie": {
        "Red": 1,
        "Orange": 21,
        "Yellow": 116,
        "Green": 170,
        "Blue": 308,
        "Indigo": 1749,
        "Violet": 899,
    },
    "wizard": {
        "Red": 1,
        "Orange": 204,
        "Yellow": 187,
        "Green": 148,
        "Blue": 0,
        "Indigo": 2287,
        "Violet": 437,
    },
    "zappies": {
        "Red": 2,
        "Orange": 493,
        "Yellow": 583,
        "Green": 584,
        "Blue": 0,
        "Indigo": 1458,
        "Violet": 144,
    },
    "barbarians": {
        "Red": 2,
        "Orange": 167,
        "Yellow": 150,
        "Green": 176,
        "Blue": 962,
        "Indigo": 1021,
        "Violet": 786,
    },
    "hunter": {
        "Red": 8,
        "Orange": 255,
        "Yellow": 200,
        "Green": 910,
        "Blue": 1,
        "Indigo": 1634,
        "Violet": 256,
    },
    "minion_horde": {
        "Red": 1,
        "Orange": 427,
        "Yellow": 396,
        "Green": 544,
        "Blue": 0,
        "Indigo": 1817,
        "Violet": 79,
    },
    "prince": {
        "Red": 1,
        "Orange": 71,
        "Yellow": 176,
        "Green": 265,
        "Blue": 0,
        "Indigo": 1956,
        "Violet": 795,
    },
    "executioner": {
        "Red": 1,
        "Orange": 292,
        "Yellow": 635,
        "Green": 461,
        "Blue": 0,
        "Indigo": 1412,
        "Violet": 463,
    },
    "electro_dragon": {
        "Red": 138,
        "Orange": 1410,
        "Yellow": 252,
        "Green": 1106,
        "Blue": 0,
        "Indigo": 272,
        "Violet": 86,
    },
    "balloon": {
        "Red": 1,
        "Orange": 773,
        "Yellow": 356,
        "Green": 156,
        "Blue": 53,
        "Indigo": 1562,
        "Violet": 363,
    },
    "witch": {
        "Red": 0,
        "Orange": 120,
        "Yellow": 125,
        "Green": 203,
        "Blue": 0,
        "Indigo": 2180,
        "Violet": 636,
    },
    "rascals": {
        "Red": 1,
        "Orange": 320,
        "Yellow": 469,
        "Green": 407,
        "Blue": 0,
        "Indigo": 1322,
        "Violet": 745,
    },
    "giant": {
        "Red": 1,
        "Orange": 43,
        "Yellow": 117,
        "Green": 230,
        "Blue": 474,
        "Indigo": 1513,
        "Violet": 886,
    },
    "bowler": {
        "Red": 54,
        "Orange": 1392,
        "Yellow": 316,
        "Green": 119,
        "Blue": 0,
        "Indigo": 482,
        "Violet": 901,
    },
    "giant_skeleton": {
        "Red": 0,
        "Orange": 727,
        "Yellow": 456,
        "Green": 423,
        "Blue": 0,
        "Indigo": 1280,
        "Violet": 378,
    },
    "royal_recruits": {
        "Red": 4,
        "Orange": 316,
        "Yellow": 338,
        "Green": 175,
        "Blue": 2,
        "Indigo": 1737,
        "Violet": 692,
    },
    "goblin_giant": {
        "Red": 20,
        "Orange": 433,
        "Yellow": 184,
        "Green": 1353,
        "Blue": 2,
        "Indigo": 978,
        "Violet": 294,
    },
    "mega_knight": {
        "Red": 23,
        "Orange": 507,
        "Yellow": 335,
        "Green": 295,
        "Blue": 0,
        "Indigo": 1905,
        "Violet": 199,
    },
    "pekka": {
        "Red": 2,
        "Orange": 251,
        "Yellow": 173,
        "Green": 512,
        "Blue": 117,
        "Indigo": 2018,
        "Violet": 191,
    },
    "royal_giant": {
        "Red": 5,
        "Orange": 106,
        "Yellow": 378,
        "Green": 250,
        "Blue": 357,
        "Indigo": 1526,
        "Violet": 642,
    },
    "sparky": {
        "Red": 5,
        "Orange": 386,
        "Yellow": 442,
        "Green": 94,
        "Blue": 88,
        "Indigo": 1579,
        "Violet": 670,
    },
    "electro_giant": {
        "Red": 85,
        "Orange": 294,
        "Yellow": 478,
        "Green": 135,
        "Blue": 212,
        "Indigo": 1657,
        "Violet": 403,
    },
    "elite_barbarians": {
        "Red": 0,
        "Orange": 200,
        "Yellow": 150,
        "Green": 511,
        "Blue": 128,
        "Indigo": 1753,
        "Violet": 522,
    },
    "golem": {
        "Red": 1,
        "Orange": 4,
        "Yellow": 138,
        "Green": 101,
        "Blue": 106,
        "Indigo": 2102,
        "Violet": 812,
    },
    "three_musketeers": {
        "Red": 82,
        "Orange": 1033,
        "Yellow": 132,
        "Green": 424,
        "Blue": 0,
        "Indigo": 993,
        "Violet": 600,
    },
}


PLAY_COORDS = {
    # done
    "spell": {
        "left": [(116, 140)],
        "right": [(302, 140)],
    },
    "hog": {
        "left": [(77, 281), (113, 286), (154, 283)],
        "right": [(257, 283), (300, 284), (353, 283)],
    },
    "turret": {
        "left": [(224, 300), (224, 334)],
        "right": [(224, 300), (224, 334)],
    },
    "miner": {
        "left": [(86, 156), (90, 104), (143, 113), (142, 153)],
        "right": [(274, 152), (276, 111), (339, 111), (323, 157)],
    },
    "goblin_barrel": {
        "left": [(115, 134), (115, 134), (60, 96)],
        "right": [(300, 137), (300, 137), (356, 106)],
    },
    "xbow": {
        "left": [(170, 288)],
        "right": [(254, 284)],
    },
    "spawner": {
        "left": [(69, 442), (158, 444), (166, 394)],
        "right": [(247, 396), (264, 440), (343, 442)],
    },
}


def identify_card_from_color_dict(color_dict):
    min_distance = float("inf")
    identified_card = None

    for card, card_colors in card_color_data.items():
        common_colors = set(color_dict.keys()) & set(card_colors.keys())

        total_distance = sum(
            math.sqrt(
                sum(
                    (color_dict[color] - card_colors[color]) ** 2
                    for color in common_colors
                )
            )
            for color_dict, card_colors in [(color_dict, card_colors)]
        )

        if total_distance < min_distance:
            min_distance = total_distance
            identified_card = card

    return identified_card


def colors_from_pixels(pixel_list):
    color_counts = {
        "Red": 0,
        "Orange": 0,
        "Yellow": 0,
        "Green": 0,
        "Blue": 0,
        "Indigo": 0,
        "Violet": 0,
    }

    for pixel in pixel_list:
        color = color_from_pixel(pixel)
        color_counts[color] += 1

    return color_counts


def color_from_pixel(pixel):
    COLORS = {
        "Red": [255, 0, 0],
        "Orange": [255, 165, 0],
        "Yellow": [255, 255, 0],
        "Green": [0, 128, 0],
        "Blue": [0, 0, 255],
        "Indigo": [75, 0, 130],
        "Violet": [148, 0, 211],
    }

    # Calculate the Euclidean distance between the pixel and each color
    distances = {
        color: math.sqrt(sum((a - b) ** 2 for a, b in zip(pixel, COLORS[color])))
        for color in COLORS
    }

    # Find the color with the minimum distance
    closest_color = min(distances, key=distances.get)

    return closest_color


def get_pixels_and_count(iar, topleft):
    width = 51
    height = 64
    pixels = []
    for x in range(width):
        for y in range(height):
            pixel = iar[topleft[1] + y][topleft[0] + x]
            pixels.append(pixel)
    return pixels


def identify_hand_cards(vm_index):
    iar = numpy.asarray(screenshot(vm_index))
    top_lefts = [
        [114, 528],
        [181, 528],
        [248, 528],
        [315, 528],
    ]

    card_ids = []

    for top_left in top_lefts:
        pixels = get_pixels_and_count(iar, top_left)
        color_dict = colors_from_pixels(pixels)
        id = identify_card_from_color_dict(color_dict)
        card_ids.append(id)

    return card_ids


def get_card_group(card_id) -> str:
    card_groups: dict[str, list[str]] = {
        "spell": [
            "earthquake",
            "fireball",
            "freeze",
            "poison",
            "arrows",
            "snowball",
            "zap",
            "rocket",
            "lightning",
            "log",
            "tornado",
            "graveyard",
        ],
        "turret": [
            "bomb_tower",
            "cannon",
            "tesla",
            "goblin_cage",
            "inferno_tower",
        ],
        "hog": [
            "battle_ram",
            "wall_breakers",
            "princess",
            "ram_rider",
            "skeleton_barrel",
            "hog",
            "royal_hogs",
        ],
        "miner": [
            "goblin_drill",
            "miner",
        ],
        "goblin_barrel": [
            "goblin_barrel",
        ],
        "xbow": [
            "xbow",
            "mortar",
        ],
        "spawner": [
            "tombstone",
            "goblin_hut",
            "barb_hut",
            "furnace",
        ],
    }

    for group, cards in card_groups.items():
        if card_id in cards:
            return group

    return "No group"


def calculate_play_coords(card_grouping: str, side_preference: str):
    if PLAY_COORDS.get(card_grouping):
        group_datum = PLAY_COORDS[card_grouping]
        if side_preference == "left" and "left" in group_datum:
            return random.choice(group_datum["left"])
        if side_preference == "right" and "right" in group_datum:
            return random.choice(group_datum["right"])
        if "coords" in group_datum:
            return random.choice(group_datum["coords"])

    if side_preference == "left":
        return (random.randint(60, 206), random.randint(281, 456))
    return (random.randint(210, 351), random.randint(281, 456))


def get_play_coords_for_card(vm_index, card_index, side_preference):
    # get the ID of this card(ram_rider, zap, etc)
    identity = identify_hand_cards(vm_index)[card_index]

    # get the grouping of this card (hog, turret, spell, etc)
    group = get_card_group(identity)

    # get the play coords of this grouping
    coords = calculate_play_coords(group, side_preference)

    return identity, coords


def check_which_cards_are_available(vm_index):
    iar = numpy.asarray(screenshot(vm_index))

    card_1_pixels = []
    card_2_pixels = []
    card_3_pixels = []
    card_4_pixels = []

    toplefts = [
        [133, 582],
        [199, 583],
        [266, 583],
        [334, 582],
    ]
    width = 20
    height = 20

    for i, topleft in enumerate(toplefts):
        for x in range(width):
            for y in range(height):
                x_coord = topleft[0] + x
                y_coord = topleft[1] + y

                if i == 0:
                    card_1_pixels.append(iar[y_coord][x_coord])
                if i == 1:
                    card_2_pixels.append(iar[y_coord][x_coord])
                if i == 2:
                    card_3_pixels.append(iar[y_coord][x_coord])
                if i == 3:
                    card_4_pixels.append(iar[y_coord][x_coord])

    purple_count_1 = count_purple_colors_in_pixel_list(card_1_pixels)
    purple_count_2 = count_purple_colors_in_pixel_list(card_2_pixels)
    purple_count_3 = count_purple_colors_in_pixel_list(card_3_pixels)
    purple_count_4 = count_purple_colors_in_pixel_list(card_4_pixels)

    card_exists_list = []

    if purple_count_1 > 25:
        card_exists_list.append(0)

    if purple_count_2 > 25:
        card_exists_list.append(1)

    if purple_count_3 > 25:
        card_exists_list.append(2)

    if purple_count_4 > 25:
        card_exists_list.append(3)

    return card_exists_list


def count_purple_colors_in_pixel_list(pixel_list):
    purple_color = [255, 43, 227]
    count = 0
    for p in pixel_list:
        if pixel_is_equal(p, purple_color, tol=30):
            count += 1

    return count


if __name__ == "__main__":
    while 1:
        print(check_which_cards_are_available(12))
