import base64
import os
import sys
import time
from io import BytesIO
import multiprocessing

import PySimpleGUI as sg
from PIL import Image


def prepare_files(classes):
    print("prepping files")
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


def crop_image(file_name: str) -> list[str]:
    print(f"Cropping {file_name[70:]}")
    """make cropped images

    Args:
        file_name (str): location of folder

    Returns:
        list[str]: list of cropped images
    """
    # locations of corners on grid
    corners = {
        #name:(left, top, right, bottom)
        "A1": (65, 190, 175, 255),    "A2": (175, 190, 245, 255),    "A3": (245, 190, 355, 255),
        "B1": (65, 275, 175, 400),    "B2": (175, 275, 245, 400),    "B3": (245, 275, 355, 400),
        "C1": (65, 400, 175, 515),    "C2": (175, 400, 245, 515),    "C3": (245, 400, 355, 515),
    }
    crops = []
    for key in corners:
        # crop image
        crop = Image.open(file_name).crop(corners[key])
        crop = crop.resize((round(crop.size[0]*2), round(crop.size[1]*2)))
        # convert image to b64 for use in button image
        im_file = BytesIO()
        crop.save(im_file, format="PNG")
        crop = base64.b64encode(im_file.getvalue())
        crops.append(crop)
    return crops


def crop_images(file_names: list[str]) -> dict[str, list[str]]:
    print(f"Cropping images")
    """crop a list of images

    Args:
        file_names (list[str]): list of image paths

    Returns:
        dict[str,list[str]]: dictionary of image paths and their crops in b64
    """
    try:
        cpus = multiprocessing.cpu_count()
    except NotImplementedError:
        cpus = 2   # arbitrary default

    pool = multiprocessing.Pool(processes=cpus)
    image_crops = pool.map(crop_image, file_names)

    image_crop_dict = dict(zip(file_names, image_crops))
    return image_crop_dict


def prompt_for_class(classes:list[str],file_name: str, image_crops: list[str]) -> str:
    """prompt user to classify image

    Args:
        classes (list[str]): list of classes
        file_name (str): name of file to be classified
        corner_images (list[str]): list of crops of image b64 encoded

    Returns:
        str: classification of image
    """
    # define GUI layout
    layout = [
        [
            sg.Button("A1", image_data=image_crops[0]),
            sg.Button("A2", image_data=image_crops[1]),
            sg.Button("A3", image_data=image_crops[2])
        ],
        [
            sg.Button("B1", image_data=image_crops[3]),
            sg.Button("B2", image_data=image_crops[4]),
            sg.Button("B3", image_data=image_crops[5])
        ],
        [
            sg.Button("C1", image_data=image_crops[6]),
            sg.Button("C2", image_data=image_crops[7]),
            sg.Button("C3", image_data=image_crops[8])
        ],
        [sg.Button("Exit"), sg.Text(
            file_name, size=(63, None)), sg.Button("None(n)")]
    ]
    # define GUI window
    window = sg.Window(
        "Manual Classifier",
        layout,
        element_justification='r',
        return_keyboard_events=True
    )

    # GUI Event Loop
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            window.close()
            sys.exit()
        elif event in classes:
            window.close()
            return event
        elif event == 'n':
            window.close()
            return "None"


def save_classified_image(classes: list[str], train_data_dir: str, file_name: str, classification: str) -> None:
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
    Image.open(file_name).crop((65, 190, 355, 515)).save(image_dir)
    os.remove(file_name)


def main() -> None:
    # classes for which to make folders
    classes = ["A1", "A3", "B1", "B3", "C1", "C2", "C3", "None"]

    # locate the training data dir and the file names
    train_data_dir, file_names = prepare_files(classes)

    # crop images
    image_crop_dict = crop_images(file_names)

    # prompt and save each image
    for file_name in image_crop_dict:
        image_crops = image_crop_dict[file_name]
        classification = prompt_for_class(classes,
            os.path.basename(file_name), image_crops)
        save_classified_image(classes, train_data_dir,
                              file_name, classification)


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
