# inference.py - Adapted from clash-royale-fight-vision-demo for py-clash-bot
from itertools import count
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional
import os
import time

import cv2
import numpy as np
import json
import onnxruntime as ort
from PIL import Image, ImageDraw, ImageFont
import re
from pathlib import Path
import torch
from torchvision import transforms


# ---------- Print Flags ----------
DEBUG_PRINT = False  # Set to True to enable debug prints
TIMING_PRINT = False  # Set to True to enable timing prints


# ---------- utils ----------

IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)

# Default stickiness config values - can be overridden by importing tracking config
DEFAULT_DETECTION_SCORE_THRESHOLD = 0.15
DEFAULT_DETECTION_NMS_IOU = 0.7
DEFAULT_MIN_BBOX_AREA = 2


def _fixed_top_strip_pil(pil_img: Image.Image, frac=0.12, fill=(0, 0, 0)):
    w, h = pil_img.size
    band = int(h * frac)
    draw = ImageDraw.Draw(pil_img)
    draw.rectangle([0, 0, w, band], fill=fill)
    return pil_img


def _resize_shorter_side(pil_img: Image.Image, target: int) -> Image.Image:
    w, h = pil_img.size
    if min(w, h) == target:
        return pil_img
    if w < h:
        new_w = target
        new_h = int(h * (target / w))
    else:
        new_h = target
        new_w = int(w * (target / h))
    return pil_img.resize((new_w, new_h), Image.BILINEAR)


def _center_crop(pil_img: Image.Image, size: int) -> Image.Image:
    w, h = pil_img.size
    left = (w - size) // 2
    top = (h - size) // 2
    return pil_img.crop((left, top, left + size, top + size))


def letterbox(img, new_shape=(640, 640), color=(114, 114, 114)):
    h, w = img.shape[:2]
    r = min(new_shape[0] / h, new_shape[1] / w)
    new_unpad = (int(round(w * r)), int(round(h * r)))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]
    dw /= 2
    dh /= 2
    if (w, h) != new_unpad:
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(
        img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color
    )
    return img, r, (left, top)


def xywh2xyxy(x):
    y = np.copy(x)
    y[:, 0] = x[:, 0] - x[:, 2] / 2
    y[:, 1] = x[:, 1] - x[:, 3] / 2
    y[:, 2] = x[:, 0] + x[:, 2] / 2
    y[:, 3] = x[:, 1] + x[:, 3] / 2
    return y


def nms_numpy(boxes, scores, iou_thres=0.45):
    if boxes.size == 0:
        return []
    x1, y1, x2, y2 = boxes.T
    areas = (x2 - x1) * (y2 - y1)
    order = scores.argsort()[::-1]
    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])
        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        inter = w * h
        iou = inter / (areas[i] + areas[order[1:]] - inter + 1e-6)
        inds = np.where(iou <= iou_thres)[0]
        order = order[inds + 1]
    return keep


def choose_providers(prefer_cuda=True):
    av = ort.get_available_providers()
    if prefer_cuda and "CUDAExecutionProvider" in av:
        return ["CUDAExecutionProvider", "CPUExecutionProvider"]
    if "DmlExecutionProvider" in av:
        return ["DmlExecutionProvider", "CPUExecutionProvider"]
    return ["CPUExecutionProvider"]


# ---------- detector ----------


@dataclass
class DetResult:
    xyxy: Tuple[int, int, int, int]
    score: float
    cls: int


def get_stickiness_value(attr_name, default_value):
    """Get value from stickiness config if available, otherwise use default"""
    try:
        from .tracking.stickiness_config import STICKINESS
        return getattr(STICKINESS, attr_name)
    except ImportError:
        return default_value


