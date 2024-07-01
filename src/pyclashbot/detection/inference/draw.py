

from functools import lru_cache

import cv2
import numpy as np

rng = np.random.default_rng(82)


@lru_cache
def generate_colors(num_classes):
    colors = [tuple(255 * rng.random(3)) for _ in range(num_classes)]
    return colors


def draw_bbox(
    image: np.ndarray,
    bbox: np.ndarray,
    label,
    color: tuple[int, int, int],
):
    label = str(label)
    bbox = bbox.astype(int)
    # (x_center,y_center,width,height)

    x1 = bbox[0] - bbox[2] // 2
    y1 = bbox[1] - bbox[3] // 2
    x2 = bbox[0] + bbox[2] // 2
    y2 = bbox[1] + bbox[3] // 2

    cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

    cv2.putText(
        image, label, (bbox[0] + 20, bbox[1]), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2
    )


def draw_bboxes(
    image: np.ndarray,
    pred: np.ndarray,
    pred_dims: tuple[int, int],
):
    num_classes = pred.shape[1] - 5
    colors = generate_colors(num_classes)

    height = image.shape[:2][0]
    width = image.shape[:2][1]

    for row in pred:
        label = np.argmax(row[5:])
        color = colors[int(label)]

        bbox = row[:4]
        bbox[0] = (bbox[0] / pred_dims[0]) * width
        bbox[1] = (bbox[1] / pred_dims[1]) * height
        bbox[2] = (bbox[2] / pred_dims[0]) * width
        bbox[3] = (bbox[3] / pred_dims[1]) * height

        draw_bbox(image, bbox, label, color)

    return image
