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
    bbox = [int(x) for x in bbox]

    x1 = bbox[0] - bbox[2] // 2
    y1 = bbox[1] - bbox[3] // 2
    x2 = bbox[0] + bbox[2] // 2
    y2 = bbox[1] + bbox[3] // 2

    cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

    text_x_pos = x1
    text_y_pos = y1 - 10

    cv2.putText(
        image, label, (text_x_pos, text_y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2
    )


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


def draw_bboxes(
    image: np.ndarray,
    pred: np.ndarray,
    labels,
    pred_dims: tuple[int, int],
):
    colors = [
        (255, 0, 0),  # blue
        (0, 0, 255),  # red
    ]

    height = image.shape[:2][0]
    width = image.shape[:2][1]

    for i, row in enumerate(pred):
        label = labels[i]
        if "ally" in label:
            color = colors[0]
        else:
            color = colors[1]

        bbox = row[:4]
        bbox[0] = (bbox[0] / pred_dims[0]) * width
        bbox[1] = (bbox[1] / pred_dims[1]) * height
        bbox[2] = (bbox[2] / pred_dims[0]) * width
        bbox[3] = (bbox[3] / pred_dims[1]) * height

        draw_bbox(image, bbox, label, color)

    return image


def draw_point(
    image: np.ndarray,
    x: int,
    y: int,
    color: tuple[int, int, int],
    radius: int = 5,
    thickness: int = -1,
):
    """
    Draws a point on the given image at the specified coordinates.

    Parameters:
    - image: numpy.ndarray representing the image to draw on.
    - x: int, x-coordinate of the point.
    - y: int, y-coordinate of the point.
    - color: tuple (b, g, r), color of the point in BGR format.
    - radius: int, radius of the point (default: 5).
    - thickness: int, thickness of the point. Use -1 for a filled circle (default: -1).

    Returns:
    - numpy.ndarray: Image with the point drawn.
    """
    color = tuple(map(int, color))  # Ensure color values are integers
    cv2.circle(image, (int(x), int(y)), radius, color, thickness)
    return image


def draw_arrow(
    image: np.ndarray,
    start: tuple[int, int],
    end: tuple[int, int],
    color: tuple[int, int, int],
    thickness: int = 2,
    tip_length: float = 0.3,
):
    """
    Draws an arrow on the given image from start to end coordinates.

    Parameters:
    - image: numpy.ndarray representing the image to draw on.
    - start: tuple (x, y), starting point of the arrow.
    - end: tuple (x, y), ending point of the arrow.
    - color: tuple (b, g, r), color of the arrow in BGR format.
    - thickness: int, thickness of the arrow line (default: 2).
    - tip_length: float, relative length of the arrow tip (default: 0.3).

    Returns:
    - numpy.ndarray: Image with the arrow drawn.
    """
    color = tuple(map(int, color))  # Ensure color values are integers
    start = tuple(map(int, start))
    end = tuple(map(int, end))
    cv2.arrowedLine(image, start, end, color, thickness, tipLength=tip_length)
    return image


if __name__ == "__main__":
    image = np.zeros((500, 500, 3), dtype=np.uint8)
    start = (100, 100)
    end = (400, 400)
    color = (0, 255, 0)  # Green in BGR format
    image_with_arrow = draw_arrow(image, start, end, color)
    cv2.imshow("Image with Arrow", image_with_arrow)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
