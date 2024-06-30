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




class HandClassifier(OnnxDetector):
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
        return self._infer(image).astype(np.float32)[0]
