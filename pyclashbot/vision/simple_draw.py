"""
Simple drawing functions for fight vision - inspired by clash-royale-fight-vision-demo.
Lightweight, efficient visualization without the complexity of the full FightVisualizer.
"""
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import hashlib
import colorsys
from typing import Dict, List, Any, Optional


def _hash_color(key: str):
    """Generate stable bright color from a string (label)."""
    h = int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16) % 360
    r, g, b = colorsys.hsv_to_rgb(h / 360.0, 0.90, 1.0)
    return int(r * 255), int(g * 255), int(b * 255)


def _load_font(pref_size: int):
    """Try to load a clean font, fallback to default."""
    candidates = [
        "DejaVuSans.ttf",
        "DejaVuSansCondensed.ttf", 
        "Roboto-Regular.ttf",
        "arial.ttf",
    ]
    for name in candidates:
        try:
            return ImageFont.truetype(name, pref_size)
        except Exception:
            continue
    return ImageFont.load_default()


def draw_waiting(img_bgr, text="Waiting for fight vision...", box_alpha=0.65):
    """
    Return a copy of img_bgr with a centered message in a rounded, semi-transparent box.
    """
    im = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)).convert("RGBA")
    W, H = im.size
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(overlay, "RGBA")

    # Font & sizing
    font_size = max(18, round(min(W, H) / 18))
    font = _load_font(font_size)
    pad = max(8, font_size // 3)

    # Text bbox (centered)
    tb = dr.textbbox((0, 0), text, font=font, stroke_width=2)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]
    bx1 = (W - (tw + 2 * pad)) // 2
    by1 = (H - (th + 2 * pad)) // 2
    bx2 = bx1 + tw + 2 * pad
    by2 = by1 + th + 2 * pad

    # Background box
    dr.rounded_rectangle(
        [bx1, by1, bx2, by2],
        radius=pad,
        fill=(0, 0, 0, int(255 * box_alpha)),
        outline=(255, 255, 255, 220),
        width=2,
    )
    # Text
    dr.text(
        (bx1 + pad, by1 + pad),
        text,
        font=font,
        fill=(255, 255, 255, 255),
        stroke_width=2,
        stroke_fill=(0, 0, 0, 160),
    )

    out = Image.alpha_composite(im, overlay).convert("RGB")
    return cv2.cvtColor(np.array(out), cv2.COLOR_RGB2BGR)


