from pyclashbot.memu.client import screenshot
from pyclashbot.detection.inference.unit_detector.unit_detector import UnitDetector
from pyclashbot.detection.inference.hand_card_classifier.hand_card_classifier import HandClassifier
from pyclashbot.detection.inference.draw import draw_bboxes

unit_detector_model_path = r'src\pyclashbot\detection\inference\unit_detector\unit_detector.onnx'
hand_card_classifier_model_path = r'src\pyclashbot\detection\inference\hand_card_classifier\hand_card_classifier.onnx'

class FightVision:
    def __init__(self,vm_index):
        self.unit_detector = UnitDetector(unit_detector_model_path, use_gpu=True)
        self.hand_classifier = HandClassifier(hand_card_classifier_model_path, use_gpu=True)
        self.image = None
        self.hand_cards = [None,None,None,None]
        self.unit_positions = []
        self.vm_index = vm_index

    def update_image(self,image):
        self.image = image

    def get_unit_data(self):
        #returns a list of bboxes and their cooresponding confidences
        inp = self.unit_detector.preprocess(self.image)
        pred=self.unit_detector.run(inp)
        pred = self.unit_detector.postprocess(pred)
        self.unit_positions = pred
        return pred

    def get_hand_cards(self):
        pred = self.hand_classifier.run(self.image)
        cards = []
        for card,_ in pred:
            cards.append(card)
        self.hand_cards = cards
        return cards

    def read_fight_image(self):
        #update the image
        self.update_image(screenshot(self.vm_index))

        #update unit data
        unit_data = self.get_unit_data()

        #update hand card data
        hand_card_data = self.get_hand_cards()

        return unit_data,hand_card_data

    def get_fight_data(self):
        return self.unit_positions,self.hand_cards

if __name__ == '__main__':
    vm_index=0
    fight = FightVision(vm_index)

    while 1:
        fight.update_image(screenshot(0))
        unit_data = fight.get_unit_data()
        hand_card_data = fight.get_hand_cards()
        print('----------------')
