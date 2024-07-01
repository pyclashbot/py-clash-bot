from PIL import Image
import numpy as np
from pyclashbot.detection.inference.detector import OnnxDetector


CARD_NAMES = [
    "empty",
    "archer_queen",
    "archers",
    "baby_dragon",
    "arrows",
    "balloon",
    "bandit",
    "barbarians",
    "barbarian_barrel",
    "bats",
    "inferno_dragon",
    "clone",
    "battle_ram",
    "bomber",
    "log",
    "royal_delivery",
    "bowler",
    "graveyard",
    "freeze",
    "cannon_cart",
    "dark_prince",
    "dart_goblin",
    "e_dragon",
    "e_giant",
    "e_spirit",
    "lightning",
    "tornado",
    "earthquake",
    "fireball",
    "rocket",
    "e_wizard",
    "elite_barbarians",
    "elixir_golem",
    "executioner",
    "firecracker",
    "fire_spirit",
    "fisherman",
    "flying_machine",
    "giant_regular",
    "giant_skeleton",
    "goblin_gang",
    "goblin_giant",
    "goblins",
    "golden_knight",
    "golem",
    "guards",
    "healer",
    "heal_spirit",
    "hog_rider",
    "hunter",
    "ice_golem",
    "ice_spirit",
    "ice_wizard",
    "goblin_demolisher",
    "knight",
    "lava_hound",
    "little_prince",
    "lumberjack",
    "magic_archer",
    "mega_knight",
    "mega_minion",
    "mighty_miner",
    "miner",
    "mini_pekka",
    "minion_horde",
    "minions",
    "monk",
    "mother_witch",
    "musketeer",
    "night_witch",
    "pekka",
    "phoenix",
    "_prince",
    "princess",
    "ram_rider",
    "rascals",
    "royal_ghost",
    "royal_giant",
    "royal_hogs",
    "poison",
    "royal_recruits",
    "skeleton_army",
    "skeleton_barrel",
    "skeleton_dragons",
    "skeleton_king",
    "skeletons",
    "sparky",
    "spear_goblins",
    "three_musketeers",
    "valkyrie",
    "wall_breakers",
    "wizard",
    "bomb_tower",
    "cannon_tower",
    "inferno_tower",
    "mortar",
    "tesla",
    "xbow",
    "barbarian_hut",
    "elixir_collector",
    "furnace",
    "goblin_cage",
    "goblin_drill",
    "snowball",
    "goblin_hut",
    "rage",
    "tombstone",
    "witch",
    "zap_spell",
    "zappies",
]

# sort card_names alphabetically
CARD_NAMES = sorted(CARD_NAMES)
HAND_IMAGE_CROP = [173, 533, 570, 606]  # left, top, width, height
IMAGE_SIZE = 64
BASE_IMAGE_RESIZE = 640
card_bboxes = [
    (0, 0, 89, 73),
    (102, 0, 191, 73),
    (205, 0, 294, 73),
    (309, 0, 398, 73),
]


def crop_image(image, coords):
    return image.crop(coords)


def resize_pil_image(image, size):
    return image.resize((size, size))


def crop_image_into_card_images(image):
    crops = []
    for coord in card_bboxes:
        crop = crop_image(image, coord)
        crop = resize_pil_image(crop, IMAGE_SIZE)
        crops.append(crop)
    return crops


def convert_numpy_to_pil(image):
    return Image.fromarray(image)


def convert_pil_to_numpy(image):
    return np.array(image)


class HandClassifier(OnnxDetector):
    def preprocess(self, image):
        image = convert_numpy_to_pil(image)
        image = resize_pil_image(image, BASE_IMAGE_RESIZE)
        image = crop_image(image, HAND_IMAGE_CROP)
        card_images = crop_image_into_card_images(image)
        card_images = [convert_pil_to_numpy(card) for card in card_images]
        return card_images

    def postprocess(self, output: np.ndarray):
        cardName2prob = {}
        for i in range(len(output)):
            cardName2prob[CARD_NAMES[i]] = output[i]

        # sort cardName2prob by prob
        cardName2prob = dict(
            sorted(cardName2prob.items(), key=lambda item: item[1], reverse=True)
        )

        # get the highest card name, highest card index, and highest card prob
        highest_card_name = list(cardName2prob.keys())[0]
        highest_card_index = CARD_NAMES.index(highest_card_name)
        highest_card_prob = cardName2prob[highest_card_name]

        return [highest_card_name, highest_card_prob]

    def run(self, image):
        images = self.preprocess(image)
        outputs = []
        for img in images:
            outputs.append(self._infer(img).astype(np.float32)[0])

        return [self.postprocess(output) for output in outputs]
