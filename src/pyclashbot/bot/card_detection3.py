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
    "fireball":{'Red': 0, 'Orange': 0, 'Yellow': 125, 'Green': 0, 'Blue': 1030, 'Indigo': 1331, 'Violet': 778},
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
    "inferno_tower2":{'Red': 0, 'Orange': 1, 'Yellow': 544, 'Green': 153, 'Blue': 0, 'Indigo': 2066, 'Violet': 500},
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

    print('\n')
    for i,top_left in enumerate(top_lefts):
        pixels = get_pixels_and_count(iar, top_left)
        color_dict = colors_from_pixels(pixels)
        id = identify_card_from_color_dict(color_dict)
        card_ids.append(id)

        print(i+1, id, color_dict)

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
            "inferno_tower2",
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
        print(identify_hand_cards(12))
