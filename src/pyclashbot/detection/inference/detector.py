import logging

import cv2
import numpy as np
import onnxruntime as ort
from onnx import ModelProto
from onnxconverter_common.float16 import convert_float_to_float16
from onnxmltools.utils import load_model


class OnnxDetector:
    def __init__(self, model_path, use_gpu=False):
        self.model_path = model_path

        providers = list(
            set(ort.get_available_providers())
            & {"CUDAExecutionProvider" if use_gpu else None, "CPUExecutionProvider"}
        )
        logging.info(f"Using providers: {providers}")

        mdl_in = load_model(model_path)
        mdl: ModelProto = convert_float_to_float16(mdl_in)
        self.sess = ort.InferenceSession(
            mdl.SerializeToString(),
            providers=providers,
        )

        self.output_name = self.sess.get_outputs()[0].name

        input_ = self.sess.get_inputs()[0]
        self.input_name = input_.name
        self.model_height, self.model_width = input_.shape[2:]

    def preprocess(self, x: np.ndarray):
        x = cv2.resize(x, (self.model_width, self.model_height))
        return x

    def fix_bboxes(self, x, width, height, padding):
        x[:, [0, 2]] -= padding[0]
        x[:, [1, 3]] -= padding[2]
        x[..., [0, 2]] *= width / (self.model_width - padding[0] - padding[1])
        x[..., [1, 3]] *= height / (self.model_height - padding[2] - padding[3])
        return x

    def _infer(self, x: np.ndarray):
        """
        x,y,3 -> 1,3,x,y
        """

        if x.dtype == np.uint8:
            x = x.astype(np.float16) / 255.0
        else:
            x = x.astype(np.float16)
        x = np.expand_dims(x.transpose(2, 0, 1), axis=0)
        return self.sess.run([self.output_name], {self.input_name: x})[0]

    def run(self, image):
        raise NotImplementedError
