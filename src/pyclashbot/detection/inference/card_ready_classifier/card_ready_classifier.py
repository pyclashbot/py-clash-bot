from PIL import Image
import numpy as np
from pyclashbot.detection.inference.detector import OnnxDetector


# sort card_names alphabetically
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


class CardReadyClassifier(OnnxDetector):
    def preprocess(self, image):
        image = convert_numpy_to_pil(image)
        image = resize_pil_image(image, BASE_IMAGE_RESIZE)
        image = crop_image(image, HAND_IMAGE_CROP)
        card_images = crop_image_into_card_images(image)
        card_images = [convert_pil_to_numpy(card) for card in card_images]
        return card_images

    def postprocess(self, output: np.ndarray):
        if output[1] > output[0]:
            return ('unavailable',output[1])
        else:
            return ('ready',output[0])


    def run(self, image):
        images = self.preprocess(image)
        outputs = []
        for img in images:
            outputs.append(self._infer(img).astype(np.float32)[0])

        return [self.postprocess(output) for output in outputs]
