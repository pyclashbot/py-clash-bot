from fastai.vision.all import *

ANNOTATION_TEXT_FILE_PATH = r"src\pyclashbot\detection\models\tower_annotations.txt"

TOWER_REGIONS = [
    (95, 116, 155, 176),
    (268, 116, 328, 176),
    (95, 362, 155, 422),
    (268, 362, 328, 422),
]
# left top right bottom


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


img = Image.open(
    r"C:\My Files\my Programs\clash\tower_annotator\annotated_images\screenshot1713106915.994428_0.png"
)
img.show()
label, _, probs = learn_inf.predict(img)
print(f"This is a {label}")
print(f"prob of destroyed: {convert_to_percent(probs[0].item())}%")
print(f"prob of alive: {convert_to_percent(probs[1].item())}%")
