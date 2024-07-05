import random
import time
import cv2
from pyclashbot.detection.inference.tower_status_classifier.tower_status_classifier import (
    TowerClassifier,
)
from pyclashbot.memu.client import screenshot, click
from pyclashbot.detection.inference.unit_detector.unit_detector import UnitDetector
from pyclashbot.detection.inference.hand_card_classifier.hand_card_classifier import (
    HandClassifier,
)
from pyclashbot.detection.inference.unit_side_classifier.unit_side_classifier import (
    UnitSideClassifier,
)
from pyclashbot.detection.inference.card_ready_classifier.card_ready_classifier import (
    CardReadyClassifier,
)
from pyclashbot.detection.inference.draw import (
    draw_bboxes,
    draw_text,
    draw_bbox,
    draw_arrow,
    draw_point,
)
import numpy as np
from sklearn.cluster import DBSCAN


unit_detector_model_path = (
    r"src\pyclashbot\detection\inference\unit_detector\unit_detector.onnx"
)
hand_card_classifier_model_path = (
    r"src\pyclashbot\detection\inference\hand_card_classifier\hand_card_classifier.onnx"
)
tower_status_classifier_model_path = (
    r"src\pyclashbot\detection\inference\tower_status_classifier\tower_classifier.onnx"
)
unit_side_classifier_model_path = (
    r"src\pyclashbot\detection\inference\unit_side_classifier\unit_side_classifier.onnx"
)
card_ready_classifier_model_path = r"src\pyclashbot\detection\inference\card_ready_classifier\card_ready_classifier.onnx"
color2rbg = {
    "green": (0, 255, 0),
    "yellow": (0, 255, 255),
    "blue": (255, 0, 0),
    "red": (0, 0, 255),
    "purple": (255, 0, 255),
    "white": (255, 255, 255),
    "black": (0, 0, 0),
}
anti_cluster_spells = [
    "arrows",
    "barbarian_barrel",
    "log",
    "freeze",
    "lightning",
    "tornado",
    "earthquake",
    "fireball",
    "rocket",
    "snowball",
    "rage",
    "zap_spell",
]
defensive_melee_units = [
    "baby_dragon",
    "barbarians",
    "royal_delivery",
    "bowler",
    "dark_prince",
    "e_spirit",
    "elite_barbarians",
    "giant_skeleton",
    "goblin_gang",
    "goblins",
    "golden_knight",
    "guards",
    "knight",
    "lumberjack",
    "mega_knight",
    "mighty_miner",
    "mini_pekka",
    "monk",
    "pekka",
    "_prince",
    "rascals",
    "royal_ghost",
    "royal_recruits",
    "skeleton_army",
    "skeletons",
    "spear_goblins",
    "valkyrie",
    "goblin_cage",
]
defensive_ranged_units = [
    "archer_queen",
    "archers",
    "baby_dragon",
    'bandit',
    "bomber",
    "cannon_cart",
    "dart_goblin",
    "e_dragon",
    "e_spirit",
    "e_wizard",
    "executioner",
    "firecracker",
    "fire_spirit",
    "fisherman",
    "flying_machine",
    "goblin_gang",
    "hunter",
    "ice_wizard",
    "goblin_demolisher",
    "little_prince",
    "magic_archer",
    "mother_witch",
    "musketeer",
    "night_witch",
    "princess",
    "rascals",
    "skeleton_dragons",
    "sparky",
    "spear_goblins",
    "three_musketeers",
    "wizard",
    "witch",
    "zappies",
]
tower_cards = [
    "bomb_tower",
    "cannon_tower",
    "inferno_tower",
    "tesla",
    "goblin_cage",
    "tombstone",
]
spawner_cards = [
    "barbarian_hut",
    "elixir_collector",
    "furnace",
    "goblin_hut",
    "tombstone",
]
waiting_troops = [
    "archer_queen",
    "archers",
    "baby_dragon",
    "balloon",
    "bandit",
    "barbarians",
    "bats",
    "inferno_dragon",
    "battle_ram",
    "bomber",
    "royal_delivery",
    "bowler",
    "cannon_cart",
    "dark_prince",
    "dart_goblin",
    "e_dragon",
    "e_giant",
    "e_spirit",
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
    "wizard",
    "witch",
    "zappies",
]


def get_elixir_count(iar):
    negative_color = (115, 49, 4)

    def color_is_negative(color):
        tol = 30 * 3
        diff = 0
        for i in range(3):
            diff += abs(color[i] - negative_color[i])
        return diff < tol

    pixels = [
        iar[612][146],
        iar[612][166],
        iar[612][191],
        iar[612][216],
        iar[612][238],
        iar[612][263],
        iar[612][291],
        iar[612][313],
        iar[612][336],
        iar[612][363],
    ]

    for i, p in enumerate(pixels):
        if color_is_negative(p):
            return i

    return 10


