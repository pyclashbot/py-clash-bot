import os

import pyautogui

image_data_path = os.path.dirname(os.path.realpath(__file__))
image_data_path = os.path.join(image_data_path, "image_data")

# method to count the files in a given directory
def count_files_in_dir(dir_path):
    return len(
        [
            name
            for name in os.listdir(dir_path)
            if os.path.isfile(os.path.join(dir_path, name))
        ]
    )


# method to save a screenshot to a given directory
def save_screenshot_for_ML_data():
    # get a screenshot
    screenshot = pyautogui.screenshot(region=[65, 100, 290, 405])

    # show the image we're about to save
    # show_image(screenshot)

    # count files in file
    count = count_files_in_dir(image_data_path)

    # make path of this screenshot
    path = os.path.join(image_data_path, str(count + 1) + ".png")

    screenshot.save(path)

    print("saved to path " + path)
