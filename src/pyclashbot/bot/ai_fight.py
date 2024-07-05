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

import random


def make_play(elixir_count, hand_cards, ready_hand_cards, clusters):
    """
    params:
        elixir_count:int
        hand_cards: list[str] of length 4 where str is the card name
        ready_hand_cards: list[bool] of length 4
        clusters: list[bbox] where bbox = [center_x, center_y, width, height]
    returns:
        (card_index,coord) where card_index = int(0-3) and coord = (x,y)
    """

    # return a (card, coord) tuple given fight data

    # if elixir count is less than 2, return (None,None)
    if elixir_count < 2:
        return (None, None)

    # if every value in ready_hand_cards is false, return (None,None)
    if not any(ready_hand_cards):
        return (None, None)

    # attack clusters with anti_cluster_spells
    if len(clusters) > 0:
        print(f"There are clusters")
        # if there are anti_cluster_spells in the hand, select that card index
        random.shuffle(hand_cards)
        for card_index, card in enumerate(hand_cards):
            if card and card in anti_cluster_spells:
                print(f"Found anti cluster spell: {card} at index {card_index}")
                y_adjustment = 50

                target_cluster = random.choice(clusters)
                x, y = target_cluster[:2]

                # adjust the y coord to account for troop movement
                y += y_adjustment

                coord = (x, y)

                return (card_index, coord)

    # if no checks occured, return (None,None) meaning no card, no coord
    return (None, None)


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
        self.unit_side_predictions = []
        self.cluster_predictions = []

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
            elixir_count:int
            hand_cards: list[str] of length 4 where str is the card name
            ready_hand_cards: list[bool] of length 4
            clusters: list[bbox] where bbox = [center_x, center_y, width, height]
        returns:
            (card_index,coord) where card_index = int(0-3) and coord = (x,y)
        """

        # return a (card, coord) tuple given fight data

        # if elixir count is less than 2, return (None,None)
        if self.elixir_count < 2:
            return (None, None)

        # if every value in ready_hand_cards is false, return (None,None)
        if not any(self.ready_hand_cards):
            return (None, None)

        # attack clusters with anti_cluster_spells
        if len(self.cluster_predictions) > 0:
            print(f"There are clusters")
            # if there are anti_cluster_spells in the hand, select that card index
            for card_index, card in enumerate(self.hand_cards):
                if card and card in anti_cluster_spells:
                    print(f"Found anti cluster spell: {card} at index {card_index}")
                    y_adjustment = 50

                    target_cluster = random.choice(self.cluster_predictions)
                    x, y = target_cluster[:2]

                    # adjust the y coord to account for troop movement
                    y += y_adjustment

                    coord = (x, y)

                    return (card_index, coord)

        # if no checks occured, return (None,None) meaning no card, no coord
        return (None, None)

    def update_image(self, image):
        self.image = image

    def predict_unit_sides(self):
        preds = [
            self.unitClassifier.run(self.image, unit_bbox)
            for unit_bbox in self.unit_positions
        ]
        self.unit_side_predictions = preds

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
        clusters = cluster_unit_bboxes(self.unit_positions, self.unit_side_predictions)
        self.cluster_predictions = clusters
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
                0: (142, 561),
                1: (210, 563),
                2: (272, 561),
                3: (341, 563),
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
            image, self.unit_positions, self.unit_side_predictions
        )
        image = draw_hand_cards(image, self.hand_cards)
        image = draw_tower_statuses(image, self.tower_statuses)
        image = draw_elixir_count(image, self.elixir_count)
        image = draw_clusters(image, self.cluster_predictions)
        image = draw_best_play(image)
        return image

    def run_detection_demo(self):
        def print_play(coord, card_index):
            if coord is None or card_index is None:
                print("No play")

        while True:
            self.update_image(screenshot(self.vm_index))
            self.predict_fight_data()
            image_with_text = self.make_display_image()
            cv2.imshow("Predictions", image_with_text)
            if cv2.waitKey(25) == 27:  # ESC key to break
                break


if __name__ == "__main__":
    vm_index = 1
    fight = FightVision(vm_index)

    fight.run_detection_demo()
