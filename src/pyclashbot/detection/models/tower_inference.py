from pyclashbot.memu.client import screenshot
from fastai.learner import load_learner
import time
import numpy as np

ANNOTATION_TEXT_FILE_PATH = r"src\pyclashbot\detection\models\tower_annotations.txt"


TOWER_REGIONS = [
    (95, 116, 155, 176),  # left enemy
    (268, 116, 328, 176),  # right enemy
    (95, 362, 155, 422),  # left friendly
    (268, 362, 328, 422),  # right friendly
]


def get_raw_annotations(directory):
    good_lines = []
    with open(directory, "r") as file:
        lines = file.readlines()
        for line in lines:
            good_lines.append(line.strip())

    return lines


def convert_to_percent(num):
    num = num * 100
    return round(num, 2)


def GetLabel(image_file_name):
    image_file_name = image_file_name.replace("\n", "").replace(".png", "")

    annotation_lines = get_raw_annotations(ANNOTATION_TEXT_FILE_PATH)

    for line in annotation_lines:
        if image_file_name in line:
            return line[-2]

    return 3


learn_inf = load_learner(
    r"src\pyclashbot\detection\models\tower_inference_model_2024-05-13_17-57-40.pkl"
)


def get_tower_statuses(vm_index):
    idx2tower = {
        0: "enemy_left",
        1: "enemy_right",
        2: "ally_left",
        3: "ally_right",
    }

    def parse_output(index, label, probs):
        print(idx2tower[index], label)

    tower_statuses = []

    ss = screenshot(vm_index)

    # regions are definted as left, top, right,bottom
    for i, region in enumerate(TOWER_REGIONS):
        iar = np.asarray(ss)

        # crop the iar to the region
        iar = iar[region[1] : region[3], region[0] : region[2]]
        label, _, probs = learn_inf.predict(iar)

        parse_output(i, label, probs)

    return tower_statuses


while 1:
    start_time = time.time()
    print("====================================")
    get_tower_statuses(12)