def draw_fight_results(img_bgr, vision_results, stats: Optional[Dict] = None):
    """
    Draw fight vision results on image with lightweight approach.
    
    Args:
        img_bgr: Input image (BGR format)
        vision_results: Results from tracking engine (InferenceResult object or dict)
        stats: Optional statistics dictionary (fps, timing, etc.)
    
    Returns:
        Annotated image in BGR format
    """
    # Convert to PIL for drawing
    im = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)).convert("RGBA")
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    dr = ImageDraw.Draw(overlay, "RGBA")
    
    W, H = im.size
    
    # Font sizes
    unit_font = _load_font(10)
    stats_font = _load_font(12)
    
    # Handle both InferenceResult objects and dictionaries
    if hasattr(vision_results, 'units'):
        # InferenceResult object
        units = getattr(vision_results, 'units', [])
        hand_cards = getattr(vision_results, 'hand_cards', [])
        tower_health = getattr(vision_results, 'tower_health', {})
    else:
        # Dictionary format
        units = vision_results.get("units", [])
        hand_cards = vision_results.get("hand_cards", [])
        tower_health = vision_results.get("tower_health", {})
    
    # Draw units
    for unit in units:
        x1, y1, x2, y2 = unit.get("xyxy", [0, 0, 0, 0])
        label = unit.get("cls_label", "unknown")
        side = unit.get("side", "unknown")
        confidence = unit.get("det_score", 0.0)
        track_id = unit.get("track_id", "")[:6]  # Short track ID
        
        # Color based on side
        if side == "friendly":
            color = (40, 200, 40, 200)  # Green
        elif side == "enemy":
            color = (200, 40, 40, 200)  # Red
        else:
            color = (200, 200, 40, 200)  # Yellow for unknown
        
        # Draw bounding box
        dr.rectangle([x1, y1, x2, y2], outline=color, width=2)
        
        # Draw label with background
        text = f"{side[0].upper()}:{label[:8]}"
        tb = dr.textbbox((0, 0), text, font=unit_font)
        tw, th = tb[2] - tb[0], tb[3] - tb[1]
        
        # Position label above box
        label_x = x1
        label_y = max(5, y1 - th - 4)
        
        # Background for text
        dr.rectangle(
            [label_x - 2, label_y - 2, label_x + tw + 2, label_y + th + 2],
            fill=(0, 0, 0, 180)
        )
        
        # Text
        dr.text((label_x, label_y), text, font=unit_font, fill=(255, 255, 255, 255))
        
        # Track ID if available
        if track_id:
            track_text = f"[{track_id}]"
            dr.text((x1, y2 + 2), track_text, font=unit_font, fill=color)
    
    # Draw hand cards
    if hand_cards:
        card_y_start = H - 80
        for i, card in enumerate(hand_cards):
            label = card.get("label", "unknown")
            confidence = card.get("confidence", 0.0)
            
            # Card position
            card_x = 10 + i * 100
            card_text = f"{i}: {label[:10]}"
            conf_text = f"{confidence*100:.0f}%"
            
            # Background
            dr.rectangle([card_x - 2, card_y_start - 2, card_x + 90, card_y_start + 30],
                        fill=(0, 0, 0, 150), outline=(100, 100, 100, 200))
            
            # Text
            dr.text((card_x, card_y_start), card_text, font=unit_font, fill=(255, 255, 255, 255))
            dr.text((card_x, card_y_start + 12), conf_text, font=unit_font, fill=(200, 200, 200, 255))
    
    # Draw statistics overlay
    if stats:
        stats_lines = []
        
        # Performance stats
        fps = stats.get('fps', 0)
        inference_time = stats.get('inference_time', 0)
        tracking_time = stats.get('tracking_time', 0)
        total_time = inference_time + tracking_time
        
        stats_lines.append(f"FPS: {fps:.1f}")
        stats_lines.append(f"Inference: {inference_time:.1f}ms")
        stats_lines.append(f"Tracking: {tracking_time:.1f}ms")
        stats_lines.append(f"Total: {total_time:.1f}ms")
        
        # Unit counts
        friendly_count = stats.get('friendly_count', 0)
        enemy_count = stats.get('enemy_count', 0)
        stats_lines.append(f"Units: F:{friendly_count} E:{enemy_count}")
        
        # Device info
        device = stats.get('inference_device', 'Unknown')
        stats_lines.append(f"Device: {device}")
        
        # Draw stats box
        line_height = 14
        box_height = len(stats_lines) * line_height + 10
        box_width = 160
        
        # Position in top-right
        box_x = W - box_width - 10
        box_y = 10
        
        # Background
        dr.rectangle([box_x, box_y, box_x + box_width, box_y + box_height],
                    fill=(0, 0, 0, 180), outline=(100, 100, 100, 200), width=1)
        
        # Stats text
        for i, line in enumerate(stats_lines):
            y = box_y + 5 + i * line_height
            dr.text((box_x + 5, y), line, font=stats_font, fill=(255, 255, 255, 255))
    
    # Draw tower health indicators (simple)
    tower_positions = [
        ("enemy_left_tower", 80, 30),
        ("enemy_main_tower", W//2, 20), 
        ("enemy_right_tower", W-80, 30),
        ("friendly_left_tower", 80, H-30),
        ("friendly_main_tower", W//2, H-20),
        ("friendly_right_tower", W-80, H-30),
    ]
    
    for tower_name, tx, ty in tower_positions:
        if tower_name in tower_health:
            tower_data = tower_health[tower_name]
            label = tower_data.get("label", "unknown")
            
            # Color based on health
            if label == "destroyed":
                color = (100, 100, 100, 200)  # Gray
            elif label == "full":
                color = (40, 200, 40, 200)    # Green
            else:
                color = (200, 200, 40, 200)   # Yellow for partial
            
            # Simple indicator
            dr.ellipse([tx-6, ty-6, tx+6, ty+6], fill=color, outline=(255,255,255,100))
    
    # Composite and return
    result = Image.alpha_composite(im, overlay).convert("RGB")
    return cv2.cvtColor(np.array(result), cv2.COLOR_RGB2BGR)


def get_fight_stats(vision_results, fps: float = 0, inference_time: float = 0, 
                   tracking_time: float = 0, device: str = "Unknown") -> Dict:
    """
    Generate statistics dictionary for overlay display.
    
    Args:
        vision_results: Results from tracking engine (InferenceResult object or dict)
        fps: Current FPS
        inference_time: Inference timing in ms
        tracking_time: Tracking timing in ms
        device: Inference device name
    
    Returns:
        Stats dictionary for draw_fight_results
    """
    # Handle both InferenceResult objects and dictionaries
    if hasattr(vision_results, 'units'):
        # InferenceResult object
        units = getattr(vision_results, 'units', [])
        tower_health = getattr(vision_results, 'tower_health', {})
        hand_cards = getattr(vision_results, 'hand_cards', [])
    else:
        # Dictionary format
        units = vision_results.get("units", [])
        tower_health = vision_results.get("tower_health", {})
        hand_cards = vision_results.get("hand_cards", [])
    
    friendly_count = sum(1 for u in units if u.get("side") == "friendly")
    enemy_count = sum(1 for u in units if u.get("side") == "enemy")
    
    return {
        'fps': fps,
        'inference_time': inference_time,
        'tracking_time': tracking_time,
        'friendly_count': friendly_count,
        'enemy_count': enemy_count,
        'tower_count': len(tower_health),
        'hand_card_count': len(hand_cards),
        'inference_device': device,
    }