class UnitDetector:
    """
    Expects a YOLOv5 ONNX exported WITHOUT NMS (default).
    We crop a fixed ROI, letterbox to model size, run, NMS, then map back.
    """

    def __init__(
        self,
        onnx_path: str,
        roi=(56, 60, 360, 470),
        img_size=(640, 640),
        prefer_cuda=True,
    ):
        self.roi = roi  # x1,y1,x2,y2 in original image
        self.img_h, self.img_w = img_size

        self.session = ort.InferenceSession(
            onnx_path, providers=choose_providers(prefer_cuda)
        )
        self.in_name = self.session.get_inputs()[0].name

    def preprocess(self, image_bgr: np.ndarray):
        x1, y1, x2, y2 = self.roi
        crop = image_bgr[y1:y2, x1:x2]  # crop ROI
        rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)  # YOLO expects RGB
        lb, r, (px, py) = letterbox(rgb, (self.img_h, self.img_w))
        im = (lb.astype(np.float32) / 255.0).transpose(2, 0, 1)
        im = np.expand_dims(np.ascontiguousarray(im), 0)
        meta = dict(
            ratio=r, pad=(px, py), roi_offset=(x1, y1), roi_wh=(x2 - x1, y2 - y1)
        )
        return im, meta

    def predict(self, blob: np.ndarray):
        y = self.session.run(None, {self.in_name: blob})[0]  # (1, N, 85)
        return y[0]

    def postprocess(self, pred: np.ndarray, meta) -> List[DetResult]:
        # pred: (N, 5+nc) = [cx,cy,w,h, obj, class_scores...]
        boxes = xywh2xyxy(pred[:, :4])
        obj = pred[:, 4:5]
        cls = pred[:, 5:]
        cls_idx = cls.argmax(1)
        cls_score = cls.max(1)
        scores = obj[:, 0] * cls_score

        # filter using stickiness config or defaults
        detection_threshold = get_stickiness_value('detection_score_threshold', DEFAULT_DETECTION_SCORE_THRESHOLD)
        m = scores > detection_threshold
        boxes, scores, cls_idx = boxes[m], scores[m], cls_idx[m]
        if boxes.size == 0:
            return []

        # undo letterbox
        px, py = meta["pad"]
        r = meta["ratio"]
        w_roi, h_roi = meta["roi_wh"]
        boxes[:, [0, 2]] -= px
        boxes[:, [1, 3]] -= py
        boxes[:, :4] /= r
        boxes[:, [0, 2]] = boxes[:, [0, 2]].clip(0, w_roi - 1)
        boxes[:, [1, 3]] = boxes[:, [1, 3]].clip(0, h_roi - 1)

        # add ROI offset back to full image coords
        offx, offy = meta["roi_offset"]
        boxes[:, [0, 2]] += offx
        boxes[:, [1, 3]] += offy

        # NMS using stickiness config or default
        nms_iou = get_stickiness_value('detection_nms_iou', DEFAULT_DETECTION_NMS_IOU)
        keep = nms_numpy(boxes, scores, nms_iou)
        boxes, scores, cls_idx = boxes[keep], scores[keep], cls_idx[keep]

        out = []
        min_bbox_area = get_stickiness_value('min_bbox_area', DEFAULT_MIN_BBOX_AREA)
        for b, s, c in zip(boxes, scores, cls_idx):
            x1, y1, x2, y2 = [int(round(v)) for v in b]
            # Drop small boxes based on area threshold
            if (x2 - x1) * (y2 - y1) < min_bbox_area:
                continue
            out.append(DetResult((x1, y1, x2, y2), float(s), int(c)))
        return out

    def detect_units(self, image_bgr: np.ndarray) -> List[DetResult]:
        preprocess_start = time.perf_counter()
        blob, meta = self.preprocess(image_bgr)
        preprocess_time = (time.perf_counter() - preprocess_start) * 1000

        predict_start = time.perf_counter()
        pred = self.predict(blob)
        predict_time = (time.perf_counter() - predict_start) * 1000

        postprocess_start = time.perf_counter()
        results = self.postprocess(pred, meta)
        postprocess_time = (time.perf_counter() - postprocess_start) * 1000

        if TIMING_PRINT:
            print(
                f"    Detection - Preprocess: {preprocess_time:.1f}ms, Inference: {predict_time:.1f}ms, Postprocess: {postprocess_time:.1f}ms"
            )
        return results


# ---------- classifier ----------


@dataclass
class ClsResult:
    label: str
    score: float


