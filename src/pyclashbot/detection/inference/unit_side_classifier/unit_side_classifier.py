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
        def to_readable(digit):
            digit = float(digit)
            digit = str(digit)
            digit = digit[:3]
            return float(digit)

        def convert_bbox(bbox):
            BBOX_EXPAND_FACTOR = 1.0

            def xywh2xyxy(bbox):
                center_x,center_y,w,h = bbox
                horizontal_adjustment = (w/2)*BBOX_EXPAND_FACTOR
                vertical_adjustment = (h/2)*BBOX_EXPAND_FACTOR

                left = center_x - horizontal_adjustment
                top = center_y - vertical_adjustment
                right = center_x + horizontal_adjustment
                bottom = center_y + vertical_adjustment

                return (left,top,right,bottom)

            bbox = [float(b) for b in bbox]
            bbox = bbox[:4]
            bbox = xywh2xyxy(bbox)
            return bbox

        #convert to rgb from bgr
        image = image[..., ::-1]
        #convert the image to PIL
        image = Image.fromarray(image)
        # convert image to 640x640
        image=resize_pil_image(image,640)
        # crop image to bbox
        bbox = convert_bbox(bbox)
        crop = crop_image(image,bbox)
        #resize to 64
        crop = resize_pil_image(crop,64)
        # crop.show()
        # convert back to numpy
        crop = convert_pil_to_numpy(crop)

        return crop

    def postprocess(self, output: np.ndarray):
        def format_confidence(conf):
            conf = float(conf) * 100
            conf = str(conf)[:5]
            return conf

        output = [float(o) for o in output]
        if output[1] > output[0]:
            return "enemy " + format_confidence(output[1])
        else:
            return "ally " + format_confidence(output[0])

    def run(self, image,bbox):
        image = self.preprocess(image,bbox)
        output = self._infer(image).astype(np.float32)[0]

        return self.postprocess(output)



if __name__ == '__main__':
    pass

