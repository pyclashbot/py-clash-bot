import time
import cv2
from pyclashbot.detection.inference.tower_status_classifier.tower_status_classifier import (
    TowerClassifier,
)
from pyclashbot.memu.client import screenshot
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
from pyclashbot.detection.inference.draw import draw_bboxes, draw_text, draw_bbox

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
        self.durations = {
            "unit_data": 0,
            "hand_cards": 0,
            "tower_statuses": 0,
            "elixir_count": 0,
        }

        # demo stuff
        self.display_image = None

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
        unit_data_start_time = time.time()
        self.get_unit_data()
        self.durations["unit_data"] += time.time() - unit_data_start_time

        hand_cards_start_time = time.time()
        self.get_hand_cards()
        self.durations["hand_cards"] += time.time() - hand_cards_start_time

        tower_statuses_start_time = time.time()
        self.get_tower_statuses()
        self.durations["tower_statuses"] += time.time() - tower_statuses_start_time

        elixir_count_start_time = time.time()
        self.elixir_count = get_elixir_count(self.image)
        self.durations["elixir_count"] += time.time() - elixir_count_start_time

    def make_display_image(self):
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
        return image

    def run_detection_demo(self):
        while True:
            start_time = time.time()
            self.update_image(screenshot(self.vm_index))
            self.predict_fight_data()
            self.print_fight_data()
            image_with_text = self.make_display_image()
            cv2.imshow("Predictions", image_with_text)
            if cv2.waitKey(25) == 27:  # ESC key to break
                break

    def print_fight_data(self):
        def print_hand_cards(hand_cards):
            print("Hand cards:")
            string = ""
            for card in hand_cards:
                string += "{:^20} |".format(card)
            # remove last char
            string = string[:-1]
            print(string)

        def print_units(unit_positions, unit_classes):
            def format_number(number):
                number = float(number)
                number = str(number)[:4]
                return number

            print("Unit positions:")
            for i, unit_pos in enumerate(unit_positions):
                label = unit_side_predictions[i]
                bbox = unit_pos[:4]
                bbox = [format_number(b) for b in bbox]

                print(label, bbox)

        def print_duration_dict():
            def format_time(s):
                s = str(s)
                return s[:5] + "s"

            def format_percent(p):
                p = str(p)
                p = p.split(".")[0]
                return p + "%"

            print("\n\n")
            total_time = sum(self.durations.values())
            for label, time in self.durations.items():
                percent = time / total_time * 100
                percent = format_percent(percent)
                total_time += time
                time = format_time(time)
                print("{:^15}: {:^7} {}".format(label, time, percent))

        hand_cards = self.hand_cards
        ready_cards = self.ready_hand_cards
        unit_positions = self.unit_positions
        tower_statuses = self.tower_statuses
        elixir_count = self.elixir_count
        unit_side_predictions = self.unit_side_predictions

        print_duration_dict()


if __name__ == "__main__":
    vm_index = 1
    fight = FightVision(vm_index)

    fight.run_detection_demo()