class UnitClassifier:
    def __init__(
        self,
        onnx_path: str,
        labels: Optional[List[str]] = None,
        input_size=(224, 224),
        prefer_cuda=True,
        labels_path: str = None,
    ):
        self.labels = labels
        self.h, self.w = input_size
        self.session = ort.InferenceSession(
            onnx_path, providers=choose_providers(prefer_cuda)
        )
        self.in_name = self.session.get_inputs()[0].name

        self.label2index = None
        self.index2label = None
        self.labels = None
        
        # Load labels from path if provided, otherwise use default path
        if labels_path:
            self.load_labels(labels_path)
        else:
            # Try to load from models directory
            try:
                models_dir = Path(__file__).parent.parent / "models"
                self.load_labels(str(models_dir / "unit_class_to_idx.json"))
            except Exception:
                # Fallback to relative path for backwards compatibility
                self.load_labels("models/unit_class_to_idx.json")

    def load_labels(self, labels_path: str):
        try:
            with open(labels_path, "r", encoding="utf-8") as f:
                self.label2index = json.load(f)
                self.index2label = {v: k for k, v in self.label2index.items()}
                self.labels = [self.index2label[i] for i in sorted(self.index2label.keys())]
        except Exception as e:
            print(f"Warning: Could not load labels from {labels_path}: {e}")

    def preprocess(self, crop_bgr: np.ndarray, *, return_rgb=False):
        """Mirror the validation pipeline used during training."""
        # BGR -> RGB, to PIL
        rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)

        # 1) hide top band (level indicators)
        pil = _fixed_top_strip_pil(pil, frac=0.12, fill=(0, 0, 0))

        # 2) stretch directly to target size (no aspect ratio preservation)
        pil = pil.resize((self.w, self.h), Image.BILINEAR)

        # 3) to CHW float in [0,1]
        arr = np.asarray(pil).astype(np.float32) / 255.0
        arr = arr.transpose(2, 0, 1)  # HWC -> CHW

        # 4) normalize with ImageNet stats
        mean = np.array(IMAGENET_MEAN, dtype=np.float32)[:, None, None]
        std = np.array(IMAGENET_STD, dtype=np.float32)[:, None, None]
        arr = (arr - mean) / std

        blob = np.expand_dims(np.ascontiguousarray(arr), 0)
        return (blob, np.asarray(pil)) if return_rgb else blob

    def predict(self, blob):
        logits = self.session.run(None, {self.in_name: blob})[0][0]
        p = np.exp(logits - logits.max())
        p = p / p.sum()
        idx = int(np.argmax(p))
        label = "unknown"

        if self.index2label is not None:
            label = self.index2label.get(idx, label)

        return ClsResult(label=label, score=float(p[idx]))

    def classify_unit(self, crop_bgr: np.ndarray) -> ClsResult:
        preprocess_start = time.perf_counter()
        blob = self.preprocess(crop_bgr)
        preprocess_time = (time.perf_counter() - preprocess_start) * 1000

        predict_start = time.perf_counter()
        result = self.predict(blob)
        predict_time = (time.perf_counter() - predict_start) * 1000

        if TIMING_PRINT:
            print(
                f"      Unit Classify - Preprocess: {preprocess_time:.1f}ms, Inference: {predict_time:.1f}ms"
            )
        return result


# ---------- Side Classifier ----------


class SideClassifier:
    """Classifier for determining which side a unit is on (friendly/enemy)."""
    
    def __init__(self, onnx_path: str, input_size=(224, 224), prefer_cuda=True):
        self.h, self.w = input_size
        self.session = ort.InferenceSession(
            onnx_path, providers=choose_providers(prefer_cuda)
        )
        self.in_name = self.session.get_inputs()[0].name
    
    def preprocess(self, crop_bgr: np.ndarray):
        """Preprocess crop for side classification."""
        rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        pil = pil.resize((self.w, self.h), Image.BILINEAR)
        
        arr = np.asarray(pil).astype(np.float32) / 255.0
        arr = arr.transpose(2, 0, 1)  # HWC -> CHW
        
        # Normalize with ImageNet stats
        mean = np.array(IMAGENET_MEAN, dtype=np.float32)[:, None, None]
        std = np.array(IMAGENET_STD, dtype=np.float32)[:, None, None]
        arr = (arr - mean) / std
        
        return np.expand_dims(np.ascontiguousarray(arr), 0)
    
    def predict(self, blob):
        """Predict side (friendly/enemy)."""
        logits = self.session.run(None, {self.in_name: blob})[0][0]
        p = np.exp(logits - logits.max())
        p = p / p.sum()
        
        # Assume binary classification: 0=friendly, 1=enemy
        side = "friendly" if np.argmax(p) == 0 else "enemy"
        confidence = float(p[np.argmax(p)])
        
        return side, confidence
    
    def classify_side(self, crop_bgr: np.ndarray):
        """Classify unit side."""
        blob = self.preprocess(crop_bgr)
        return self.predict(blob)


# ---------- Hand Card Classifier ----------


