import numpy as np

from pyclashbot.detection.inference.detector import OnnxDetector


class UnitDetector(OnnxDetector):
    MIN_CONF = 0.2
    UNIT_Y_START = 0.05
    UNIT_Y_END = 0.80
    OVERLAP_MAX = 0.3

    def non_max_suppression(self, boxes: np.ndarray, overlap_threshold) -> np.ndarray:
        # overlap_threshold should be between 0 and 1, 1 means no overlap

        if len(boxes) == 0:
            return boxes

        # Unstacking Bounding Box Coordinates
        x_min = boxes[:, 0] - boxes[:, 2] / 2
        y_min = boxes[:, 1] - boxes[:, 3] / 2
        x_max = boxes[:, 0] + boxes[:, 2] / 2
        y_max = boxes[:, 1] + boxes[:, 3] / 2

        # Sorting the pscores in descending order and keeping respective indices.
        sorted_idx = np.argsort(boxes[:, 4])[::-1]
        # Calculating areas of all bboxes.Adding 1 to the side values to avoid zero area bboxes.
        bbox_areas = (x_max - x_min + 1) * (y_max - y_min + 1)

        # list to keep filtered bboxes.
        filtered = []
        while len(sorted_idx) > 0:
            # Keeping highest pscore bbox as reference.
            rbbox_i = sorted_idx[0]
            # Appending the reference bbox index to filtered list.
            filtered.append(rbbox_i)

            # Calculating (xmin,ymin,xmax,ymax) coordinates of all bboxes w.r.t to reference bbox
            overlap_xmins = np.maximum(x_min[rbbox_i], x_min[sorted_idx[1:]])
            overlap_ymins = np.maximum(y_min[rbbox_i], y_min[sorted_idx[1:]])
            overlap_xmaxs = np.minimum(x_max[rbbox_i], x_max[sorted_idx[1:]])
            overlap_ymaxs = np.minimum(y_max[rbbox_i], y_max[sorted_idx[1:]])

            # Calculating overlap bbox widths,heights and there by areas.
            overlap_widths = np.maximum(0, (overlap_xmaxs - overlap_xmins + 1))
            overlap_heights = np.maximum(0, (overlap_ymaxs - overlap_ymins + 1))
            overlap_areas = overlap_widths * overlap_heights

            # Calculating IOUs for all bboxes except reference bbox
            ious = overlap_areas / (
                bbox_areas[rbbox_i] + bbox_areas[sorted_idx[1:]] - overlap_areas
            )

            # select indices for which IOU is greather than threshold
            delete_idx = np.nonzero(ious > overlap_threshold)[0] + 1
            delete_idx = np.concatenate(([0], delete_idx))

            # delete the above indices
            sorted_idx = np.delete(sorted_idx, delete_idx)

        # Return filtered bboxes
        out = boxes[filtered]
        return out

    def postprocess(self, pred: np.ndarray):
        pred = np.array(pred[pred[:, 4] > self.MIN_CONF])
        pred = self.non_max_suppression(pred, self.OVERLAP_MAX)
        return pred

    def run(self, image):
        return self._infer(image).astype(np.float32)[0]
