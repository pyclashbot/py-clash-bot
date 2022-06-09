import base64
import os
import sys
import time
from io import BytesIO

import PySimpleGUI as sg
from PIL import Image

# classes for which to make folders
classes = ["A1", "A3", "B1", "B3", "C1", "C2", "C3", "None"]

# locations of corners on grid
corners = {
    #name:(left, top, right, bottom)
    "A1": (65, 190, 175, 255),    "A2": (175, 190, 245, 255),    "A3": (245, 190, 355, 255),
    "B1": (65, 275, 175, 400),    "B2": (175, 275, 245, 400),    "B3": (245, 275, 355, 400),
    "C1": (65, 400, 175, 515),    "C2": (175, 400, 245, 515),    "C3": (245, 400, 355, 515),
}


def prepare_files(classes):
    """make the necessary directories

    Args:
        classes (list[str]): list of classes for which to make directories

    Returns:
        str, list[str]: training data (output) dir and list of input files
    """
    # get dir of current file
    module_path = os.path.dirname(os.path.realpath(__file__))
    # define preprocessed data directory, make if not there
    pre_process_data_dir = os.path.join(module_path, 'data', 'preprocess')
    if not os.path.exists(pre_process_data_dir):
        os.makedirs(pre_process_data_dir)
        print("Made preprocesing dir, add images there first, quitting.")
        sys.exit()
    # retrieve file names from preprocess dir
    file_names = [os.path.join(pre_process_data_dir, file_name) for file_name in next(
        os.walk(pre_process_data_dir), (None, None, []))[2]]
    # define training data dir, make if not there
    train_data_dir = os.path.join(module_path, 'data', 'train')
    if not os.path.exists(train_data_dir):
        os.makedirs(train_data_dir)
    # make directories for classes
    for classification in classes:
        class_dir = os.path.join(train_data_dir, classification)
        if not os.path.exists(class_dir):
            os.makedirs(class_dir)
    return train_data_dir, file_names


def make_corners(file_name, corners) -> list[Image.Image]:
    """make cropped images

    Args:
        file_name (str): location of folder
        corners (tuple[int]): the left, top, right, and bottom coordinates

    Returns:
        list[Image.Image]: list of cropped images
    """
    crops = []
    for key in corners:
        im_file = BytesIO()
        crop = Image.open(file_name).crop(corners[key])
        crop.save(im_file, format="PNG")
        crop = base64.b64encode(im_file.getvalue())
        crops.append(crop)
    return crops


def prompt_for_class(classes: list[str], corner_images: list[Image.Image]):
    """prompt user for classes

    Args:
        classes(list[str]) : list of classes
        corner_images (list[Image.Image]): list of crops of image

    Returns:
        str: classification of image
    """
    # define GUI layout
    layout = [
        [
            sg.Button("A1", image_data=corner_images[0]),
            sg.Button("A2", image_data=corner_images[1]),
            sg.Button("A3", image_data=corner_images[2])
        ],
        [
            sg.Button("B1", image_data=corner_images[3]),
            sg.Button("B2", image_data=corner_images[4]),
            sg.Button("B3", image_data=corner_images[5])
        ],
        [
            sg.Button("C1", image_data=corner_images[6]),
            sg.Button("C2", image_data=corner_images[7]),
            sg.Button("C3", image_data=corner_images[8])
        ],
        [sg.Button("Exit"), sg.Button("None")]
    ]
    # define GUI window
    window = sg.Window(
        "Manual Classifier",
        layout,
        element_justification='r'
    )

    # GUI Event Loop
    while True:
        event, values = window.read()
        if event in classes:
            break
        elif event in (sg.WIN_CLOSED, 'Exit'):
            sys.exit()
        return event
    window.close()


def save_classified_image(classes, train_data_dir, file_name, classification):
    """save image to proper class folder

    Args:
        classes (list[str]): list of classes
        train_data_dir (str): directory of training data
        file_name (str): name of file
        classification (str): image classification
    """
    class_dir = os.path.join(train_data_dir, str(
        classification)) if classification in classes else os.path.join(train_data_dir, "None")
    image_dir = os.path.join(class_dir, f"{int(time.time())}.png")
    Image.open(file_name).save(image_dir)
    os.remove(file_name)


# locate the training data dir and the file names
train_data_dir, file_names = prepare_files(classes)

# crop images
image_crop_dict = {file_name: make_corners(
    file_name, corners) for file_name in file_names}

# prompt and save each image
for file_name in image_crop_dict:
    image_crops = image_crop_dict[file_name]
    classification = prompt_for_class(classes, image_crops)
    save_classified_image(classes, train_data_dir, file_name, classification)
