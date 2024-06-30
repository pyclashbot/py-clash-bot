import os
import numpy as np
from PIL import Image
import cv2
from pyclashbot.detection.inference.hand_card_classifier.hand_card_classifier import (
    HandClassifier,
)
from pyclashbot.memu.client import screenshot

# Paths and constants
current_path = os.path.dirname(os.path.realpath(__file__))
model_path = os.path.join(current_path, "hand_card_classifier.onnx")
use_gpu = True
vm_index = 12
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


def convert_raw_iar_to_card_images(image):
    image = convert_numpy_to_pil(image)
    image = resize_pil_image(image, BASE_IMAGE_RESIZE)
    image = crop_image(image, HAND_IMAGE_CROP)
    card_images = crop_image_into_card_images(image)
    card_images = [convert_pil_to_numpy(card) for card in card_images]
    return card_images


def draw_text(
    image,
    text,
    position=(10, 10),
    font_size=40,
    font_color=(255, 255, 255),
    font=cv2.FONT_HERSHEY_SIMPLEX,
    thickness=2,
):
    """
    Draws text on the given image using cv2.

    Parameters:
    - image: numpy.ndarray representing the image to draw on.
    - text: str, the text to be drawn.
    - position: tuple (x, y), the starting position of the text (default: (10, 10)).
    - font_size: int, font size in pixels (default: 40).
    - font_color: tuple (r, g, b), color of the text in RGB format (default: white).
    - font: cv2 font type, font for text rendering (default: cv2.FONT_HERSHEY_SIMPLEX).
    - thickness: int, thickness of the text characters (default: 2).

    Returns:
    - numpy.ndarray: Image with text drawn.
    """
    cv2.putText(image, text, position, font, font_size / 10, font_color, thickness)
    return image


def detection(detector):
    image = screenshot(vm_index)
    images = convert_raw_iar_to_card_images(image)
    predictions = []

    for card_image in images:
        prediction = detector.run(card_image)
        prediction = detector.postprocess(prediction)
        predictions.append(prediction)

    # Display predictions on image
    text_coords = [
        (100, 610),
        (160, 625),
        (235, 610),
        (300, 625),
    ]
    for i, prediction in enumerate(predictions):
        if i % 2 == 0:
            color = (0, 255, 255)#red
        else:
            color = (255, 255, 0)
        text = prediction[0]
        draw_text(
            image=image,
            text=text.replace('_',' '),
            position=(text_coords[i][0], text_coords[i][1]),
            font_size=5,
            font_color=color,
        )

    return image


def detection_loop():
    detector = HandClassifier(model_path, use_gpu)

    while True:
        try:
            image_with_text = detection(detector)
            cv2.imshow("Predictions", image_with_text)
            if cv2.waitKey(25) == 27:  # ESC key to break
                break
        except Exception as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    detection_loop()
