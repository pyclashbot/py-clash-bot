from PIL import Image
import numpy as np
from pyclashbot.detection.inference.detector import OnnxDetector


# sort card_names alphabetically
tower_bboxes = [
    (83, 90, 151, 175),
    (269, 90, 339, 175),
    (87, 350, 151, 422),
    (269, 350, 331, 427),
]
TOWER_IMAGE_CROP = 64


def crop_image(image, coords):
    return image.crop(coords)


def resize_pil_image(image, size):
    return image.resize((size, size))


def crop_image_into_card_images(image):
    crops = []
    for coord in tower_bboxes:
        crop = crop_image(image, coord)
        resize = resize_pil_image(crop, TOWER_IMAGE_CROP)
        crops.append(resize)
    return crops


def convert_numpy_to_pil(image):
    return Image.fromarray(image)


def convert_pil_to_numpy(image):
    return np.array(image)


class TowerClassifier(OnnxDetector):
    def preprocess(self, image):
        image = convert_numpy_to_pil(image)
        card_images = crop_image_into_card_images(image)
        card_images = [convert_pil_to_numpy(card) for card in card_images]
        return card_images

    def postprocess(self, output: np.ndarray):
        def format_confidence(conf):
            conf = float(conf) * 100
            conf = str(conf)[:5]
            return conf

        output = [float(o) for o in output]
        if output[0] > output[1]:
            return ("destroyed "+ format_confidence(output[0]))
        else:
            return ("alive " + format_confidence(output[1]))

    def run(self, image):
        images = self.preprocess(image)
        outputs = []
        for img in images:
            outputs.append(self._infer(img).astype(np.float32)[0])

        return [self.postprocess(output) for output in outputs]