def cluster_unit_bboxes(unit_bboxes, unit_side_predictions):  # -> list:
    """
    unit_bboxes: list of unscaled bboxes: [[123,345,15,15],[262,152,45,23],[600,580,29,27]] #centerx,centery,width,height
    unit_side_predictions: list of side prediction + confidence tuples: [("ally",0.99),("enemy",0.82),("ally",0.93)]
    """

    def cluster_points(points, eps, min_samples=2):  # -> list:
        """
        Clusters points using the DBSCAN algorithm and returns the coordinates and sizes of the clusters.

        Parameters:
        ----------
        points : list of lists
            List of points, where each point is represented as a list [x, y].
        eps : int or float, optional
            Maximum distance between two points to be considered in the same neighborhood (for DBSCAN). Default is 50.
        min_samples : int, optional
            Minimum number of points to form a cluster (for DBSCAN). Default is 2.

        Returns:
        -------
        list of lists
            List of clusters, where each cluster is represented as a list with:
            [center_x, center_y, width, height]
        """
        # Convert points to numpy array
        points_array = np.array(points)

        # Cluster the points using DBSCAN
        db = DBSCAN(eps=eps, min_samples=min_samples).fit(points_array)
        labels = db.labels_

        # Extract cluster information
        clusters = {}
        for idx, label in enumerate(labels):
            if label == -1:  # Ignore noise
                continue
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(points_array[idx])

        # Calculate cluster coordinates and sizes
        cluster_bboxes = []
        for label, cluster_points in clusters.items():
            cluster_points = np.array(cluster_points)
            min_x, min_y = cluster_points.min(axis=0)
            max_x, max_y = cluster_points.max(axis=0)

            # Calculate width and height of the cluster bounding box
            width = max_x - min_x
            height = max_y - min_y

            # Calculate center coordinates
            center_x = min_x + width / 2
            center_y = min_y + height / 2

            bbox = [center_x, center_y, width, height]
            cluster_bboxes.append(bbox)

        return cluster_bboxes

    def convert_bbox_to_coord(bbox):  # -> tuple:
        coord = (bbox[0], bbox[1])

        return coord

    enemy_coords = []
    for i, side in enumerate(unit_side_predictions):
        if "enemy" in side:
            unit_coord = convert_bbox_to_coord(unit_bboxes[i])
            enemy_coords.append(unit_coord)

    if len(enemy_coords) < 4:
        return []

    clusters = cluster_points(enemy_coords, eps=50, min_samples=4)

    return clusters






