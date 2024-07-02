import cv2
from pyclashbot.detection.inference.tower_status_classifier.tower_status_classifier import (
    TowerClassifier,
)
from pyclashbot.memu.client import screenshot
from pyclashbot.detection.inference.unit_detector.unit_detector import UnitDetector
from pyclashbot.detection.inference.hand_card_classifier.hand_card_classifier import (
    HandClassifier,
)
from pyclashbot.detection.inference.draw import draw_bboxes, draw_text

unit_detector_model_path = (
    r"src\pyclashbot\detection\inference\unit_detector\unit_detector.onnx"
)
hand_card_classifier_model_path = (
    r"src\pyclashbot\detection\inference\hand_card_classifier\hand_card_classifier.onnx"
)
tower_status_classifier_model_path = (
    r"src\pyclashbot\detection\inference\tower_status_classifier\tower_classifier.onnx"
)

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
    negative_color = (115 , 49 ,  4)
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
        # image stuff
        self.vm_index = vm_index
        self.image = None
        # fight data predictions
        self.hand_cards = [None, None, None, None]
        self.unit_positions = []
        self.tower_statuses = [None, None, None, None]
        self.elixir_count = 0
        # demo stuff
        self.display_image = None

    def update_image(self, image):
        self.image = image

    def get_unit_data(self):
        # returns a list of bboxes and their cooresponding confidences
        inp = self.unit_detector.preprocess(self.image)
        pred = self.unit_detector.run(inp)
        pred = self.unit_detector.postprocess(pred)
        self.unit_positions = pred
        return pred

    def get_hand_cards(self):
        pred = self.hand_classifier.run(self.image)
        cards = []
        for card, _ in pred:
            cards.append(card)
        self.hand_cards = cards
        return cards

    def get_tower_statuses(self):
        pred = self.tower_status_classifier.run(self.image)
        self.tower_statuses = pred
        return pred

    def predict_fight_data(self):
        self.get_unit_data()
        self.get_hand_cards()
        self.get_tower_statuses()
        self.elixir_count=get_elixir_count(self.image)

    def make_display_image(self):
        def draw_elixir_count(image,count):
            text = f"Elixir: {count}"
            color = color2rbg["yellow"]
            image = draw_text(
                image=image,
                text=text,
                position=(135, 625),
                font_size=5,
                font_color=color,
            )
            return image

        def draw_tower_statuses(image, preds):
            text_coords = [
                (129, 183),
                (405, 183),
                (129, 360),
                (405, 360),
            ]
            color = (0, 0, 255)
            for i, pred in enumerate(preds):
                if 'alive' in pred:
                    color = color2rbg["green"]
                else:
                    color = color2rbg["red"]
                draw_text(
                    image=image,
                    text=pred.replace("_", " "),
                    position=(text_coords[i][0], text_coords[i][1]),
                    font_size=5,
                    font_color=color,
                )

            return image

        def draw_troop_positions(image, bboxes) -> None:
            image = cv2.resize(image, (640, 640))
            for bbox in bboxes:
                print(bbox)
            image = draw_bboxes(image, bboxes, (640, 640))
            return image

        def draw_hand_cards(image, predictions):
            text_coords = [
                (165, 522),
                (285, 522),
                (387, 522),
                (490, 522),
            ]

            for i, pred in enumerate(predictions):
                text = pred.replace("_", " ")
                text = f"({text})"
                if "empty" in text:
                    color = color2rbg["red"]
                else:
                    color = color2rbg["green"]
                image = draw_text(
                    image=image,
                    text=text,
                    position=(text_coords[i][0], text_coords[i][1]),
                    font_size=5,
                    font_color=color,
                )

            return image

        print("Troops:")
        for t in self.unit_positions:
            print("\t", t)
        print("Hand Cards:")
        for c in self.hand_cards:
            print("\t", c)
        print("Tower Statuses:")
        for s in self.tower_statuses:
            print("\t", s)

        image = self.image
        image = draw_troop_positions(image, self.unit_positions)
        image = draw_hand_cards(image, self.hand_cards)
        image = draw_tower_statuses(image, self.tower_statuses)
        image = draw_elixir_count(image,self.elixir_count)
        return image

    def run_detection_demo(self):
        while True:
            self.update_image(screenshot(self.vm_index))
            self.predict_fight_data()
            image_with_text = self.make_display_image()
            cv2.imshow("Predictions", image_with_text)
            if cv2.waitKey(25) == 27:  # ESC key to break
                break


####TODO ADD ELIXIR DETECTOR

if __name__ == "__main__":
    vm_index = 0
    fight = FightVision(vm_index)

    fight.run_detection_demo()


