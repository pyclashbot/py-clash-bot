import os
import random

from PIL import Image

from pyclashbot.detection.image_rec import (
    check_for_location,
    find_references,
    get_file_count,
    make_reference_image_list,
)
from pyclashbot.memu.client import screenshot

PLAY_COORDS = {
    "spell": {
        "left": [(94, 151), (95, 151), (86, 117)],
        "right": [(327, 153), (327, 105)],
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


def get_play_coords_for_card(vm_index: int, card_index: int, side_preference: str):
    # get this card image(PIL image)
    image = get_card_images(vm_index)[card_index]

    # get the ID of this card(ram_rider, zap, etc)
    identity = identify_card(image)

    # get the grouping of this card (hog, turret, spell, etc)
    group = get_card_group(identity)

    # get the play coords of this grouping
    coords = calculate_play_coords(group, side_preference)

    return identity, coords


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


def get_card_images(vm_index):
    whole_image = screenshot(vm_index)

    card_images = []

    for region in [
        [104, 520, 76, 87],
        [175, 521, 67, 83],
        [241, 521, 68, 82],
        [309, 526, 64, 74],
    ]:
        card_image = crop_image(whole_image, region)
        card_images.append(card_image)

    return card_images


def crop_image(image: Image.Image, region: list[int]) -> Image.Image:
    """Method to crop a Pillow image based on a given region

    Args:
        image (PIL.Image.Image): The original image to be cropped
        region (list[int]): List defining the region as [left, top, width, height]

    Returns:
        PIL.Image.Image: Cropped image based on the given region
    """
    left, top, width, height = region
    right = left + width
    bottom = top + height

    cropped_image = image.crop((left, top, right, bottom))
    return cropped_image


def get_card_name_list():
    card_names = []
    for name in get_file_names(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__))[:-4],
            "detection",
            "reference_images",
        )
    ):
        if "card_" in name:
            name = name.replace("card_", "")
            card_names.append(name)

    return card_names


def get_file_names(directory):
    file_names = []

    for item_name in os.listdir(directory):
        item_path = os.path.join(directory, item_name)
        if os.path.isfile(item_path) or os.path.isdir(item_path):
            file_names.append(item_name)

    return file_names


def identify_card(image):
    card_names = get_card_name_list()

    for card_name in card_names:
        folder_str: str = f"card_{card_name}"

        file_count: int = get_file_count(folder_str)

        references = make_reference_image_list(file_count)

        locations: list[list[int] | None] = find_references(
            image=image, folder=folder_str, names=references, tolerance=0.97
        )

        if check_for_location(locations):
            return card_name

    return "Unknown"


# dev methods




if __name__ == "__main__":
    pass