class FightVision:
    def __init__(self, vm_index):
        # models
        self.unit_detector = UnitDetector(unit_detector_model_path, use_gpu=True)
        self.hand_classifier = HandClassifier(
            hand_card_classifier_model_path, use_gpu=True
        )
        self.tower_status_classifier = TowerClassifier(
            tower_status_classifier_model_path, use_gpu=True
        )
        self.unitClassifier = UnitSideClassifier(unit_side_classifier_model_path, True)
        self.card_ready_classifier = CardReadyClassifier(
            card_ready_classifier_model_path, True
        )

        # image stuff
        self.vm_index = vm_index
        self.image = None

        # fight data predictions
        self.hand_cards = [None, None, None, None]
        self.ready_hand_cards = [False, False, False, False]
        self.unit_positions = []
        self.tower_statuses = [None, None, None, None]
        self.elixir_count = 0
        self.unit_sides = []
        self.clusters = []

        # play calculations
        self.play_card = None
        self.play_coord = (None, None)

        # tracking inference times for different models
        self.durations = {
            "unit_data": 0,
            "hand_cards": 0,
            "tower_statuses": 0,
            "elixir_count": 0,
            "clusters": 0,
            "play_calculation": 0,
        }

        # demo stuff
        self.display_image = None

    def make_play(self):  # -> tuple[None, None] | tuple[int, tuple]:
        """
        params:
            #TODO
        returns:
            (card_index,coord) where card_index = int(0-3) and coord = (x,y)
        """

        # if elixir count is less than 2, return (None,None)
        if self.elixir_count < 2:
            return (None, None)

        # if every value in ready_hand_cards is false, return (None,None)
        if not any(self.ready_hand_cards):
            return (None, None)


        def preprocess():
            def coord_in_region(coord, region):
                x, y = coord
                x1, y1, x2, y2 = region
                return x1 <= x <= x2 and y1 <= y <= y2
            def bbox2coord(bbox):
                return bbox[:2]

            # make a dict of enemy and ally positions for ez access
            side2positions = {
                "ally": [],
                "enemy": [],
            }
            for i, unit_position in enumerate(self.unit_positions):
                if "enemy" in self.unit_sides[i]:
                    side2positions["enemy"].append(bbox2coord(unit_position))
                else:
                    side2positions["ally"].append(bbox2coord(unit_position))

            board_regions = [  # xyxy
                (82,64,316,263),  # topleft
                (321,60,541,267),  # topright
                (92,269,311,489),  # bottomleft
                (318,288,547,476),  # bottomright
            ]

            # make a dict of quandrants to counts
            quandrant2enemyCount = {
                0: 0,
                1: 0,
                2: 0,
                3: 0,
            }
            quandrant2allyCount = {
                0: 0,
                1: 0,
                2: 0,
                3: 0,
            }

            # fill out the dicts
            ally_positions = side2positions["ally"]
            enemy_positions = side2positions["enemy"]
            for i, region in enumerate(board_regions):
                for ally_position in ally_positions:
                    if coord_in_region(ally_position, region):
                        quandrant2allyCount[i] += 1
                for enemy_position in enemy_positions:
                    if coord_in_region(enemy_position, region):
                        quandrant2enemyCount[i] += 1

            return side2positions, quandrant2enemyCount, quandrant2allyCount

        side2positions, quandrant2enemyCount, quandrant2allyCount = preprocess()

        # use anti-cluster spells against clusters (arrows on a skeleton army)
        def check_for_cluster_plays(hand_cards, clusters):
            if len(clusters) == 0:
                return False

            # if there are anti_cluster_spells in the hand, select that card index
            for card_index, card in enumerate(hand_cards):
                if card and card in anti_cluster_spells:
                    y_adjustment = 50

                    target_cluster = random.choice(clusters)
                    x, y = target_cluster[:2]

                    # adjust the y coord to account for troop movement
                    y += y_adjustment

                    coord = (x, y)

                    return (card_index, coord)

            return False

        def get_defense_play(side='left'):
            def get_ready_card_index():
                for i,ready in enumerate(self.ready_hand_cards):
                    if ready:
                        return i
                return -1

            defend_left_melee_coord = (183,358)
            defend_left_ranged_coord = random.choice([(116,412),(267,407)])
            defend_right_melee_coord = (451,363)
            defend_right_ranged_coord = random.choice([(394,401),(510,411)])
            tower_left_coord = (296,343)
            tower_right_coord = (344,347)

            #try to defend with a defensive_melee_units
            defensive_card_index=-1
            for defensive_card in defensive_melee_units:
                if defensive_card in self.hand_cards:
                    defensive_card_index = self.hand_cards.index(defensive_card)
                    if self.ready_hand_cards[defensive_card_index] is False:
                        continue
                    break
            if defensive_card_index != -1:
                if side == 'left':
                    return (defensive_card_index, defend_left_melee_coord)
                else:
                    return (defensive_card_index, defend_right_melee_coord)

            #try to defend with a defensive_ranged_units
            for defensive_card in defensive_ranged_units:
                if defensive_card in self.hand_cards:
                    defensive_card_index = self.hand_cards.index(defensive_card)
                    if self.ready_hand_cards[defensive_card_index] is False:
                        continue
                    break
            if defensive_card_index != -1:
                if side == 'left':
                    return (defensive_card_index, defend_left_ranged_coord)
                else:
                    return (defensive_card_index, defend_right_ranged_coord)

            #try to defend with a tower_card
            tower_card_index=-1
            for tower_card in tower_cards:
                if tower_card in self.hand_cards:
                    tower_card_index = self.hand_cards.index(tower_card)
                    if self.ready_hand_cards[tower_card_index] is False:
                        continue
                    break
            if tower_card_index != -1:
                if side == 'left':
                    return (tower_card_index, tower_left_coord)
                else:
                    return (tower_card_index, tower_right_coord)

            #else just return a random card to try and defend as best as possible

            card_index = get_ready_card_index()
            if card_index == -1:
                card_index = random.randint(0,3)
            if side == 'left':
                return (card_index, defend_left_melee_coord)
            else:
                return (card_index, defend_right_melee_coord)

        def check_for_defensive_play():
            # focus on the last 2 (our right and left lanes)
            left_lane_index = 2
            right_lane_index = 3

            # if there are more enemies on the right lane than allies, defend the right lane
            if (
                quandrant2enemyCount[right_lane_index]
                > quandrant2allyCount[right_lane_index]
            ):
                print("defend right")
                return get_defense_play(side='right')

            # if there are more enemies on the left lane than allies, defend the left lane
            if quandrant2enemyCount[left_lane_index] > quandrant2allyCount[left_lane_index]:
                print("defend left")
                return get_defense_play(side='left')

            return False

        def check_for_spawner_play():
            #if there are enemies in the 3rd or 4th quadrant, dont play spawners
            if quandrant2enemyCount[2] > 0 or quandrant2enemyCount[3] > 0:
                return False

            #pick a spot for the spawner based on ally tower statuses
            play_coord=random.choice([(470,454),(131,448)])
            if 'destroyed' in self.tower_statuses[2]:
                play_coord = (470,454)
            if 'destroyed' in self.tower_statuses[3]:
                play_coord = (131,448)

            for i, card in enumerate(self.hand_cards):
                if card in spawner_cards:
                    if self.ready_hand_cards[i] is False:
                        continue
                    return (i, play_coord)

            return False

        def check_for_waiting_play():
            left_waiting_coord = random.choice([(114,418),(159,462),(277,404)])
            right_waiting_coord = random.choice([(503,471),(445,446),(402,410)])

            #see if there is a waiting troop in the hand
            waiting_troop_index = -1
            for i, card in enumerate(self.hand_cards):
                if self.ready_hand_cards[i] is False:
                        continue
                if card in waiting_troops:
                    waiting_troop_index = i
                    break
            if waiting_troop_index == -1:
                return False

            #if there are no enemies on 3rd or 4th quadrant (our side of the board)
            if quandrant2enemyCount[2] == 0 and quandrant2enemyCount[3] == 0:
                #if there are enemies in the 1st quadrant (their left side)
                if quandrant2enemyCount[0] > 0:
                    return (waiting_troop_index, left_waiting_coord)
                #if there are enemies in the 2nd quadrant (their right side)
                if quandrant2enemyCount[1] > 0:
                    return (waiting_troop_index, right_waiting_coord)
                return False

            return False


        #check for defense
        defense_play = check_for_defensive_play()
        if defense_play is not False:
            print('Doing a cluster play')
            return defense_play

        # attack clusters with anti_cluster_spells
        cluster_play = check_for_cluster_plays(self.hand_cards, self.clusters)
        if cluster_play is not False:
            print('Doing a cluster play')
            return cluster_play

        #check for spawner plays
        spawner_play = check_for_spawner_play()
        if spawner_play is not False:
            print('Doing a spawner play')
            return spawner_play

        #check for waiting plays
        waiting_play = check_for_waiting_play()
        if waiting_play is not False:
            print('Doing a waiting play')
            return waiting_play

        # if no checks occured, return (None,None) meaning no card, no coord
        return (None, None)

    def update_image(self, image):
        self.image = image

    def predict_unit_sides(self):
        preds = [
            self.unitClassifier.run(self.image, unit_bbox)
            for unit_bbox in self.unit_positions
        ]
        self.unit_sides = preds

    def get_unit_data(self):
        # returns a list of bboxes and their cooresponding confidences
        inp = self.unit_detector.preprocess(self.image)
        pred = self.unit_detector.run(inp)
        pred = self.unit_detector.postprocess(pred)
        self.unit_positions = pred
        self.predict_unit_sides()
        return pred

    def get_hand_cards(self):
        pred = self.hand_classifier.run(self.image)
        ready_predictions = self.card_ready_classifier.run(self.image)
        cards = []
        for card, _ in pred:
            cards.append(card)
        self.hand_cards = cards
        self.ready_hand_cards = ready_predictions

    def get_tower_statuses(self):
        pred = self.tower_status_classifier.run(self.image)
        self.tower_statuses = pred
        return pred

    def predict_fight_data(self):
        # unit position + unit side predictions
        unit_data_start_time = time.time()
        self.get_unit_data()
        self.durations["unit_data"] += time.time() - unit_data_start_time

        # hand card classifications + ready predictinos
        hand_cards_start_time = time.time()
        self.get_hand_cards()
        self.durations["hand_cards"] += time.time() - hand_cards_start_time

        # tower status predictions
        tower_statuses_start_time = time.time()
        self.get_tower_statuses()
        self.durations["tower_statuses"] += time.time() - tower_statuses_start_time

        # elixir status detection
        elixir_count_start_time = time.time()
        self.elixir_count = get_elixir_count(self.image)
        self.durations["elixir_count"] += time.time() - elixir_count_start_time

        # cluter calculation
        cluster_start_time = time.time()
        clusters = cluster_unit_bboxes(self.unit_positions, self.unit_sides)
        self.clusters = clusters
        self.durations["clusters"] += time.time() - cluster_start_time

        # calculate the best play given the fight data
        play_calculation_start_time = time.time()
        self.play_card, self.play_coord = self.make_play()
        self.durations["play_calculation"] += time.time() - play_calculation_start_time

    def make_display_image(self):
        def draw_best_play(image):
            best_coord = self.play_coord
            best_card = self.play_card

            if best_coord is None or best_card is None:
                return image

            cardIndex2coord = {
                0: (214,567),
                1: (320,567),
                2: (421, 567),
                3: (526, 567),
            }

            draw_arrow(image, cardIndex2coord[best_card], best_coord, (255, 255, 0))

            return image

        def draw_clusters(image, clusters):
            # draw all the cluster bboxes
            for bbox in clusters:
                draw_bbox(
                    image,
                    bbox,
                    "enemy_cluster",
                    (255, 0, 255),
                )

            return image

        def draw_elixir_count(image, count):
            bbox = [386, 624, 387, 17]

            text = f"Elixir: {count}"
            color = color2rbg["yellow"]

            draw_bbox(
                image,
                bbox,
                text,
                color,
            )
            return image

        def draw_tower_statuses(image, preds):
            # draw all the labels

            tower_bbox_size = 75
            tower_bboxes = [
                (180, 135, tower_bbox_size, tower_bbox_size),
                (463, 135, tower_bbox_size, tower_bbox_size),
                (180, 398, tower_bbox_size, tower_bbox_size),
                (463, 398, tower_bbox_size, tower_bbox_size),
            ]
            color = (0, 0, 255)
            for i, pred in enumerate(preds):
                if "alive" in pred:
                    color = color2rbg["green"]
                else:
                    color = color2rbg["red"]

                bbox = tower_bboxes[i]

                draw_bbox(
                    image,
                    bbox,
                    pred,
                    color,
                )

            return image

        def draw_troop_positions(image, bboxes, sides) -> None:
            image = cv2.resize(image, (640, 640))

            image = draw_bboxes(image, bboxes, sides, (640, 640))
            return image

        def draw_hand_cards(image, predictions):
            card_sizes = (468 - 377, 608 - 523)
            card_bboxes = [
                (215, 567, card_sizes[0], card_sizes[1]),
                (319, 567, card_sizes[0], card_sizes[1]),
                (422, 567, card_sizes[0], card_sizes[1]),
                (524, 567, card_sizes[0], card_sizes[1]),
            ]

            for i, pred in enumerate(predictions):
                text = pred.replace("_", " ")
                text = f"({text})"
                if "empty" in text:
                    color = color2rbg["red"]
                else:
                    color = color2rbg["green"]

                text = text[:13].replace("(", "").replace(")", "")
                bbox = card_bboxes[i]
                draw_bbox(
                    image,
                    bbox,
                    text,
                    color,
                )
            return image

        image = self.image
        image = draw_troop_positions(
            image, self.unit_positions, self.unit_sides
        )
        image = draw_hand_cards(image, self.hand_cards)
        image = draw_tower_statuses(image, self.tower_statuses)
        image = draw_elixir_count(image, self.elixir_count)
        image = draw_clusters(image, self.clusters)
        image = draw_best_play(image)
        return image

    def run_detection_demo(self,make_plays=False):
        def make_play():
            hand_card_coords = [
            (142, 561),
            (210, 563),
            (272, 561),
            (341, 563),
        ]

            def convert_coord(coord,old_dims,new_dims):
                x,y = coord
                x = int((x/old_dims[0])*new_dims[0])
                y = int((y/old_dims[1])*new_dims[1])
                return x,y


            #grab info from FightVision
            card_index = self.play_card
            play_coord = self.play_coord

            #if no play, make no play
            if card_index is None or play_coord is None:
                return

            #convert play coord to useable
            play_coord = convert_coord(play_coord,(640,640),(419,633))

            #convert card_index to useable
            card_coord = hand_card_coords[card_index]

            click(self.vm_index, card_coord[0], card_coord[1])
            click(self.vm_index, play_coord[0], play_coord[1])


        while True:
            self.update_image(screenshot(self.vm_index))
            self.predict_fight_data()
            image_with_text = self.make_display_image()
            print('\n')
            for label,duration in self.durations.items():
                print('{:^16} : {}'.format(label,duration))
            if make_plays:
                make_play()
            cv2.imshow("Predictions", image_with_text)
            if cv2.waitKey(25) == 27:  # ESC key to break
                break


if __name__ == "__main__":
    vm_index = 1
    fight = FightVision(vm_index)

    fight.run_detection_demo(make_plays=True)
