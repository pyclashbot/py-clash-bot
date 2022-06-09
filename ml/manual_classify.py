import base64
import os
import sys
import time
from io import BytesIO

import PySimpleGUI as sg
from PIL import Image

module_path = os.path.dirname(os.path.realpath(__file__))
pre_process_data_dir = os.path.join(module_path, 'data', 'preprocess')
train_data_dir = os.path.join(module_path, 'data', 'train')

classes = [
    "A1",
    "A3",
    "B1",
    "B3",
    "C1",
    "C2",
    "C3",
    "None"
]

corners = {
    #name:(left, top, right, lower)
    "A1": (65, 190, 175, 255),
    "A2": (175, 190, 245, 255),
    "A3": (245, 190, 355, 255),
    "B1": (65, 275, 175, 400),
    "B2": (175, 275, 245, 400),
    "B3": (245, 275, 355, 400),
    "C1": (65, 400, 175, 515),
    "C2": (175, 400, 245, 515),
    "C3": (245, 400, 355, 515),
}

file_names = [os.path.join(pre_process_data_dir, file_name) for file_name in next(
    os.walk(pre_process_data_dir), (None, None, []))[2]]


def make_directories(train_data_dir, classes):
    for classification in classes:
        class_dir = os.path.join(train_data_dir, classification)
        if not os.path.exists(class_dir):
            os.makedirs(class_dir)


def make_corners(file_name, corners):
    crops = []
    for key in corners:
        im_file = BytesIO()
        crop = Image.open(file_name).crop(corners[key])
        crop.save(im_file, format="PNG")
        crop = base64.b64encode(im_file.getvalue())
        crops.append(crop)
    return crops


def prompt_for_class(image_corners, file_name):
    corner_images = image_corners[file_name]
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
        [sg.Button("Exit"), sg.Button("None"), sg.Button("Next")]
    ]
    window = sg.Window("Manual Classifier", layout, no_titlebar=True)
    while True:             # Event Loop
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Next'):
            break
        elif event in (sg.WIN_CLOSED, 'Exit'):
            sys.exit()
        return event
    window.close()


image_corners = {file_name: make_corners(
    file_name, corners) for file_name in file_names}


make_directories(train_data_dir, classes)

for file_name in image_corners:
    classification = prompt_for_class(image_corners, file_name)
    if classification in classes:
        class_dir = os.path.join(train_data_dir, str(classification))
        image_dir = os.path.join(class_dir, f"{time.time()}.png")
        Image.open(file_name).save(image_dir)
    else:
        class_dir = os.path.join(train_data_dir, "None")
        image_dir = os.path.join(class_dir, f"{int(time.time())}.png")
        Image.open(file_name).save(image_dir)
    os.remove(file_name)