class HandCardClassifier:
    """Classifier for hand cards."""
    
    def __init__(self, onnx_path: str, labels_path: str, input_size=(224, 224), prefer_cuda=True):
        self.h, self.w = input_size
        self.session = ort.InferenceSession(
            onnx_path, providers=choose_providers(prefer_cuda)
        )
        self.in_name = self.session.get_inputs()[0].name
        
        # Load card labels
        with open(labels_path, 'r', encoding='utf-8') as f:
            self.label2index = json.load(f)
            self.index2label = {v: k for k, v in self.label2index.items()}
    
    def preprocess(self, crop_bgr: np.ndarray):
        """Preprocess hand card crop."""
        rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        pil = pil.resize((self.w, self.h), Image.BILINEAR)
        
        arr = np.asarray(pil).astype(np.float32) / 255.0
        arr = arr.transpose(2, 0, 1)  # HWC -> CHW
        
        # Normalize with ImageNet stats
        mean = np.array(IMAGENET_MEAN, dtype=np.float32)[:, None, None]
        std = np.array(IMAGENET_STD, dtype=np.float32)[:, None, None]
        arr = (arr - mean) / std
        
        return np.expand_dims(np.ascontiguousarray(arr), 0)
    
    def predict(self, blob):
        """Predict card label."""
        logits = self.session.run(None, {self.in_name: blob})[0][0]
        p = np.exp(logits - logits.max())
        p = p / p.sum()
        
        idx = int(np.argmax(p))
        label = self.index2label.get(idx, "unknown")
        confidence = float(p[idx])
        
        return label, confidence
    
    def classify_card(self, crop_bgr: np.ndarray):
        """Classify hand card."""
        blob = self.preprocess(crop_bgr)
        return self.predict(blob)


# ---------- Tower Health Classifiers ----------


class TowerHealthClassifier:
    """Binary classifier for tower health state (destroyed/middle/full)."""
    
    def __init__(self, onnx_path: str, input_size=(224, 224), prefer_cuda=True):
        self.h, self.w = input_size
        self.session = ort.InferenceSession(
            onnx_path, providers=choose_providers(prefer_cuda)
        )
        self.in_name = self.session.get_inputs()[0].name
        self.classes = ["destroyed", "middle", "full"]
    
    def preprocess(self, crop_bgr: np.ndarray):
        """Preprocess tower crop."""
        rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        pil = pil.resize((self.w, self.h), Image.BILINEAR)
        
        arr = np.asarray(pil).astype(np.float32) / 255.0
        arr = arr.transpose(2, 0, 1)  # HWC -> CHW
        
        # Normalize
        mean = np.array(IMAGENET_MEAN, dtype=np.float32)[:, None, None]
        std = np.array(IMAGENET_STD, dtype=np.float32)[:, None, None]
        arr = (arr - mean) / std
        
        return np.expand_dims(np.ascontiguousarray(arr), 0)
    
    def classify(self, crop_bgr: np.ndarray):
        """Classify tower health state."""
        blob = self.preprocess(crop_bgr)
        logits = self.session.run(None, {self.in_name: blob})[0][0]
        p = np.exp(logits - logits.max())
        p = p / p.sum()
        
        idx = int(np.argmax(p))
        classification = self.classes[idx] if idx < len(self.classes) else "unknown"
        confidence = float(p[idx])
        
        return classification, confidence


class TowerHealthRegressor:
    """Regression model for exact tower health percentage."""
    
    def __init__(self, onnx_path: str, input_size=(224, 224), prefer_cuda=True):
        self.h, self.w = input_size
        self.session = ort.InferenceSession(
            onnx_path, providers=choose_providers(prefer_cuda)
        )
        self.in_name = self.session.get_inputs()[0].name
    
    def preprocess(self, crop_bgr: np.ndarray):
        """Preprocess tower crop."""
        rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)
        pil = pil.resize((self.w, self.h), Image.BILINEAR)
        
        arr = np.asarray(pil).astype(np.float32) / 255.0
        arr = arr.transpose(2, 0, 1)  # HWC -> CHW
        
        # Normalize
        mean = np.array(IMAGENET_MEAN, dtype=np.float32)[:, None, None]
        std = np.array(IMAGENET_STD, dtype=np.float32)[:, None, None]
        arr = (arr - mean) / std
        
        return np.expand_dims(np.ascontiguousarray(arr), 0)
    
    def predict_health(self, crop_bgr: np.ndarray):
        """Predict exact health percentage."""
        blob = self.preprocess(crop_bgr)
        health_pct = self.session.run(None, {self.in_name: blob})[0][0][0]
        return max(0.0, min(100.0, float(health_pct)))  # Clamp to 0-100%


# ---------- Main FightVision Class ----------


