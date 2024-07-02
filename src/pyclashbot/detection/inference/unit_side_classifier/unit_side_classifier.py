from PIL import Image
import numpy as np
from pyclashbot.detection.inference.detector import OnnxDetector




def crop_image(image, coords):
    return image.crop(coords)


def resize_pil_image(image, size):
    return image.resize((size, size))


def convert_numpy_to_pil(image):
    return Image.fromarray(image)


def convert_pil_to_numpy(image):
    return np.array(image)


class UnitSideClassifier(OnnxDetector):
    def preprocess(self, image, bbox):
        #convert the image to PIL
        image = Image.fromarray(image)
        # convert image to 640x640
        image=resize_pil_image(image,640)
        # convert bbox to 640x640 dims
        bbox = [int(b*640) for b in bbox]
        # crop image to bbox
        crop = crop_image(image,bbox)
        # convert back to numpy
        crop = convert_pil_to_numpy(crop)

        return crop

    def postprocess(self, output: np.ndarray):
        def format_confidence(conf):
            conf = float(conf) * 100
            conf = str(conf)[:5]
            return conf

        output = [float(o) for o in output]
        if output[0] > output[1]:
            return "enemy " + format_confidence(output[0])
        else:
            return "ally " + format_confidence(output[1])

    def run(self, image,bbox):
        images = self.preprocess(image,bbox)
        outputs = []
        for img in images:
            outputs.append(self._infer(img).astype(np.float32)[0])

        return [self.postprocess(output) for output in outputs]



if __name__ == '__main__':
    pass

