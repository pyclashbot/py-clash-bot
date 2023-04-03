import random
import time

from pyclashbot.detection import check_for_location, find_references
from pyclashbot.memu import get_file_count, make_reference_image_list, screenshot


"""Methods that have to do with the scanning of cards during a battle
"""


def get_card_images():
    """Method to get the images of the user's 4 current cards
    args:
        None
    returns:
        list: list of 4 images of the user's current cards
    """
    return [
        screenshot(region=[105, 550, 70, 90]),
        screenshot(region=[177, 550, 70, 90]),
        screenshot(region=[245, 550, 70, 90]),
        screenshot(region=[311, 550, 70, 90]),
    ]


def check_for_card(image, card_name=""):
    """Method to read the card image and get it's name
    args:
        image: image of the card
        card_name: name of the card to check for
    returns:
        bool: True if the card is the given card, False otherwise
    """

    folder_str = f"check_if_card_is_{card_name}"

    references = make_reference_image_list(
        get_file_count(
            f"check_if_card_is_{card_name}",
        )
    )

    locations = find_references(
        screenshot=image, folder=folder_str, names=references, tolerance=0.97
    )

    return check_for_location(locations)


def identify_cards():
    """Method to check the user's current cards and return a list of their names or "unknown" if the card is not recognized
    args:
        None
    returns:
        list: list of the names of the user's current cards
    """
    card_images = get_card_images()

    return [identify_card(image) for image in card_images]


def identify_card(image):
    """Method to identify the name of the given card image
    args:
        image: image of the card
    returns:
        str: name of the card"""

    # make a list of cards the bot knows about
    card_list = [
        "arrows",
        "barbbarrel",
        "wallbreakers",
        "princess",
        "miner",
        "skeletonbarrel",
        "goblinbarrel",
        "hog",
        "battleram",
        "bombtower",
        "cannon",
        "clone",
        "earthquake",
        "goblindrill",
        "goblincage",
        "ramrider",
        "royalhogs",
        "graveyard",
        "elixerpump",
        "furnace",
        "barbhut",
        "fireball",
        "freeze",
        "tombstone",
        "goblinhut",
        "infernotower",
        "lightning",
        "log",
        "mortar",
        "poison",
        "rage",
        "rocket",
        "snowball",
        "tesla",
        "tornado",
        "xbow",
        "zap",
    ]

    return next((card for card in card_list if check_for_card(image, card)), "unknown")


def get_card_group(card_identification):
    """Method to identify the card group of a given card
    args:
        card_identification: name of the card
    returns:
        str: name of the card group
    """
    turret_cards = [
        "turret_cards",
        "bombtower",
        "cannon",
        "infernotower",
        "tesla",
        "goblincage",
    ]

    spell_cards = [
        "spell_cards",
        "arrows",
        "earthquake",
        "fireball",
        "freeze",
        "lightning",
        "poison",
        "rocket",
        "snowball",
        "tornado",
        "zap",
        "freeze",
    ]

    hog_cards = [
        "hog_cards",
        "hog",
        "battleram",
        "ramrider",
        "royalhogs",
    ]

    spawner_cards = [
        "spawner_cards",
        "goblinhut",
        "tombstone",
        "barbhut",
        "furnace",
    ]

    princess_cards = [
        "princess_cards",
        "skeletonbarrel",
        "princess",
        "barbbarrel",
        "log",
    ]

    miner_cards = [
        "miner_cards",
        "miner",
        "goblindrill",
    ]

    goblin_barrel_cards = [
        "goblin_barrel_cards",
        "goblinbarrel",
        "graveyard",
    ]

    wall_breaker_cards = [
        "wall_breaker_cards",
        "wallbreakers",
    ]

    friendly_spell_cards = [
        "friendly_spell_cards",
        "clone",
        "rage",
    ]

    xbow_cards = [
        "xbow_cards",
        "xbow",
    ]

    mortar_cards = [
        "mortar_cards",
        "mortar",
    ]

    elixer_pump_cards = [
        "elixer_pump_cards",
        "elixerpump",
    ]

    card_list_list = [
        turret_cards,
        spell_cards,
        hog_cards,
        spawner_cards,
        princess_cards,
        miner_cards,
        goblin_barrel_cards,
        wall_breaker_cards,
        friendly_spell_cards,
        xbow_cards,
        mortar_cards,
        elixer_pump_cards,
    ]

    return next(
        (
            card_list[0]
            for card_list in card_list_list
            if card_identification in card_list
        ),
        "regular",
    )


