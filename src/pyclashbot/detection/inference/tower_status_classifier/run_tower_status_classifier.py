import os
from charset_normalizer import detect
import numpy as np
from PIL import Image
import cv2
from pyclashbot.detection.inference.tower_status_classifier.tower_status_classifier import (
    TowerClassifier,
)
from pyclashbot.detection.inference.draw import draw_text
from pyclashbot.memu.client import screenshot

# Paths and constants
current_path = os.path.dirname(os.path.realpath(__file__))
model_path = os.path.join(current_path, "tower_classifier.onnx")
use_gpu = True
vm_index = 0


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


def detection(detector):
    image = screenshot(vm_index)
    predictions = detector.run(image)

    # Display predictions on image
    text_coords = [
        (89, 170),
        (275, 170),
        (87, 350),
        (269, 350),
    ]
    for i, prediction in enumerate(predictions):
        if i in [0,1]:
            color = (0, 0, 255)#red
        else:
            color = (0, 255, 0)
        text = prediction[0] + " " + prediction[1] + "%"
        draw_text(
            image=image,
            text=text.replace('_',' '),
            position=(text_coords[i][0], text_coords[i][1]),
            font_size=5,
            font_color=color,
        )

    return image





def detection_loop():
    detector = TowerClassifier(model_path, use_gpu)

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
