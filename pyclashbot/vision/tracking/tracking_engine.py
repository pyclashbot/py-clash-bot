# tracking_engine.py
"""
Tracking and smoothing module - responsible for parsing multiple inference results OVER TIME.
Handles smoothness, tracking, filtering, and anything else involving multiple inference points.
"""
import time
import uuid
from dataclasses import dataclass
from collections import deque, Counter
from typing import List, Dict, Any, Optional
import numpy as np

from .stickiness_config import STICKINESS

# Import timing flags from fight.py if available, otherwise use defaults
try:
    from pyclashbot.bot.fight import TIMING_INFERENCE
except ImportError:
    TIMING_INFERENCE = False


# ---------- Unit Tracking ----------


@dataclass
class Track:
    """Represents a single unit being tracked across frames."""

    track_id: str
    bbox_history: deque  # (x1, y1, x2, y2) history
    class_history: deque  # classification results history
    side_history: deque  # side classification history
    score_history: deque  # detection scores
    frames_since_update: int = 0
    age: int = 0
    birth_time: float = 0.0  # time when track was created

    def __post_init__(self):
        if not isinstance(self.bbox_history, deque):
            self.bbox_history = deque(maxlen=STICKINESS.track_history_length)
        if not isinstance(self.class_history, deque):
            self.class_history = deque(maxlen=STICKINESS.track_history_length)
        if not isinstance(self.side_history, deque):
            self.side_history = deque(maxlen=STICKINESS.track_history_length)
        if not isinstance(self.score_history, deque):
            self.score_history = deque(maxlen=STICKINESS.track_history_length)
        if self.birth_time == 0.0:
            self.birth_time = time.time()

    @property
    def smoothed_bbox(self):
        """Return exponentially smoothed bounding box."""
        if not self.bbox_history:
            return None

        # Use unified smoothing decay for all units
        decay_factor = STICKINESS.bbox_smoothing_decay

        # Exponential moving average
        weights = [decay_factor**i for i in range(len(self.bbox_history))]
        weights.reverse()  # Most recent frame gets highest weight
        weight_sum = sum(weights)

        smoothed = [0, 0, 0, 0]
        for i, bbox in enumerate(self.bbox_history):
            weight = weights[i] / weight_sum
            for j in range(4):
                smoothed[j] += bbox[j] * weight

        return tuple(int(coord) for coord in smoothed)

    @property
    def smoothed_class(self):
        """Return most common class from recent history."""
        if not self.class_history:
            return "unknown"
        return Counter(self.class_history).most_common(1)[0][0]

    @property
    def smoothed_side(self):
        """Return most common side from recent history."""
        if not self.side_history:
            return "unknown"
        return Counter(self.side_history).most_common(1)[0][0]

    @property
    def smoothed_score(self):
        """Return confidence-weighted average score."""
        if not self.score_history:
            return 0.0
        return sum(self.score_history) / len(self.score_history)

    @property
    def centroid(self):
        """Return current centroid of the track."""
        bbox = self.smoothed_bbox
        if bbox is None:
            return None
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    @property
    def time_alive(self):
        """Return time alive in seconds since track was created."""
        return time.time() - self.birth_time

    def update(self, bbox, cls_label, side, score):
        """Update track with new detection."""
        # Check for side inconsistency - if side changed dramatically, this might be a different unit
        if len(self.side_history) > 0:
            current_side = self.smoothed_side
            if current_side != "unknown" and side != "unknown" and current_side != side:
                # Side conflict detected - reduce track confidence/age to encourage new track creation
                self.age = max(1, self.age // 2)  # Cut age in half to reduce stickiness
                print(
                    f"[Track] Side conflict: {current_side} -> {side}, reducing track confidence"
                )

        self.bbox_history.append(bbox)
        self.class_history.append(cls_label)
        self.side_history.append(side)
        self.score_history.append(score)
        self.frames_since_update = 0
        self.age += 1

    def predict_next_bbox(self):
        """Linear prediction for next frame based on velocity."""
        if len(self.bbox_history) < 2:
            return self.smoothed_bbox

        # Simple velocity-based prediction
        recent = list(self.bbox_history)[-2:]
        dx = recent[1][0] - recent[0][0]
        dy = recent[1][1] - recent[0][1]
        dw = recent[1][2] - recent[0][2]
        dh = recent[1][3] - recent[0][3]

        current = recent[1]
        predicted = (current[0] + dx, current[1] + dy, current[2] + dw, current[3] + dh)
        return predicted


class UnitTracker:
    """Multi-object tracker for units across video frames."""

    def __init__(
        self,
        max_disappeared=None,
        min_track_age=None,
        iou_threshold=None,
        distance_threshold=None,
    ):
        self.tracks = {}  # track_id -> Track
        # Use stickiness config with fallback to original defaults
        self.max_disappeared = max_disappeared or STICKINESS.track_max_disappeared
        self.min_track_age = min_track_age or STICKINESS.track_min_age
        self.iou_threshold = iou_threshold or STICKINESS.track_iou_threshold
        self.distance_threshold = (
            distance_threshold or STICKINESS.track_distance_threshold
        )

    def _compute_iou(self, box1, box2):
        """Compute IoU between two bounding boxes."""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        if x2 <= x1 or y2 <= y1:
            return 0.0

        intersection = (x2 - x1) * (y2 - y1)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection

        return intersection / union if union > 0 else 0.0

    def _compute_distance(self, center1, center2):
        """Compute Euclidean distance between two centroids."""
        return ((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2) ** 0.5

    def _associate_detections_to_tracks(self, detections):
        """Associate new detections with existing tracks using IoU + distance."""
        if not self.tracks:
            return {}, list(range(len(detections)))

        # Get track predictions and centroids
        track_ids = list(self.tracks.keys())
        track_bboxes = []
        track_centroids = []

        for tid in track_ids:
            track = self.tracks[tid]
            predicted_bbox = track.predict_next_bbox()
            track_bboxes.append(predicted_bbox)

            # Calculate predicted centroid
            if predicted_bbox:
                cx = (predicted_bbox[0] + predicted_bbox[2]) / 2
                cy = (predicted_bbox[1] + predicted_bbox[3]) / 2
                track_centroids.append((cx, cy))
            else:
                track_centroids.append((0, 0))

        # Calculate detection centroids
        det_centroids = []
        det_bboxes = []
        for det in detections:
            bbox = det["xyxy"]
            det_bboxes.append(bbox)
            cx = (bbox[0] + bbox[2]) / 2
            cy = (bbox[1] + bbox[3]) / 2
            det_centroids.append((cx, cy))

        # Compute cost matrix (IoU + normalized distance)
        if len(track_bboxes) > 0 and len(det_bboxes) > 0:
            iou_matrix = np.zeros((len(track_bboxes), len(det_bboxes)))
            dist_matrix = np.zeros((len(track_bboxes), len(det_bboxes)))

            for i, track_bbox in enumerate(track_bboxes):
                for j, det_bbox in enumerate(det_bboxes):
                    iou_matrix[i, j] = self._compute_iou(track_bbox, det_bbox)
                    dist_matrix[i, j] = self._compute_distance(
                        track_centroids[i], det_centroids[j]
                    )

            # Normalize distance matrix
            max_dist = max(dist_matrix.max(), 1.0)
            dist_matrix = dist_matrix / max_dist

            # Combined cost (higher is better for IoU, lower is better for distance)
            cost_matrix = iou_matrix - 0.5 * dist_matrix
        else:
            cost_matrix = np.array([])

        # Simple greedy assignment (for more complex scenarios, use Hungarian algorithm)
        matched_tracks = {}
        matched_detections = set()

        if cost_matrix.size > 0:
            # Find best matches above threshold
            for _ in range(min(len(track_ids), len(detections))):
                if cost_matrix.size == 0:
                    break

                # Find best match
                best_track_idx, best_det_idx = np.unravel_index(
                    cost_matrix.argmax(), cost_matrix.shape
                )
                best_iou = iou_matrix[best_track_idx, best_det_idx]
                best_dist = dist_matrix[best_track_idx, best_det_idx] * max_dist

                # Get track side for side-aware thresholds
                track_id = track_ids[best_track_idx]
                track_side = self.tracks[track_id].smoothed_side
                detection_side = detections[best_det_idx].get("side", "unknown")

                # Use unified distance threshold
                distance_threshold = STICKINESS.track_distance_threshold

                # Check for side conflicts - don't match if sides are different and both are known
                side_conflict = (
                    track_side != "unknown"
                    and detection_side != "unknown"
                    and track_side != detection_side
                )

                # Check if match is good enough with side-aware thresholds
                if (
                    best_iou >= STICKINESS.track_iou_threshold
                    and best_dist <= distance_threshold
                    and not side_conflict
                ):

                    matched_tracks[track_id] = best_det_idx
                    matched_detections.add(best_det_idx)

                    # Remove this match from consideration
                    cost_matrix[best_track_idx, :] = -np.inf
                    cost_matrix[:, best_det_idx] = -np.inf
                else:
                    break

        # Find unmatched detections
        unmatched_detections = [
            i for i in range(len(detections)) if i not in matched_detections
        ]

        return matched_tracks, unmatched_detections

    def update(self, detections):
        """Update tracker with new frame detections."""
        # Increment age and frames_since_update for all tracks
        for track in self.tracks.values():
            track.frames_since_update += 1
            track.age += 1

        # Associate detections to tracks
        matched_tracks, unmatched_detections = self._associate_detections_to_tracks(
            detections
        )

        # Update matched tracks
        for track_id, det_idx in matched_tracks.items():
            detection = detections[det_idx]
            track = self.tracks[track_id]
            track.update(
                bbox=detection["xyxy"],
                cls_label=detection.get("cls_label", "unknown"),
                side=detection.get("side", "unknown"),
                score=detection.get("det_score", 0.0),
            )

        # Create new tracks for unmatched detections
        for det_idx in unmatched_detections:
            detection = detections[det_idx]
            track_id = str(uuid.uuid4())[:8]  # Short unique ID

            new_track = Track(
                track_id=track_id,
                bbox_history=deque(maxlen=STICKINESS.track_history_length),
                class_history=deque(maxlen=STICKINESS.track_history_length),
                side_history=deque(maxlen=STICKINESS.track_history_length),
                score_history=deque(maxlen=STICKINESS.track_history_length),
                birth_time=time.time(),
            )

            new_track.update(
                bbox=detection["xyxy"],
                cls_label=detection.get("cls_label", "unknown"),
                side=detection.get("side", "unknown"),
                score=detection.get("det_score", 0.0),
            )

            self.tracks[track_id] = new_track

        # Remove old tracks (use current stickiness settings)
        tracks_to_remove = []
        for track_id, track in self.tracks.items():
            if track.frames_since_update > STICKINESS.track_max_disappeared:
                tracks_to_remove.append(track_id)

        for track_id in tracks_to_remove:
            del self.tracks[track_id]

    def get_smoothed_results(self):
        """Get smoothed tracking results for current frame."""
        results = []

        for track_id, track in self.tracks.items():
            # Only return tracks that are active and have enough history (use current stickiness)
            if track.frames_since_update == 0 and track.age >= STICKINESS.track_min_age:

                smoothed_bbox = track.smoothed_bbox
                if smoothed_bbox is not None:
                    result = {
                        "track_id": track_id,
                        "xyxy": smoothed_bbox,
                        "det_score": track.smoothed_score,
                        "cls_label": track.smoothed_class,
                        "label": track.smoothed_class,
                        "cls_score": track.smoothed_score,
                        "side": track.smoothed_side,
                        "side_score": track.smoothed_score,
                        "track_age": track.age,
                        "track_confidence": min(
                            1.0, track.age / 10.0
                        ),  # Confidence grows with age
                        "time_alive": track.time_alive,
                    }
                    results.append(result)

        return results


# ---------- Hand Card Tracking ----------


@dataclass
class HandCardTrack:
    """Represents tracking history for a single hand card position."""

    position: int
    label_history: deque  # Recent card labels
    confidence_history: deque  # Recent confidences
    frames_since_update: int = 0

    def __post_init__(self):
        if not isinstance(self.label_history, deque):
            self.label_history = deque(maxlen=STICKINESS.hand_card_history_length)
        if not isinstance(self.confidence_history, deque):
            self.confidence_history = deque(maxlen=STICKINESS.hand_card_history_length)

    @property
    def smoothed_label(self):
        """Return label prioritizing the most recent prediction (cards change instantly!)."""
        if not self.label_history:
            return "unknown"

        # For hand cards, heavily prioritize the most recent prediction
        # since cards change completely when played
        if len(self.label_history) == 1:
            return self.label_history[-1]  # Only one prediction, use it

        # If we have multiple predictions, give exponentially more weight to recent ones
        recent_label = self.label_history[-1]  # Most recent
        recent_conf = self.confidence_history[-1]

        # If recent prediction is confident enough, use it immediately
        if recent_conf >= 0.3:  # Low threshold for immediate updates
            return recent_label

        # Otherwise, use confidence-weighted recent bias
        label_scores = {}
        for i, (label, conf) in enumerate(
            zip(self.label_history, self.confidence_history)
        ):
            if label not in label_scores:
                label_scores[label] = 0
            # Exponentially weight recent predictions (most recent gets 4x weight)
            recency_weight = 2**i  # 1, 2, 4, 8... (most recent gets highest)
            label_scores[label] += conf * recency_weight

        return max(label_scores.items(), key=lambda x: x[1])[0]

    @property
    def smoothed_confidence(self):
        """Return confidence prioritizing recent predictions."""
        if not self.confidence_history:
            return 0.0
        # For hand cards, prioritize the most recent confidence
        # since old predictions become irrelevant when cards are played
        if len(self.confidence_history) == 1:
            return self.confidence_history[-1]

        # Weight recent confidences more heavily
        total_weight = 0
        weighted_sum = 0
        for i, conf in enumerate(self.confidence_history):
            weight = 2**i  # Exponential weighting favoring recent frames
            weighted_sum += conf * weight
            total_weight += weight

        try:
            return weighted_sum / total_weight if total_weight > 0 else 0.0
        except Exception as e:
            print(
                f"[!] Warning HandCardTrack smoothed_confidence experienced this error: {e}"
            )
            return 0.0

    def update(self, label, confidence):
        """Update track with new detection."""
        self.label_history.append(label)
        self.confidence_history.append(confidence)
        self.frames_since_update = 0

    def is_stable(self):
        """Check if card prediction is stable enough to show (very lenient for hand cards)."""
        if not self.label_history:
            return False

        # For hand cards, prioritize showing recent predictions immediately
        # Check if we have minimum frames AND recent prediction is confident enough
        has_min_frames = (
            len(self.label_history) >= STICKINESS.hand_card_min_stability_frames
        )

        # Use the most recent confidence for threshold check (not smoothed)
        recent_confidence = (
            self.confidence_history[-1] if self.confidence_history else 0.0
        )
        meets_threshold = recent_confidence >= STICKINESS.hand_card_confidence_threshold

        return has_min_frames and meets_threshold


class HandCardTracker:
    """Tracks hand cards across frames with temporal smoothing."""

    def __init__(self):
        # Track for each of the 4 card positions
        self.tracks = {
            0: HandCardTrack(
                position=0, label_history=deque(), confidence_history=deque()
            ),
            1: HandCardTrack(
                position=1, label_history=deque(), confidence_history=deque()
            ),
            2: HandCardTrack(
                position=2, label_history=deque(), confidence_history=deque()
            ),
            3: HandCardTrack(
                position=3, label_history=deque(), confidence_history=deque()
            ),
        }

    def update(self, hand_card_results):
        """Update tracker with new frame's hand card detections."""
        # Increment frames_since_update for all tracks
        for track in self.tracks.values():
            track.frames_since_update += 1

        # Update with new detections
        for result in hand_card_results:
            position = result["position"]
            label = result["label"]
            confidence = result["confidence"]

            if position in self.tracks:
                self.tracks[position].update(label, confidence)

    def get_smoothed_results(self):
        """Get smoothed hand card results for current frame."""
        results = []

        for position, track in self.tracks.items():
            # Only return stable predictions
            if track.is_stable():
                result = {
                    "position": position,
                    "label": track.smoothed_label,
                    "confidence": track.smoothed_confidence,
                    "stability": len(track.label_history),
                    "frames_since_update": track.frames_since_update,
                }
                results.append(result)

        return results


# ---------- Tower Health Tracking ----------


@dataclass
class TowerHealthTrack:
    """Represents tracking history for a single tower's health."""

    tower_name: str
    classification_history: deque  # Recent classifications (destroyed, middle, full)
    confidence_history: deque  # Recent confidences
    health_value_history: deque  # Recent health percentage values (for middle towers)
    frames_since_update: int = 0

    def __post_init__(self):
        max_len = 5  # Keep short history for tower health (changes slowly)
        if not isinstance(self.classification_history, deque):
            self.classification_history = deque(maxlen=max_len)
        if not isinstance(self.confidence_history, deque):
            self.confidence_history = deque(maxlen=max_len)
        if not isinstance(self.health_value_history, deque):
            self.health_value_history = deque(maxlen=max_len)

    @property
    def smoothed_classification(self):
        """Return most common classification from recent history."""
        if not self.classification_history:
            return "unknown"
        return Counter(self.classification_history).most_common(1)[0][0]

    @property
    def smoothed_health_value(self):
        """Return smoothed health percentage (for middle towers)."""
        if not self.health_value_history:
            return 0.0
        
        # Use exponential moving average with decay factor
        decay_factor = STICKINESS.tower_health_smoothing
        weights = [decay_factor**i for i in range(len(self.health_value_history))]
        weights.reverse()  # Most recent gets highest weight
        weight_sum = sum(weights)
        
        weighted_sum = sum(val * weight for val, weight in zip(self.health_value_history, weights))
        return weighted_sum / weight_sum if weight_sum > 0 else 0.0

    @property
    def smoothed_confidence(self):
        """Return average confidence."""
        if not self.confidence_history:
            return 0.0
        return sum(self.confidence_history) / len(self.confidence_history)

    def update(self, classification, confidence, health_value=None):
        """Update track with new tower health detection."""
        self.classification_history.append(classification)
        self.confidence_history.append(confidence)
        if health_value is not None:
            self.health_value_history.append(health_value)
        self.frames_since_update = 0

    def get_smoothed_result(self):
        """Get smoothed tower health result."""
        smoothed_class = self.smoothed_classification
        smoothed_conf = self.smoothed_confidence
        
        if smoothed_class == "middle" and self.health_value_history:
            # Use smoothed health value for middle towers
            smoothed_health = self.smoothed_health_value
            final_label = f"{smoothed_health:.1f}%"
        else:
            final_label = smoothed_class
        
        return {
            "label": final_label,
            "classification": smoothed_class,
            "confidence": smoothed_conf,
        }


class TowerHealthTracker:
    """Tracks tower health across frames with temporal smoothing."""

    def __init__(self):
        # Track for each tower
        self.tracks = {}
        self.tower_names = [
            "enemy_left_tower",
            "friendly_left_tower", 
            "enemy_right_tower",
            "friendly_right_tower",
            "enemy_main_tower",
            "friendly_main_tower",
        ]
        
        for name in self.tower_names:
            self.tracks[name] = TowerHealthTrack(
                tower_name=name,
                classification_history=deque(),
                confidence_history=deque(),
                health_value_history=deque(),
            )

    def update(self, tower_health_results):
        """Update tracker with new frame's tower health detections."""
        # Increment frames_since_update for all tracks
        for track in self.tracks.values():
            track.frames_since_update += 1

        # Update with new detections
        for tower_name, result in tower_health_results.items():
            if tower_name in self.tracks:
                classification = result["classification"]
                confidence = result["confidence"]
                
                # Extract health value if it's a percentage string
                health_value = None
                if "%" in result["label"]:
                    try:
                        health_value = float(result["label"].replace("%", ""))
                    except ValueError:
                        pass
                
                self.tracks[tower_name].update(classification, confidence, health_value)

    def get_smoothed_results(self):
        """Get smoothed tower health results for current frame."""
        results = {}
        
        for tower_name, track in self.tracks.items():
            # Only return towers that have been updated recently
            if track.frames_since_update == 0:
                results[tower_name] = track.get_smoothed_result()
        
        return results


# ---------- Main Tracking Engine ----------


class TrackingEngine:
    """
    Main tracking engine that coordinates all tracking and smoothing operations.
    Handles multi-frame analysis for units, hand cards, and tower health.
    """
    
    def __init__(self, enable_unit_tracking=True, enable_hand_card_tracking=True, enable_tower_health_tracking=True):
        self.enable_unit_tracking = enable_unit_tracking
        self.enable_hand_card_tracking = enable_hand_card_tracking
        self.enable_tower_health_tracking = enable_tower_health_tracking
        
        # Initialize trackers
        self.unit_tracker = UnitTracker() if enable_unit_tracking else None
        self.hand_card_tracker = HandCardTracker() if enable_hand_card_tracking else None
        self.tower_health_tracker = TowerHealthTracker() if enable_tower_health_tracking else None
    
    def update(self, inference_results: dict) -> dict:
        """
        Update all trackers with new inference results and return smoothed results.
        
        Args:
            inference_results: Raw inference results from InferenceEngine
            
        Returns:
            Dictionary with smoothed/tracked results
        """
        start_time = time.perf_counter()
        
        # Update unit tracking
        unit_tracking_start = time.perf_counter()
        if self.unit_tracker and "units" in inference_results:
            self.unit_tracker.update(inference_results["units"])
            smoothed_units = self.unit_tracker.get_smoothed_results()
        else:
            smoothed_units = inference_results.get("units", [])
        unit_tracking_time = (time.perf_counter() - unit_tracking_start) * 1000
        
        # Update hand card tracking
        hand_card_tracking_start = time.perf_counter()
        if self.hand_card_tracker and "hand_cards" in inference_results:
            self.hand_card_tracker.update(inference_results["hand_cards"])
            smoothed_hand_cards = self.hand_card_tracker.get_smoothed_results()
        else:
            smoothed_hand_cards = inference_results.get("hand_cards", [])
        hand_card_tracking_time = (time.perf_counter() - hand_card_tracking_start) * 1000
        
        # Update tower health tracking
        tower_tracking_start = time.perf_counter()
        if self.tower_health_tracker and "tower_health" in inference_results:
            self.tower_health_tracker.update(inference_results["tower_health"])
            smoothed_tower_health = self.tower_health_tracker.get_smoothed_results()
        else:
            smoothed_tower_health = inference_results.get("tower_health", {})
        tower_tracking_time = (time.perf_counter() - tower_tracking_start) * 1000
        
        tracking_time = (time.perf_counter() - start_time) * 1000
        
        # Print detailed timing breakdown if enabled
        if TIMING_INFERENCE:
            print(f"  Tracking Engine Timing:")
            print(f"    Unit Tracking: {unit_tracking_time:.1f}ms ({len(smoothed_units)} units)")
            print(f"    Hand Card Tracking: {hand_card_tracking_time:.1f}ms ({len(smoothed_hand_cards)} cards)")
            print(f"    Tower Health Tracking: {tower_tracking_time:.1f}ms ({len(smoothed_tower_health)} towers)")
            print(f"    Total Tracking Time: {tracking_time:.1f}ms")
        
        return {
            "units": smoothed_units,
            "hand_cards": smoothed_hand_cards,
            "tower_health": smoothed_tower_health,
            "tracking_time_ms": tracking_time,
        }
    
    def get_tracking_stats(self) -> dict:
        """Get statistics about current tracking state."""
        stats = {}
        
        if self.unit_tracker:
            stats["active_unit_tracks"] = len([
                track for track in self.unit_tracker.tracks.values()
                if track.frames_since_update == 0
            ])
            stats["total_unit_tracks"] = len(self.unit_tracker.tracks)
        
        if self.hand_card_tracker:
            stats["stable_hand_cards"] = len([
                track for track in self.hand_card_tracker.tracks.values()
                if track.is_stable()
            ])
        
        if self.tower_health_tracker:
            stats["active_tower_tracks"] = len([
                track for track in self.tower_health_tracker.tracks.values()
                if track.frames_since_update == 0
            ])
        
        return stats


if __name__ == "__main__":
    pass