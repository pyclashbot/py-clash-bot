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

    image_data_folder_path = (
        r"C:\Users\matmi\OneDrive\Desktop\clashbot_fight_ML_image_data"
    )

    # count files in file
    count = count_files_in_dir(image_data_folder_path)

    # make path of this screenshot
    this_screenshot_path = os.path.join(image_data_folder_path, str(count + 1) + ".png")

    screenshot.save(this_screenshot_path)

    print("saved to path " + this_screenshot_path)
