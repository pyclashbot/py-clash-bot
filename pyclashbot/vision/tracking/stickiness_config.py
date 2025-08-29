# stickiness_config.py
"""
Discrete 'stickiness' variables for manual adjustment of bbox tracking, 
averaging, and retention parameters during runtime.
"""

class StickinessConfig:
    """
    Central configuration for all tracking and smoothing parameters.
    Adjust these values manually based on runtime observations.
    """
    
    def __init__(self):
        # === TRACKING PARAMETERS ===
        
        # How many frames a track can disappear before deletion
        self.track_max_disappeared = 15  # 10-30 range, higher = more persistent
        
        # Minimum age before track is considered "mature" and shown
        self.track_min_age = 1  # Reduced for faster small unit tracking
        
        # IoU threshold for matching detections to tracks
        self.track_iou_threshold = 0.1  # Lower for small units that move quickly
        
        # Distance threshold for matching (pixels)
        self.track_distance_threshold = 60  # Unified threshold for all units
        
        # History length for smoothing (affects memory usage)
        self.track_history_length = 3  # Reduced for more responsive small unit tracking
        
        
        # === BBOX SMOOTHING PARAMETERS ===
        
        # Exponential moving average decay factor (0.0-1.0)
        # Higher = more weight to recent frames, lower = smoother but laggier
        self.bbox_smoothing_decay = 0.87  # Unified smoothing for all units
        
        # Minimum bbox change to trigger update (pixels)
        self.bbox_min_change_threshold = 1.0  # 0.5-5.0, higher = less jittery
        
        
        # === CLASSIFICATION SMOOTHING ===
        
        # Confidence threshold for classification updates
        self.cls_confidence_threshold = 0.5  # 0.3-0.8, higher = more conservative
        
        # How many frames of same class needed to change label
        self.cls_stability_frames = 3  # 1-7, higher = more stable labels
        
        
        # === SIDE CLASSIFICATION SMOOTHING ===
        
        # Confidence threshold for side classification updates  
        self.side_confidence_threshold = 0.6  # 0.4-0.9
        
        # Frames of consistency needed to change side
        self.side_stability_frames = 1  # More responsive to prevent sticky misclassifications
        
        
        # === DETECTION FILTERING ===
        
        # Score threshold before tracking (pre-filter weak detections)
        self.detection_score_threshold = 0.15  # 0.1-0.5
        
        # IoU threshold for detection NMS
        self.detection_nms_iou = 0.7  # Higher = more overlapping boxes allowed (up to 70% overlap)
        
        # Minimum bbox size to keep (width * height)
        self.min_bbox_area = 2  # Reduced from 4 to allow smaller boxes
        
        
        # === TOWER HEALTH PARAMETERS ===
        
        # Smoothing factor for tower health regression values
        self.tower_health_smoothing = 0.8  # 0.5-0.95
        
        # Confidence threshold for tower classification changes
        self.tower_classification_threshold = 0.7  # 0.5-0.9
        
        
        # === HAND CARD PARAMETERS ===
        # Hand cards change instantly when played - prioritize recent predictions!
        
        # History length for hand card smoothing (minimal for instant updates)
        self.hand_card_history_length = 1  # Only current frame - no history!
        
        # Minimum frames needed before showing a card prediction (immediate)
        self.hand_card_min_stability_frames = 1  # Show immediately - no stability required
        
        # Confidence threshold for showing hand card predictions (low for responsiveness)
        self.hand_card_confidence_threshold = 0.2  # Very low threshold for quick updates
        
        
        # === RUNTIME ADJUSTMENT HELPERS ===
        
    def make_tracking_more_sticky(self):
        """Increase persistence and smoothing for more stable tracking."""
        self.track_max_disappeared += 5
        self.track_min_age += 1
        self.track_iou_threshold -= 0.05
        self.track_distance_threshold += 20
        self.bbox_smoothing_decay -= 0.1
        print("🔧 Made tracking MORE sticky")
        
    def make_tracking_less_sticky(self):
        """Decrease persistence for more responsive tracking."""
        self.track_max_disappeared = max(5, self.track_max_disappeared - 5)
        self.track_min_age = max(1, self.track_min_age - 1)  
        self.track_iou_threshold = min(0.5, self.track_iou_threshold + 0.05)
        self.track_distance_threshold = max(30, self.track_distance_threshold - 20)
        self.bbox_smoothing_decay = min(0.9, self.bbox_smoothing_decay + 0.1)
        print("🔧 Made tracking LESS sticky")
        
    def make_classification_more_stable(self):
        """Require more confidence/consistency for label changes."""
        self.cls_confidence_threshold += 0.05
        self.cls_stability_frames += 1
        self.side_confidence_threshold += 0.05
        self.side_stability_frames += 1
        print("🔧 Made classification MORE stable")
        
    def make_classification_more_responsive(self):
        """Allow faster label changes with less confidence."""
        self.cls_confidence_threshold = max(0.2, self.cls_confidence_threshold - 0.05)
        self.cls_stability_frames = max(1, self.cls_stability_frames - 1)
        self.side_confidence_threshold = max(0.3, self.side_confidence_threshold - 0.05)
        self.side_stability_frames = max(1, self.side_stability_frames - 1)
        print("🔧 Made classification MORE responsive")
        
    def reset_to_defaults(self):
        """Reset all parameters to default values."""
        self.__init__()
        print("🔧 Reset all stickiness parameters to defaults")
        
    def print_current_settings(self):
        """Print current parameter values for debugging."""
        print("=" * 50)
        print("CURRENT STICKINESS SETTINGS:")
        print("=" * 50)
        print("TRACKING:")
        print(f"  max_disappeared: {self.track_max_disappeared}")
        print(f"  min_age: {self.track_min_age}")
        print(f"  iou_threshold: {self.track_iou_threshold:.3f}")
        print(f"  distance_threshold: {self.track_distance_threshold}")
        print(f"  history_length: {self.track_history_length}")
        print()
        print("BBOX SMOOTHING:")
        print(f"  smoothing_decay: {self.bbox_smoothing_decay:.3f}")
        print(f"  min_change_threshold: {self.bbox_min_change_threshold}")
        print()
        print("CLASSIFICATION:")
        print(f"  cls_confidence_threshold: {self.cls_confidence_threshold:.3f}")
        print(f"  cls_stability_frames: {self.cls_stability_frames}")
        print(f"  side_confidence_threshold: {self.side_confidence_threshold:.3f}")
        print(f"  side_stability_frames: {self.side_stability_frames}")
        print()
        print("DETECTION:")
        print(f"  score_threshold: {self.detection_score_threshold:.3f}")
        print(f"  nms_iou: {self.detection_nms_iou:.3f}")
        print(f"  min_bbox_area: {self.min_bbox_area}")
        print("=" * 50)


