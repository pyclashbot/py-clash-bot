import cv2
import numpy as np

def compare_images(image, template, threshold=0.8):
    """detects pixel location of a template in an image
    Args:
        image (Image): image to find template within
        template (Image): template image to match to
        threshold (float, optional): matching threshold. defaults to 0.8
    Returns:
        tuple[(int,int)] or None: a tuple of pixel location (x,y)
    """

    # show template
    # template.show()

    # Convert image to np.array
    image = np.array(image)
    template = np.array(template)

    # Convert image colors
    img_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_RGB2GRAY)

    # Perform match operations.
    res = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF_NORMED)

    # Store the coordinates of matched area in a numpy array
    loc = np.where(res >= threshold)  # type: ignore

    if len(loc[0]) != 1:
        return None

    return (loc[0][0], loc[1][0])