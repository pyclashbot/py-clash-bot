from pyclashbot.memu.client import screenshot
from fastai.learner import load_learner
import time


LABEL_PATH = r"src\pyclashbot\detection\models\plays_labels.txt"


def get_raw_annotation_lines():
    with open(LABEL_PATH, "r") as f:
        return f.readlines()


raw_annotation_lines = get_raw_annotation_lines()


def GetLabel(image_file_name):
    try:
        image_file_name = image_file_name.split(".")[0]  # Remove the extension .jpg
        for line in raw_annotation_lines:
            if image_file_name in line:
                line = line.split(",")[1].replace("\n", "")
                return line
    except Exception as e:
        print(f"An error occurered in GetLabel({image_file_name}) : {e}")
    return None


inx2label = {
    0: "ally_attacking_left",
    1: "ally_attacking_right",
    2: "ally_defending_left",
    3: "ally_defending_right",
    4: "enemy_attacking_left",
    5: "enemy_attacking_right",
    6: "enemy_defending_left",
    7: "enemy_defending_right",
}

label2idx = {v: k for k, v in inx2label.items()}

# load the model
learn_inf = load_learner(r"src\pyclashbot\detection\models\troop_position_detector.pkl")


def choose_play(vm_index):
    ss = screenshot(vm_index)

    label, _, probs = learn_inf.predict(ss)

    print(label, probs[label2idx[label]])


while 1:
    choose_play(12)
    time.sleep(1)
