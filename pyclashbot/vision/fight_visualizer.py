"""
Single consolidated fight visualization system.
Shows debug windows during fights with unit/tower/card information and heatmaps.
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Hardcoded configuration flags
ENABLE_HEALTH_VIZ = True
ENABLE_DPS_VIZ = True
SHOW_DEBUG_WINDOWS = True


class UnitDatabase:
    """Database for unit stats from units.json"""
    
    def __init__(self, units_json_path: str = None):
        if units_json_path is None:
            units_json_path = str(Path(__file__).parent.parent / "bot" / "data" / "units.json")
        
        self.units = {}
        self.load_units_data(units_json_path)
    
    def load_units_data(self, path: str):
        """Load unit data from JSON file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for unit in data.get('units', []):
                name = unit['name'].lower()
                
                # Parse numeric values, handle special cases
                hitpoints = self._parse_numeric(unit.get('hitpoints', '0'))
                dps = self._parse_numeric(unit.get('dps', '0'))
                damage = self._parse_numeric(unit.get('damage', '0'))
                
                self.units[name] = {
                    'name': unit['name'],
                    'hitpoints': hitpoints,
                    'dps': dps,
                    'damage': damage,
                    'elixir_cost': unit.get('elixirCost', 0),
                    'type': unit.get('type', 'unknown'),
                    'range': unit.get('range', 'Unknown')
                }
                
        except Exception as e:
            print(f"Failed to load units data: {e}")
    
    def _parse_numeric(self, value_str: str) -> float:
        """Parse numeric values from strings, handling special cases"""
        if not isinstance(value_str, str):
            return float(value_str) if value_str else 0.0
            
        # Handle "N/A" cases
        if value_str.upper() in ['N/A', 'UNKNOWN', '']:
            return 0.0
            
        # Remove commas and extract first number
        value_str = value_str.replace(',', '')
        
        # Handle ranges like "35-422" - take average
        if '-' in value_str:
            try:
                parts = value_str.split('-')
                if len(parts) == 2:
                    return (float(parts[0]) + float(parts[1])) / 2
            except:
                pass
        
        # Handle multipliers like "84 (x10)" - take the multiplied value
        if '(x' in value_str:
            try:
                base = float(value_str.split('(')[0].strip())
                mult_str = value_str.split('(x')[1].split(')')[0]
                mult = float(mult_str)
                return base * mult
            except:
                pass
        
        # Handle special formats like "1,766"
        try:
            # Extract just the first number
            import re
            numbers = re.findall(r'[\d,]+\.?\d*', value_str)
            if numbers:
                return float(numbers[0].replace(',', ''))
        except:
            pass
            
        return 0.0
    
    def get_unit_stats(self, unit_name: str) -> Dict:
        """Get stats for a unit by name"""
        name_lower = unit_name.lower()
        
        # Try exact match first
        if name_lower in self.units:
            return self.units[name_lower]
        
        # Try partial matches
        for key, unit in self.units.items():
            if name_lower in key or key in name_lower:
                return unit
        
        # Return default stats if not found
        return {
            'name': unit_name,
            'hitpoints': 100,
            'dps': 50,
            'damage': 50,
            'elixir_cost': 1,
            'type': 'unknown',
            'range': 'Unknown'
        }


