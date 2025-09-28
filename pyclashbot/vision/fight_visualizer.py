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

# Import timing flags from fight.py if available, otherwise use defaults
try:
    from pyclashbot.bot.fight import TIMING_VISUALIZATION
except ImportError:
    TIMING_VISUALIZATION = False

# Hardcoded configuration flags
ENABLE_HEALTH_VIZ = True
ENABLE_DPS_VIZ = True
SHOW_DEBUG_WINDOWS = True


class UnitDatabase:
    """Database for unit stats from units.json"""
    
    def __init__(self, units_json_path: str):
        self.units_json_path = units_json_path
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
    """Main visualizer for fight debugging with single combined window"""
    
    def __init__(self):
        units_file_path = r'pyclashbot\data\units.json'
        self.unit_db = UnitDatabase(units_file_path)
        
        # Single window name
        self.main_window = "Fight Vision Debug"
        
        # Frame counter
        self.frame_id = 0
        
        # Heatmap grid settings (reduced for performance)
        self.grid_size = 32  # Reduced from 64 for better performance
        self.battlefield_width = 400  # Approximate battlefield width in pixels
        self.battlefield_height = 400  # Approximate battlefield height
        self.battlefield_offset = (56, 60)  # Offset from image top-left
        
        # Font loading
        self.font = self._load_font(10)  # Smaller font
        
        # View modes - toggleable with keyboard (single window only)
        self.view_modes = {
            'z': {'name': 'Raw Game Only', 'mode': 'raw'},
            'x': {'name': 'Heatmap Overlay', 'mode': 'heatmap_overlay'},
            'c': {'name': 'Combined Overlay', 'mode': 'combined_overlay'},
            'v': {'name': 'Units Only', 'mode': 'units_overlay'},
            'b': {'name': 'Debug Info', 'mode': 'debug_overlay'},
            'n': {'name': 'Performance Stats', 'mode': 'minimal'},
            'm': {'name': 'Debug Off', 'mode': 'off'}
        }
        
        self.current_mode = 'c'  # Default to combined overlay
        
        # Display settings for better visibility
        self.display_scale = 1.0  # Full size display
        self.target_width = 640  # Target width for performance
        
        # Performance settings
        self.max_units_to_draw = 20  # Limit unit drawings for performance
        
        print(f"Fight visualizer ready - {len(self.unit_db.units)} units loaded")
        print("Controls: Z=Raw, X=Heatmap, C=Combined, V=Units, B=Debug, N=Stats, M=Off")
        
    def _load_font(self, size: int):
        """Load font for text rendering"""
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()
    
    def visualize_frame(self, image_bgr: np.ndarray, vision_results: Dict) -> np.ndarray:
        """
        Process a frame and create optimized visualization based on current view mode
        
        Returns:
            Single visualization image optimized for performance
        """
        viz_start_time = time.perf_counter()
        
        self.frame_id += 1
        
        # Handle keyboard input
        keyboard_start = time.perf_counter()
        self._handle_keyboard_input()
        keyboard_time = (time.perf_counter() - keyboard_start) * 1000
        
        # Get current view mode
        mode_config = self.view_modes.get(self.current_mode, self.view_modes['c'])
        mode = mode_config['mode']
        
        # Downscale first for performance (if needed)
        prep_start = time.perf_counter()
        base_image = self._prepare_base_image(image_bgr)
        prep_time = (time.perf_counter() - prep_start) * 1000
        
        # Create visualization based on mode
        viz_mode_start = time.perf_counter()
        if mode == 'off':
            result = base_image
        elif mode == 'raw':
            result = base_image
        elif mode == 'minimal':
            result = self._create_minimal_overlay(base_image, vision_results)
        elif mode == 'heatmap_overlay':
            result = self._create_heatmap_overlay(base_image, vision_results)
        elif mode == 'units_overlay':
            result = self._create_units_overlay(base_image, vision_results)
        elif mode == 'debug_overlay':
            result = self._create_debug_overlay(base_image, vision_results)
        elif mode == 'combined_overlay':
            result = self._create_combined_overlay(base_image, vision_results)
        else:
            result = base_image
        viz_mode_time = (time.perf_counter() - viz_mode_start) * 1000
        
        # Add mode indicator
        indicator_start = time.perf_counter()
        result = self._add_mode_indicator_cv2(result, mode_config)
        indicator_time = (time.perf_counter() - indicator_start) * 1000
        
        total_viz_time = (time.perf_counter() - viz_start_time) * 1000
        
        # Print timing information if enabled
        if TIMING_VISUALIZATION:
            print(f"  Visualization Timing:")
            print(f"    Keyboard Input: {keyboard_time:.1f}ms")
            print(f"    Image Preparation: {prep_time:.1f}ms")  
            print(f"    Mode '{mode}' Rendering: {viz_mode_time:.1f}ms")
            print(f"    Mode Indicator: {indicator_time:.1f}ms")
            print(f"    Total Visualization: {total_viz_time:.1f}ms")
        
        return result
    
    def _prepare_base_image(self, image_bgr: np.ndarray) -> np.ndarray:
        """Prepare base image with optimal scaling for performance"""
        h, w = image_bgr.shape[:2]
        
        # Scale down if image is too large for performance
        if w > self.target_width:
            scale = self.target_width / w
            new_h = int(h * scale)
            new_w = self.target_width
            image_bgr = cv2.resize(image_bgr, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # Ensure contiguous array for performance
        return np.ascontiguousarray(image_bgr, dtype=np.uint8)
    
    def _create_minimal_overlay(self, image: np.ndarray, vision_results: Dict) -> np.ndarray:
        """Create minimal overlay with basic stats using cv2"""
        result = image.copy()
        
        # Basic stats
        units_count = len(vision_results.get('units', []))
        text = f"Frame {self.frame_id} | Units: {units_count}"
        
        # Draw background rectangle for text
        (text_w, text_h), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        cv2.rectangle(result, (5, 5), (15 + text_w, 25 + text_h), (0, 0, 0), -1)
        cv2.rectangle(result, (5, 5), (15 + text_w, 25 + text_h), (100, 100, 100), 1)
        
        # Draw text
        cv2.putText(result, text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_8)
        
        return result
    
    def _create_units_overlay(self, image: np.ndarray, vision_results: Dict) -> np.ndarray:
        """Create overlay with unit bounding boxes using cv2"""
        result = image.copy()
        overlay = np.zeros_like(result, dtype=np.uint8)
        
        units = vision_results.get('units', [])[:self.max_units_to_draw]  # Limit for performance
        
        for unit in units:
            x1, y1, x2, y2 = unit.get('xyxy', [0, 0, 0, 0])
            unit_name = unit.get('cls_label', 'unknown')
            side = unit.get('side', 'unknown')
            
            # Scale coordinates if image was downscaled
            scale = image.shape[1] / 512  # Assume original is around 512px wide
            x1, y1, x2, y2 = int(x1*scale), int(y1*scale), int(x2*scale), int(y2*scale)
            
            # Color based on side
            if side == 'friendly':
                color = (80, 200, 40)  # Green (BGR)
            elif side == 'enemy':
                color = (60, 60, 220)  # Red (BGR)
            else:
                color = (200, 200, 200)  # Gray (BGR)
            
            # Draw bounding box
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 2)
            
            # Draw unit name
            text = f"{side[0].upper()}:{unit_name[:6]}"
            cv2.putText(overlay, text, (x1, max(15, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_8)
        
        # Blend overlay with original image
        result = cv2.addWeighted(result, 0.7, overlay, 0.3, 0)
        return result
    
    def _create_heatmap_overlay(self, image: np.ndarray, vision_results: Dict) -> np.ndarray:
        """Create heatmap overlay using cv2"""
        result = image.copy()
        h, w = result.shape[:2]
        
        # Create heatmap overlay
        heatmap_overlay = np.zeros((h, w, 3), dtype=np.uint8)
        
        # Simplified heatmap grid (smaller for performance)
        grid_size = 16  # Much smaller grid
        tile_w = w // grid_size
        tile_h = h // grid_size
        
        # Build simplified heatmap
        units = vision_results.get('units', [])
        for unit in units:
            x1, y1, x2, y2 = unit.get('xyxy', [0, 0, 0, 0])
            
            # Scale coordinates
            scale = w / 512
            center_x = int(((x1 + x2) / 2) * scale)
            center_y = int(((y1 + y2) / 2) * scale)
            
            # Convert to grid coordinates
            grid_x = min(grid_size - 1, max(0, center_x // tile_w))
            grid_y = min(grid_size - 1, max(0, center_y // tile_h))
            
            # Draw heatmap tile
            tile_x1 = grid_x * tile_w
            tile_y1 = grid_y * tile_h
            tile_x2 = tile_x1 + tile_w
            tile_y2 = tile_y1 + tile_h
            
            # Color based on unit type (simplified)
            unit_name = unit.get('cls_label', '').lower()
            if 'tower' in unit_name:
                color = (0, 100, 255)  # Orange for towers
            else:
                color = (255, 100, 0)  # Blue for units
                
            cv2.rectangle(heatmap_overlay, (tile_x1, tile_y1), (tile_x2, tile_y2), color, -1)
        
        # Blend heatmap with original image
        result = cv2.addWeighted(result, 0.6, heatmap_overlay, 0.4, 0)
        
        # Add legend
        cv2.rectangle(result, (w-120, 10), (w-10, 60), (0, 0, 0), -1)
        cv2.putText(result, "Heatmap", (w-115, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
        cv2.putText(result, "Blue=Units", (w-115, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 100, 0), 1)
        cv2.putText(result, "Orange=Towers", (w-115, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 100, 255), 1)
        
        return result
    
    def _create_debug_overlay(self, image: np.ndarray, vision_results: Dict) -> np.ndarray:
        """Create debug overlay with detailed information using cv2"""
        result = self._create_units_overlay(image, vision_results)
        
        # Add performance stats
        stats = [
            f"Frame: {self.frame_id}",
            f"Units: {len(vision_results.get('units', []))}",
            f"Towers: {len(vision_results.get('tower_health', {}))}",
            f"Cards: {len(vision_results.get('hand_cards', []))}",
            f"Time: {vision_results.get('inference_time_ms', 0):.1f}ms"
        ]
        
        # Draw stats background
        max_width = max(cv2.getTextSize(s, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0][0] for s in stats)
        cv2.rectangle(result, (10, 10), (20 + max_width, 20 + len(stats) * 15), (0, 0, 0), -1)
        cv2.rectangle(result, (10, 10), (20 + max_width, 20 + len(stats) * 15), (100, 100, 100), 1)
        
        # Draw stats text
        for i, stat in enumerate(stats):
            cv2.putText(result, stat, (15, 25 + i * 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (220, 220, 220), 1, cv2.LINE_8)
        
        return result
    
    def _create_combined_overlay(self, image: np.ndarray, vision_results: Dict) -> np.ndarray:
        """Create combined overlay with units and simplified heatmap using cv2"""
        # Start with heatmap
        result = self._create_heatmap_overlay(image, vision_results)
        
        # Add unit overlays on top
        overlay = np.zeros_like(result, dtype=np.uint8)
        
        units = vision_results.get('units', [])[:self.max_units_to_draw]
        
        for unit in units:
            x1, y1, x2, y2 = unit.get('xyxy', [0, 0, 0, 0])
            unit_name = unit.get('cls_label', 'unknown')
            side = unit.get('side', 'unknown')
            
            # Scale coordinates
            scale = image.shape[1] / 512
            x1, y1, x2, y2 = int(x1*scale), int(y1*scale), int(x2*scale), int(y2*scale)
            
            # Color based on side
            if side == 'friendly':
                color = (80, 255, 40)  # Bright green
            elif side == 'enemy':
                color = (40, 40, 255)  # Bright red
            else:
                color = (255, 255, 255)  # White
            
            # Draw thin bounding box
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, 1)
            
            # Draw abbreviated unit name
            text = unit_name[:3].upper()
            cv2.putText(overlay, text, (x1, max(12, y1 - 2)), cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1, cv2.LINE_8)
        
        # Blend unit overlay
        result = cv2.addWeighted(result, 0.8, overlay, 0.2, 0)
        
        return result
    
    def _add_mode_indicator_cv2(self, image: np.ndarray, mode_config: Dict) -> np.ndarray:
        """Add mode indicator using cv2"""
        result = image.copy()
        h, w = result.shape[:2]
        
        # Mode text at bottom
        mode_text = f"Mode: {mode_config['name']} (Z/X/C/V/B/N/M)"
        
        # Get text size
        (text_w, text_h), baseline = cv2.getTextSize(mode_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
        
        # Draw background
        y_pos = h - 25
        cv2.rectangle(result, (5, y_pos - 5), (15 + text_w, y_pos + text_h + 5), (0, 0, 0), -1)
        cv2.rectangle(result, (5, y_pos - 5), (15 + text_w, y_pos + text_h + 5), (100, 100, 100), 1)
        
        # Draw text
        cv2.putText(result, mode_text, (10, y_pos + text_h), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (220, 220, 220), 1, cv2.LINE_8)
        
        return result
    
    def _handle_keyboard_input(self):
        """Handle keyboard input for view switching"""
        key = cv2.waitKey(1) & 0xFF
        key_char = chr(key) if key < 128 else None
        
        if key_char and key_char.lower() in self.view_modes:
            old_mode = self.current_mode
            self.current_mode = key_char.lower()
            if old_mode != self.current_mode:
                print(f"Switched to view mode: {self.view_modes[self.current_mode]['name']}")
    
    
    def show_debug_window(self, combined_viz: np.ndarray):
        """Display single combined debug window with optimization"""
        if SHOW_DEBUG_WINDOWS:
            display_start = time.perf_counter()
            
            # Try to use OpenGL for better performance
            window_start = time.perf_counter()
            try:
                cv2.namedWindow(self.main_window, cv2.WINDOW_OPENGL | cv2.WINDOW_AUTOSIZE)
            except:
                cv2.namedWindow(self.main_window, cv2.WINDOW_AUTOSIZE)
            window_time = (time.perf_counter() - window_start) * 1000
            
            show_start = time.perf_counter()
            cv2.imshow(self.main_window, combined_viz)
            show_time = (time.perf_counter() - show_start) * 1000
            
            total_display_time = (time.perf_counter() - display_start) * 1000
            
            if TIMING_VISUALIZATION:
                print(f"  Display Window Timing:")
                print(f"    Window Setup: {window_time:.1f}ms")
                print(f"    Image Display: {show_time:.1f}ms")
                print(f"    Total Display: {total_display_time:.1f}ms")
    
    def cleanup(self):
        """Clean up resources"""
        if SHOW_DEBUG_WINDOWS:
            try:
                cv2.destroyWindow(self.main_window)
            except cv2.error:
                pass  # Window may not have been created


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