class FightVision:
    """Main vision system for fight analysis."""
    
    def __init__(self, 
                 det_model: str,
                 cls_model: str, 
                 side_classifier_model: str,
                 hand_card_model: str,
                 hand_card_labels: str,
                 tower_health_classification_model: str,
                 tower_health_regression_model: str,
                 enable_tracking: bool = True,
                 save_crops: bool = False,
                 prefer_cuda: bool = True):
        
        self.save_crops = save_crops
        self.enable_tracking = enable_tracking
        
        # Initialize models
        self.unit_detector = UnitDetector(det_model, prefer_cuda=prefer_cuda)
        self.unit_classifier = UnitClassifier(cls_model, prefer_cuda=prefer_cuda)
        self.side_classifier = SideClassifier(side_classifier_model, prefer_cuda=prefer_cuda)
        self.hand_card_classifier = HandCardClassifier(hand_card_model, hand_card_labels, prefer_cuda=prefer_cuda)
        self.tower_health_classifier = TowerHealthClassifier(tower_health_classification_model, prefer_cuda=prefer_cuda)
        self.tower_health_regressor = TowerHealthRegressor(tower_health_regression_model, prefer_cuda=prefer_cuda)
        
        # Hand card positions (fixed coordinates)
        self.hand_card_positions = [
            (118, 545, 166, 593),  # Card 0
            (186, 545, 234, 593),  # Card 1  
            (254, 545, 302, 593),  # Card 2
            (322, 545, 370, 593),  # Card 3
        ]
        
        # Tower positions (fixed coordinates)
        self.tower_positions = {
            "enemy_left_tower": (75, 120, 125, 170),
            "enemy_right_tower": (315, 120, 365, 170),
            "enemy_main_tower": (195, 80, 245, 130),
            "friendly_left_tower": (75, 400, 125, 450),
            "friendly_right_tower": (315, 400, 365, 450), 
            "friendly_main_tower": (195, 460, 245, 510),
        }
    
    def run(self, image_bgr: np.ndarray, raw_image_bgr: Optional[np.ndarray] = None) -> dict:
        """Run complete vision analysis on battle image."""
        start_time = time.perf_counter()
        
        # Detect units
        unit_detections = self.unit_detector.detect_units(image_bgr)
        
        # Classify each detected unit
        units = []
        for det in unit_detections:
            x1, y1, x2, y2 = det.xyxy
            unit_crop = image_bgr[y1:y2, x1:x2]
            
            if unit_crop.size == 0:
                continue
                
            # Classify unit type
            cls_result = self.unit_classifier.classify_unit(unit_crop)
            
            # Classify side
            side, side_confidence = self.side_classifier.classify_side(unit_crop)
            
            unit_info = {
                "xyxy": det.xyxy,
                "det_score": det.score,
                "cls_label": cls_result.label,
                "cls_score": cls_result.score,
                "side": side,
                "side_score": side_confidence,
                "label": cls_result.label,  # Backwards compatibility
            }
            units.append(unit_info)
        
        # Analyze hand cards (use raw image if available)
        hand_cards = []
        card_image = raw_image_bgr if raw_image_bgr is not None else image_bgr
        
        for i, (x1, y1, x2, y2) in enumerate(self.hand_card_positions):
            if (y2 <= card_image.shape[0] and x2 <= card_image.shape[1] and 
                y1 >= 0 and x1 >= 0):
                
                card_crop = card_image[y1:y2, x1:x2]
                if card_crop.size > 0:
                    label, confidence = self.hand_card_classifier.classify_card(card_crop)
                    hand_cards.append({
                        "position": i,
                        "label": label,
                        "confidence": confidence,
                        "bbox": (x1, y1, x2, y2)
                    })
        
        # Analyze tower health
        tower_health = {}
        for tower_name, (x1, y1, x2, y2) in self.tower_positions.items():
            if (y2 <= image_bgr.shape[0] and x2 <= image_bgr.shape[1] and 
                y1 >= 0 and x1 >= 0):
                
                tower_crop = image_bgr[y1:y2, x1:x2]
                if tower_crop.size > 0:
                    # Get classification first
                    classification, cls_confidence = self.tower_health_classifier.classify(tower_crop)
                    
                    # Get regression value for middle towers
                    if classification == "middle":
                        health_pct = self.tower_health_regressor.predict_health(tower_crop)
                        label = f"{health_pct:.1f}%"
                    else:
                        label = classification
                    
                    tower_health[tower_name] = {
                        "label": label,
                        "classification": classification,
                        "confidence": cls_confidence,
                        "bbox": (x1, y1, x2, y2)
                    }
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        return {
            "units": units,
            "hand_cards": hand_cards,
            "tower_health": tower_health,
            "inference_time_ms": elapsed_ms,
        }