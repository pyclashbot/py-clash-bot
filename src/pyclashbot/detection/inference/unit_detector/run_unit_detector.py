import logging
import os
from time import perf_counter

import cv2

from pyclashbot.detection.inference.draw import draw_bboxes
from pyclashbot.detection.inference.unit_detector import UnitDetector
from pyclashbot.memu.client import screenshot
from pyclashbot.memu.pmc import pmc

logging.basicConfig(level=logging.INFO)

logging.info("Starting VM")
vm_index = 12
pmc.start_vm(vm_index)
logging.info("VM started")

current_path = os.path.dirname(os.path.realpath(__file__))
model_path = os.path.join(current_path, "unit_detector.onnx")

def detection(detector):
    durations: dict[str, tuple[float, float]] = {}
    start = perf_counter()

    ss = screenshot(vm_index)
    durations["screenshot"] = (start, perf_counter())

    image = detector.preprocess(ss)
    durations["preprocess"] = (durations["screenshot"][1], perf_counter())

    pred = detector.run(image)
    durations["inference"] = (durations["preprocess"][1], perf_counter())

    pred = detector.postprocess(pred)
    durations["postprocess"] = (durations["inference"][1], perf_counter())

    image = draw_bboxes(ss, pred, pred_dims=(640, 640))
    cv2.imshow("Predictions", image)
    if cv2.waitKey(25) == 27:
        raise KeyboardInterrupt
    durations["draw"] = (durations["postprocess"][1], perf_counter())

    durations["total"] = (durations["screenshot"][0], durations["draw"][1])
    return {k: v[1] - v[0] for k, v in durations.items()}


def detection_loop(use_gpu):
    logging.info(f"Loading model from {model_path}")
    detector = UnitDetector(model_path, use_gpu)
    logging.info("Model loaded")

    logging.info("Starting detection loop, ctrl+c to stop")

    durations = []
    while True:
        try:
            duration = detection(detector)
            durations.append(duration)
        except Exception as e:
            logging.error(type(e))
            logging.error(e)
        except KeyboardInterrupt:
            break

    cv2.destroyAllWindows()
    logging.info("Detection loop ended")
    return durations


if __name__ == "__main__":
    durations = detection_loop(use_gpu=True)

    import pandas as pd

    durations = pd.DataFrame(durations)
    durations = durations.iloc[1:]
    logging.info("\n" + str(durations.describe()))