class FightVisualizer:
    """Main visualizer for fight debugging with multiple windows"""
    
    def __init__(self):
        self.unit_db = UnitDatabase()
        
        # Window names
        self.raw_window = "Debug: Fight Details"
        self.heatmap_window = "Debug: Health/DPS Heatmap"
        
        # Frame counter
        self.frame_id = 0
        
        # Heatmap grid settings (64x64 tiles)
        self.grid_size = 64
        self.battlefield_width = 400  # Approximate battlefield width in pixels
        self.battlefield_height = 400  # Approximate battlefield height
        self.battlefield_offset = (56, 60)  # Offset from image top-left
        
        # Font loading
        self.font = self._load_font(12)
        
        print(f"Fight visualizer ready - {len(self.unit_db.units)} units loaded")
        
    def _load_font(self, size: int):
        """Load font for text rendering"""
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()
    
    def visualize_frame(self, image_bgr: np.ndarray, vision_results: Dict) -> Tuple[np.ndarray, np.ndarray]:
        """
        Process a frame and create both visualization windows
        
        Returns:
            Tuple of (raw_details_image, heatmap_image)
        """
        self.frame_id += 1
        
        # Create visualizations
        raw_viz = self._create_raw_details_viz(image_bgr.copy(), vision_results)
        heatmap_viz = self._create_heatmap_viz(image_bgr.copy(), vision_results) if (ENABLE_HEALTH_VIZ or ENABLE_DPS_VIZ) else image_bgr.copy()
        
        return raw_viz, heatmap_viz
    
    def _create_raw_details_viz(self, image_bgr: np.ndarray, vision_results: Dict) -> np.ndarray:
        """Create raw fight details visualization (Window 1)"""
        # Convert to PIL for drawing
        im = Image.fromarray(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)).convert("RGBA")
        overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
        dr = ImageDraw.Draw(overlay, "RGBA")
        
        # Draw units with enhanced info
        units = vision_results.get('units', [])
        for unit in units:
            self._draw_unit_detailed(dr, unit)
        
        # Draw tower health
        tower_health = vision_results.get('tower_health', {})
        self._draw_tower_health(dr, tower_health)
        
        # Draw hand cards
        hand_cards = vision_results.get('hand_cards', [])
        self._draw_hand_cards(dr, hand_cards)
        
        # Draw performance stats
        self._draw_performance_stats(dr, vision_results, im.size)
        
        # Compose final image
        out = Image.alpha_composite(im, overlay).convert("RGB")
        return cv2.cvtColor(np.array(out), cv2.COLOR_RGB2BGR)
    
    def _draw_unit_detailed(self, dr: ImageDraw.Draw, unit: Dict):
        """Draw detailed unit information"""
        x1, y1, x2, y2 = unit.get('xyxy', [0, 0, 0, 0])
        unit_name = unit.get('cls_label', 'unknown')
        side = unit.get('side', 'unknown')
        
        # Get unit stats
        unit_stats = self.unit_db.get_unit_stats(unit_name)
        
        # Side-based colors
        if side == 'friendly':
            color = (40, 200, 80)  # Green
            side_prefix = "F:"
        elif side == 'enemy':
            color = (220, 60, 60)  # Red  
            side_prefix = "E:"
        else:
            color = (200, 200, 200)  # Gray
            side_prefix = ""
        
        # Draw bounding box
        dr.rounded_rectangle(
            [x1, y1, x2, y2],
            radius=4,
            outline=(*color, 200),
            width=2,
            fill=(*color, 40)  # Semi-transparent fill
        )
        
        # Prepare detailed text
        texts = [
            f"{side_prefix}{unit_name}",
            f"HP: {unit_stats['hitpoints']:.0f}",
            f"DPS: {unit_stats['dps']:.0f}",
            f"Det: {unit.get('det_score', 0):.2f}",
        ]
        
        # Draw text label
        label_text = "\n".join(texts)
        
        # Calculate text position (above unit)
        text_y = max(10, y1 - 80)  # Above the unit
        text_x = x1
        
        # Draw text background
        text_lines = label_text.split('\n')
        line_height = 15
        max_width = max(dr.textlength(line, font=self.font) for line in text_lines)
        
        bg_x1 = text_x - 2
        bg_y1 = text_y - 2
        bg_x2 = text_x + max_width + 4
        bg_y2 = text_y + len(text_lines) * line_height + 2
        
        dr.rounded_rectangle(
            [bg_x1, bg_y1, bg_x2, bg_y2],
            radius=3,
            fill=(0, 0, 0, 160),
            outline=(*color, 180),
            width=1
        )
        
        # Draw text lines
        for i, line in enumerate(text_lines):
            dr.text(
                (text_x, text_y + i * line_height),
                line,
                font=self.font,
                fill=(*color, 255),
                stroke_width=1,
                stroke_fill=(0, 0, 0, 100)
            )
    
    def _draw_tower_health(self, dr: ImageDraw.Draw, tower_health: Dict):
        """Draw tower health information"""
        # Tower display positions (approximate)
        tower_positions = {
            "enemy_left_tower": (118, 90),
            "enemy_right_tower": (301, 90), 
            "enemy_main_tower": (211, 19),
            "friendly_left_tower": (118, 392),
            "friendly_right_tower": (307, 391),
            "friendly_main_tower": (208, 479),
        }
        
        for tower_name, data in tower_health.items():
            if tower_name not in tower_positions:
                continue
                
            pos = tower_positions[tower_name]
            classification = data.get('classification', 'unknown')
            label = data.get('label', '—')
            
            # Color based on health
            if classification == "destroyed":
                color = (220, 70, 70)  # Red
            elif classification == "full":
                color = (60, 200, 80)  # Green
            else:
                # Try to extract percentage
                try:
                    if "%" in label:
                        pct = float(label.replace("%", ""))
                        if pct < 25:
                            color = (220, 70, 70)  # Red
                        elif pct < 75:
                            color = (240, 170, 60)  # Yellow
                        else:
                            color = (60, 200, 80)  # Green
                    else:
                        color = (200, 200, 200)  # Gray
                except:
                    color = (200, 200, 200)
            
            # Draw tower info
            text = f"{tower_name.replace('_', ' ').title()}\n{label.upper()}"
            text_lines = text.split('\n')
            
            # Background
            max_width = max(dr.textlength(line, font=self.font) for line in text_lines)
            line_height = 15
            
            bg_x1 = pos[0] - max_width // 2 - 4
            bg_y1 = pos[1] - 2
            bg_x2 = pos[0] + max_width // 2 + 4
            bg_y2 = pos[1] + len(text_lines) * line_height + 2
            
            dr.rounded_rectangle(
                [bg_x1, bg_y1, bg_x2, bg_y2],
                radius=4,
                fill=(0, 0, 0, 140),
                outline=(*color, 200),
                width=1
            )
            
            # Text
            for i, line in enumerate(text_lines):
                text_width = dr.textlength(line, font=self.font)
                text_x = pos[0] - text_width // 2
                text_y = pos[1] + i * line_height
                
                dr.text(
                    (text_x, text_y),
                    line,
                    font=self.font,
                    fill=(*color, 255),
                    stroke_width=1,
                    stroke_fill=(0, 0, 0, 120)
                )
    
    def _draw_hand_cards(self, dr: ImageDraw.Draw, hand_cards: List[Dict]):
        """Draw hand card information"""
        card_positions = [
            (142, 563),  # Card 0
            (210, 563),  # Card 1
            (277, 563),  # Card 2 
            (344, 563),  # Card 3
        ]
        
        for card in hand_cards:
            position = card.get('position', 0)
            if position < 0 or position >= len(card_positions):
                continue
                
            pos = card_positions[position]
            label = card.get('label', 'Unknown')
            confidence = card.get('confidence', 0.0)
            
            # Color based on confidence
            if confidence >= 0.8:
                color = (60, 200, 80)  # Green
            elif confidence >= 0.6:
                color = (240, 170, 60)  # Yellow
            else:
                color = (220, 70, 70)  # Red
            
            # Draw card info above position
            text = f"{label}\n{confidence*100:.0f}%"
            text_lines = text.split('\n')
            
            # Background
            max_width = max(dr.textlength(line, font=self.font) for line in text_lines)
            line_height = 12
            
            text_x = pos[0] - max_width // 2
            text_y = pos[1] - 50  # Above card
            
            bg_x1 = text_x - 3
            bg_y1 = text_y - 2
            bg_x2 = text_x + max_width + 3
            bg_y2 = text_y + len(text_lines) * line_height + 2
            
            dr.rounded_rectangle(
                [bg_x1, bg_y1, bg_x2, bg_y2],
                radius=3,
                fill=(0, 0, 0, 150),
                outline=(*color, 200),
                width=1
            )
            
            # Text
            for i, line in enumerate(text_lines):
                dr.text(
                    (text_x, text_y + i * line_height),
                    line,
                    font=self.font,
                    fill=(*color, 255),
                    stroke_width=1,
                    stroke_fill=(0, 0, 0, 120)
                )
    
    def _draw_performance_stats(self, dr: ImageDraw.Draw, vision_results: Dict, image_size: Tuple[int, int]):
        """Draw performance statistics"""
        stats_text = [
            f"Frame: {self.frame_id}",
            f"Units: {len(vision_results.get('units', []))}",
            f"Towers: {len(vision_results.get('tower_health', {}))}",
            f"Cards: {len(vision_results.get('hand_cards', []))}",
            f"Inference: {vision_results.get('inference_time_ms', 0):.1f}ms",
        ]
        
        # Draw in top-left corner
        x, y = 10, 10
        line_height = 14
        
        # Background
        max_width = max(dr.textlength(line, font=self.font) for line in stats_text)
        bg_height = len(stats_text) * line_height + 4
        
        dr.rounded_rectangle(
            [x-4, y-2, x + max_width + 4, y + bg_height],
            radius=5,
            fill=(0, 0, 0, 160),
            outline=(200, 200, 200, 200),
            width=1
        )
        
        # Text
        for i, line in enumerate(stats_text):
            dr.text(
                (x, y + i * line_height),
                line,
                font=self.font,
                fill=(220, 220, 220, 255),
                stroke_width=1,
                stroke_fill=(0, 0, 0, 100)
            )
    
    def _create_heatmap_viz(self, image_bgr: np.ndarray, vision_results: Dict) -> np.ndarray:
        """Create health/DPS heatmap visualization (Window 2)"""
        units = vision_results.get('units', [])
        
        # Create heatmap grids
        health_grid = np.zeros((self.grid_size, self.grid_size), dtype=np.float32)
        dps_grid = np.zeros((self.grid_size, self.grid_size), dtype=np.float32)
        
        # Fill grids with unit data
        for unit in units:
            x1, y1, x2, y2 = unit.get('xyxy', [0, 0, 0, 0])
            
            # Convert to battlefield coordinates
            center_x = (x1 + x2) // 2 - self.battlefield_offset[0]
            center_y = (y1 + y2) // 2 - self.battlefield_offset[1]
            
            # Convert to grid coordinates
            grid_x = int((center_x / self.battlefield_width) * self.grid_size)
            grid_y = int((center_y / self.battlefield_height) * self.grid_size)
            
            # Clamp to grid bounds
            grid_x = max(0, min(self.grid_size - 1, grid_x))
            grid_y = max(0, min(self.grid_size - 1, grid_y))
            
            # Get unit stats
            unit_name = unit.get('cls_label', 'unknown')
            unit_stats = self.unit_db.get_unit_stats(unit_name)
            
            # Add to grids (accumulate values in each tile)
            if ENABLE_HEALTH_VIZ:
                health_grid[grid_y, grid_x] += unit_stats['hitpoints']
            if ENABLE_DPS_VIZ:
                dps_grid[grid_y, grid_x] += unit_stats['dps']
        
        # Normalize grids
        health_grid = self._normalize_grid(health_grid)
        dps_grid = self._normalize_grid(dps_grid)
        
        # Create overlay image
        return self._render_heatmap_overlay(image_bgr, health_grid, dps_grid)
    
    def _normalize_grid(self, grid: np.ndarray) -> np.ndarray:
        """Normalize grid values to 0-1 range"""
        max_val = np.max(grid)
        if max_val > 0:
            return grid / max_val
        return grid
    
    def _render_heatmap_overlay(self, image_bgr: np.ndarray, health_grid: np.ndarray, dps_grid: np.ndarray) -> np.ndarray:
        """Render heatmap overlay on the image"""
        # Create heatmap visualization
        h, w = image_bgr.shape[:2]
        overlay = np.zeros((h, w, 4), dtype=np.uint8)  # RGBA
        
        # Calculate tile size
        battlefield_region = (
            self.battlefield_offset[0],
            self.battlefield_offset[1],
            self.battlefield_offset[0] + self.battlefield_width,
            self.battlefield_offset[1] + self.battlefield_height
        )
        
        tile_w = self.battlefield_width // self.grid_size
        tile_h = self.battlefield_height // self.grid_size
        
        # Render each tile
        for gy in range(self.grid_size):
            for gx in range(self.grid_size):
                health_val = health_grid[gy, gx] if ENABLE_HEALTH_VIZ else 0
                dps_val = dps_grid[gy, gx] if ENABLE_DPS_VIZ else 0
                
                if health_val > 0 or dps_val > 0:
                    # Calculate tile position
                    tile_x1 = battlefield_region[0] + gx * tile_w
                    tile_y1 = battlefield_region[1] + gy * tile_h
                    tile_x2 = tile_x1 + tile_w
                    tile_y2 = tile_y1 + tile_h
                    
                    # Ensure within bounds
                    tile_x1 = max(0, min(w-1, tile_x1))
                    tile_y1 = max(0, min(h-1, tile_y1))
                    tile_x2 = max(0, min(w, tile_x2))
                    tile_y2 = max(0, min(h, tile_y2))
                    
                    # Create blended color (health in green channel, dps in red channel)
                    red = int(dps_val * 255)    # DPS in red
                    green = int(health_val * 255)  # Health in green
                    blue = 0
                    alpha = int(max(health_val, dps_val) * 120)  # Semi-transparent
                    
                    # Fill tile
                    overlay[tile_y1:tile_y2, tile_x1:tile_x2] = [blue, green, red, alpha]
        
        # Convert to PIL for blending
        image_pil = Image.fromarray(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)).convert("RGBA")
        overlay_pil = Image.fromarray(overlay, "RGBA")
        
        # Blend and convert back
        result = Image.alpha_composite(image_pil, overlay_pil).convert("RGB")
        result_bgr = cv2.cvtColor(np.array(result), cv2.COLOR_RGB2BGR)
        
        # Add legend
        result_bgr = self._add_heatmap_legend(result_bgr)
        
        return result_bgr
    
    def _add_heatmap_legend(self, image_bgr: np.ndarray) -> np.ndarray:
        """Add legend to heatmap visualization"""
        # Convert to PIL for text drawing
        im = Image.fromarray(cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)).convert("RGBA")
        overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
        dr = ImageDraw.Draw(overlay, "RGBA")
        
        # Legend position (top-right)
        legend_x = im.size[0] - 200
        legend_y = 10
        
        # Legend background
        dr.rounded_rectangle(
            [legend_x - 10, legend_y - 5, legend_x + 190, legend_y + 60],
            radius=5,
            fill=(0, 0, 0, 160),
            outline=(200, 200, 200, 200),
            width=1
        )
        
        # Legend text
        legend_text = [
            "HEATMAP LEGEND:",
            "🟢 Green = Health" if ENABLE_HEALTH_VIZ else "",
            "🔴 Red = DPS" if ENABLE_DPS_VIZ else "", 
            f"Grid: {self.grid_size}x{self.grid_size}"
        ]
        legend_text = [line for line in legend_text if line]  # Remove empty lines
        
        for i, line in enumerate(legend_text):
            dr.text(
                (legend_x, legend_y + i * 14),
                line,
                font=self.font,
                fill=(220, 220, 220, 255),
                stroke_width=1,
                stroke_fill=(0, 0, 0, 100)
            )
        
        # Compose final image
        out = Image.alpha_composite(im, overlay).convert("RGB")
        return cv2.cvtColor(np.array(out), cv2.COLOR_RGB2BGR)
    
    def show_debug_windows(self, raw_viz: np.ndarray, heatmap_viz: np.ndarray):
        """Display both debug windows"""
        if SHOW_DEBUG_WINDOWS:
            cv2.imshow(self.raw_window, raw_viz)
            cv2.imshow(self.heatmap_window, heatmap_viz)
    
    def cleanup(self):
        """Clean up resources"""
        if SHOW_DEBUG_WINDOWS:
            try:
                cv2.destroyWindow(self.raw_window)
                cv2.destroyWindow(self.heatmap_window)
            except cv2.error:
                pass  # Windows may not have been created


def create_fight_visualizer() -> FightVisualizer:
    """Create a configured fight visualizer"""
    return FightVisualizer()


def test_visualizer():
    """Test the visualizer system"""
    print("Testing Fight Visualizer")
    print("=" * 40)
    
    try:
        visualizer = create_fight_visualizer()
        print("Visualizer created successfully")
        
        # Test unit database
        test_units = ['knight', 'archer', 'giant', 'wizard']
        print(f"\nTesting unit database:")
        for unit in test_units:
            stats = visualizer.unit_db.get_unit_stats(unit)
            print(f"   {unit}: HP={stats['hitpoints']:.0f}, DPS={stats['dps']:.0f}")
            
        print(f"\nConfiguration:")
        print(f"   Health viz: {'YES' if ENABLE_HEALTH_VIZ else 'NO'}")
        print(f"   DPS viz: {'YES' if ENABLE_DPS_VIZ else 'NO'}")
        print(f"   Debug windows: {'YES' if SHOW_DEBUG_WINDOWS else 'NO'}")
        
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False


if __name__ == "__main__":
    test_visualizer()