# Global instance - import this to adjust parameters
STICKINESS = StickinessConfig()


# Keyboard shortcuts for runtime adjustment
def setup_runtime_controls():
    """
    Print keyboard shortcuts for runtime parameter adjustment.
    Call this from your main loop setup.
    """
    print("🎛️  RUNTIME STICKINESS CONTROLS:")
    print("  Press 'q' in CV window + these keys:")
    print("  1 - Make tracking MORE sticky")
    print("  2 - Make tracking LESS sticky") 
    print("  3 - Make classification MORE stable")
    print("  4 - Make classification MORE responsive")
    print("  0 - Reset to defaults")
    print("  p - Print current settings")
    print("  ESC - Quit")


def handle_key_input(key):
    """
    Handle keyboard input for runtime parameter adjustment.
    Call this from your main loop with cv2.waitKey() result.
    
    Args:
        key: Result from cv2.waitKey() & 0xFF
        
    Returns:
        bool: True if should quit, False to continue
    """
    if key == ord('1'):
        STICKINESS.make_tracking_more_sticky()
    elif key == ord('2'):
        STICKINESS.make_tracking_less_sticky()
    elif key == ord('3'):
        STICKINESS.make_classification_more_stable()
    elif key == ord('4'):
        STICKINESS.make_classification_more_responsive()
    elif key == ord('0'):
        STICKINESS.reset_to_defaults()
    elif key == ord('p'):
        STICKINESS.print_current_settings()
    elif key == 27:  # ESC
        return True
    
    return False


if __name__ == "__main__":
    # Demo usage
    config = StickinessConfig()
    config.print_current_settings()
    config.make_classification_more_responsive()
    config.print_current_settings()
    