def get_play_coords(card_group, side):
    """Method to calculate the coordinates to play a card based on the card type
    args:
        card_group: name of the card group
        side: side of the board to play the card on
    returns:
        int[]: coordinates to play the card
    """

    if side == "random":
        n = random.randint(0, 1)
        side = "left" if n == 0 else "right"
    left_turret_cards_coords = [[198, 402]]
    right_turret_cards_coords = [[217, 402]]

    left_spell_cards_coords = [
        [87, 189],
        [129, 198],
    ]
    right_spell_cards_coords = [
        [270, 205],
        [321, 201],
    ]

    left_hog_cards_coords = [
        [94, 335],
        [147, 339],
    ]
    right_hog_cards_coords = [
        [293, 334],
        [344, 330],
    ]

    left_spawner_cards_coords = [
        [147, 485],
        [84, 479],
    ]
    right_spawner_cards_coords = [
        [303, 485],
        [375, 491],
    ]

    left_princess_cards_coords = [
        [188, 424],
        [186, 434],
    ]
    right_princess_cards_coords = [
        [217, 409],
        [214, 438],
    ]

    left_miner_cards_coords = [
        [94, 190],
        [140, 210],
        [155, 184],
    ]
    right_miner_cards_coords = [
        [310, 210],
        [342, 188],
        [285, 188],
    ]

    left_goblin_barrel_cards_coords = [
        [135, 192],
    ]
    right_goblin_barrel_cards_coords = [
        [308, 192],
    ]

    left_wall_breaker_cards_coords = [
        [221, 330],
        [221, 330],
        [221, 330],
        [138, 328],
    ]
    right_wall_breaker_cards_coords = [
        [221, 330],
        [221, 330],
        [221, 330],
        [306, 332],
    ]

    left_friendly_spell_cards_coords = [
        [134, 398],
    ]
    right_friendly_spell_cards_coords = [
        [315, 405],
    ]

    left_xbow_cards_coords = [
        [206, 417],
    ]
    right_xbow_cards_coords = [
        [226, 417],
    ]

    left_mortar_cards_coords = [
        [179, 332],
    ]
    right_mortar_cards_coords = [
        [289, 335],
    ]

    if card_group == "elixer_pump_cards":
        if side == "left":
            return [
                [303, 485],
                [375, 491],
            ]

        if side == "right":
            return [
                [147, 485],
                [87, 479],
            ]

    elif card_group == "friendly_spell_cards":
        if side == "left":
            return left_friendly_spell_cards_coords
        if side == "right":
            return right_friendly_spell_cards_coords

    elif card_group == "goblin_barrel_cards":
        if side == "left":
            return right_goblin_barrel_cards_coords
        if side == "right":
            return left_goblin_barrel_cards_coords

    elif card_group == "hog_cards":
        if side == "left":
            return right_hog_cards_coords
        if side == "right":
            return left_hog_cards_coords

    elif card_group == "miner_cards":
        if side == "left":
            return right_miner_cards_coords
        if side == "right":
            return left_miner_cards_coords

    elif card_group == "mortar_cards":
        if side == "left":
            return left_mortar_cards_coords
        if side == "right":
            return right_mortar_cards_coords

    elif card_group == "princess_cards":
        if side == "left":
            return left_princess_cards_coords
        if side == "right":
            return right_princess_cards_coords

    elif card_group == "spawner_cards":
        if side == "left":
            return left_spawner_cards_coords
        if side == "right":
            return right_spawner_cards_coords

    elif card_group == "spell_cards":
        if side == "left":
            return left_spell_cards_coords
        if side == "right":
            return right_spell_cards_coords

    elif card_group == "turret_cards":
        if side == "left":
            return left_turret_cards_coords
        if side == "right":
            return right_turret_cards_coords

    elif card_group == "wall_breaker_cards":
        if side == "left":
            return left_wall_breaker_cards_coords
        if side == "right":
            return right_wall_breaker_cards_coords

    elif card_group == "xbow_cards":
        if side == "left":
            return right_xbow_cards_coords
        if side == "right":
            return left_xbow_cards_coords

    if side == "left":
        return [
            [94, 335],
            [147, 339],
            [147, 485],
            [87, 479],
        ]
    if side == "right":
        return [
            [293, 334],
            [344, 330],
            [303, 485],
            [375, 491],
        ]
    return None
