#!/usr/bin/env python3
"""Overlay PLAY_COORDS tap points on a real 419x633 in-game battle screenshot.

Usage:
  # 1) Save a mid-battle emulator screenshot (must be 419x633):
  #    docs/reference/battle-screenshot.png
  # 2) Generate overlay:
  uv run python scripts/generate_placement_map.py
  uv run python scripts/generate_placement_map.py --background path/to.png

Outputs:
  docs/placement-zones-overlay.png  (screenshot + dots + legend)
  docs/placement-zones-map.png      (schematic fallback if no screenshot)
"""

from __future__ import annotations

import argparse
import ast
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
CARD_DETECTION = ROOT / "pyclashbot" / "bot" / "card_detection.py"
DEFAULT_BACKGROUND = ROOT / "docs" / "reference" / "battle-screenshot.png"
OUT_OVERLAY = ROOT / "docs" / "placement-zones-overlay.png"
OUT_SCHEMATIC = ROOT / "docs" / "placement-zones-map.png"

WIDTH, HEIGHT = 419, 633

PROFILE_COLORS: dict[str, tuple[int, int, int]] = {
    "bridge_line": (220, 60, 60),
    "bridge_rush": (255, 140, 0),
    "back_support": (46, 200, 80),
    "king_lane": (66, 133, 244),
    "princess": (186, 80, 220),
    "defense_building": (180, 130, 70),
    "siege_building": (0, 180, 170),
    "center_spell": (255, 220, 0),
    "lane_spell": (0, 220, 235),
    "reactive_spell": (0, 160, 255),
    "spirit": (255, 64, 160),
    "tornado": (180, 60, 220),
    "rocket": (200, 40, 40),
    "goblin_barrel": (160, 220, 60),
    "graveyard": (200, 200, 200),
    "miner": (80, 120, 255),
    "goblin_drill": (170, 150, 40),
}

# Shape per profile so stacked coords (e.g. center_spell vs lane_spell) stay readable.
PROFILE_SHAPES: dict[str, str] = {
    "bridge_line": "circle",
    "bridge_rush": "triangle",
    "back_support": "square",
    "king_lane": "diamond",
    "princess": "star",
    "defense_building": "pentagon",
    "siege_building": "hex",
    "center_spell": "star",
    "lane_spell": "circle",
    "reactive_spell": "cross",
    "spirit": "square",
    "tornado": "wide_bar",
    "rocket": "triangle",
    "goblin_barrel": "square",
    "graveyard": "diamond",
    "miner": "pentagon",
    "goblin_drill": "hex",
}


def draw_marker(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    shape: str,
    color: tuple[int, int, int],
    size: int,
) -> None:
    fill = (*color, 220)
    outline = (0, 0, 0, 255)
    s = size
    if shape == "circle":
        draw.ellipse((x - s, y - s, x + s, y + s), fill=fill, outline=outline, width=2)
    elif shape == "square":
        draw.rectangle((x - s, y - s, x + s, y + s), fill=fill, outline=outline, width=2)
    elif shape == "triangle":
        draw.polygon([(x, y - s), (x - s, y + s), (x + s, y + s)], fill=fill, outline=outline)
    elif shape == "diamond":
        draw.polygon([(x, y - s), (x + s, y), (x, y + s), (x - s, y)], fill=fill, outline=outline)
    elif shape == "cross":
        draw.line((x - s, y, x + s, y), fill=outline, width=3)
        draw.line((x, y - s, x, y + s), fill=outline, width=3)
        draw.ellipse((x - s // 2, y - s // 2, x + s // 2, y + s // 2), fill=fill)
    elif shape == "star":
        pts = []
        for i in range(10):
            angle = (i * 36 - 90) * 3.14159 / 180
            rad = s if i % 2 == 0 else s // 2
            pts.append((x + rad * math.cos(angle), y + rad * math.sin(angle)))
        draw.polygon(pts, fill=fill, outline=outline)
    elif shape == "pentagon":
        pts = []
        for i in range(5):
            angle = (i * 72 - 90) * math.pi / 180
            pts.append((x + s * math.cos(angle), y + s * math.sin(angle)))
        draw.polygon(pts, fill=fill, outline=outline)
    elif shape == "hex":
        pts = []
        for i in range(6):
            angle = (i * 60 - 90) * math.pi / 180
            pts.append((x + s * math.cos(angle), y + s * math.sin(angle)))
        draw.polygon(pts, fill=fill, outline=outline)
    elif shape == "wide_bar":
        draw.rectangle((x - s * 2, y - s // 2, x + s * 2, y + s // 2), fill=fill, outline=outline, width=2)
    else:
        draw.ellipse((x - s, y - s, x + s, y + s), fill=fill, outline=outline, width=2)


def load_play_coords() -> dict:
    text = CARD_DETECTION.read_text(encoding="utf-8")
    tree = ast.parse(text)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "PLAY_COORDS":
                    return ast.literal_eval(node.value)
    raise RuntimeError("PLAY_COORDS not found")


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for name in (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ):
        path = Path(name)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def load_background(path: Path) -> Image.Image:
    if not path.exists():
        raise FileNotFoundError(path)
    img = Image.open(path).convert("RGBA")
    if img.size != (WIDTH, HEIGHT):
        # Scale to emulator space so (x,y) from code line up.
        img = img.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
    return img


def draw_points(
    base: Image.Image,
    play_coords: dict,
    *,
    show_labels: bool,
    dot_radius: int = 7,
) -> Image.Image:
    canvas = base.copy()
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = load_font(9)

    overlap: dict[tuple[int, int, str], int] = {}
    for profile, sides in play_coords.items():
        color = PROFILE_COLORS.get(profile, (255, 255, 255))
        shape = PROFILE_SHAPES.get(profile, "circle")
        for side in ("left", "right"):
            for x, y in sides.get(side, []):
                key = (x, y, profile)
                n = overlap.get(key, 0)
                overlap[key] = n + 1
                jitter_x = (6 if side == "left" else -6) * n
                jitter_y = (4 * (hash(profile) % 3)) - 4
                px, py = x + jitter_x, y + jitter_y
                draw_marker(draw, px, py, shape, color, dot_radius)
                if show_labels and n == 0 and side == "left":
                    abbr = profile[:4]
                    draw.text(
                        (px + dot_radius + 2, py - 6),
                        abbr,
                        fill=(255, 255, 255, 255),
                        font=font,
                        stroke_width=1,
                        stroke_fill=(0, 0, 0, 255),
                    )

    return Image.alpha_composite(canvas, overlay)


def build_legend(height: int, play_coords: dict, scale: int = 1) -> Image.Image:
    profiles = list(play_coords.keys())
    rows = (len(profiles) + 1) // 2
    legend_h = 36 + rows * 18
    legend = Image.new("RGBA", (WIDTH * scale, legend_h * scale), (24, 24, 24, 255))
    draw = ImageDraw.Draw(legend)
    font = load_font(11 * scale)
    font_sm = load_font(9 * scale)
    draw.text(
        (10 * scale, 6 * scale),
        "Legend: shape + color = profile (see center_spell = yellow star)",
        fill=(230, 230, 230),
        font=font,
    )
    y0 = 26 * scale
    col_w = WIDTH * scale // 2
    for i, profile in enumerate(profiles):
        col, row = i % 2, i // 2
        lx = (8 + col * col_w // scale) * scale
        ly = y0 + row * 18 * scale
        c = PROFILE_COLORS.get(profile, (200, 200, 200))
        shape = PROFILE_SHAPES.get(profile, "circle")
        draw_marker(draw, lx + 6 * scale, ly + 6 * scale, shape, c, 5 * scale)
        n_l = len(play_coords[profile].get("left", []))
        n_r = len(play_coords[profile].get("right", []))
        draw.text((lx + 16 * scale, ly), f"{profile} (L{n_l}/R{n_r})", fill=(220, 220, 220), font=font_sm)
    return legend


def render_schematic(play_coords: dict, out: Path) -> None:
    """Simple green arena fallback when no battle screenshot is available."""
    img = Image.new("RGB", (WIDTH, HEIGHT), (40, 100, 50))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 248, WIDTH, 368), fill=(50, 110, 160))
    for x0, x1 in ((55, 165), (254, 364)):
        draw.rectangle((x0, 268, x1, 348), fill=(150, 120, 80))
    base_rgba = img.convert("RGBA")
    composed = draw_points(base_rgba, play_coords, show_labels=False)
    legend = build_legend(200, play_coords)
    legend_rgb = legend.convert("RGB")
    out_img = Image.new("RGB", (WIDTH, HEIGHT + legend_rgb.height), (30, 30, 30))
    out_img.paste(composed.convert("RGB"), (0, 0))
    out_img.paste(legend_rgb, (0, HEIGHT))
    out.parent.mkdir(parents=True, exist_ok=True)
    out_img.save(out)
    print(f"Wrote schematic fallback: {out}")


def render_overlay(background: Path, play_coords: dict, out: Path, show_labels: bool) -> None:
    base = load_background(background)
    composed = draw_points(base, play_coords, show_labels=show_labels)
    legend = build_legend(220, play_coords)
    legend_rgb = legend.convert("RGB")
    total_h = HEIGHT + legend_rgb.height
    out_img = Image.new("RGB", (WIDTH, total_h), (20, 20, 20))
    out_img.paste(composed.convert("RGB"), (0, 0))
    draw = ImageDraw.Draw(out_img)
    # Emulator coords: y grows downward; player hand / your towers are at the bottom.
    draw.text((8, 8), "ENEMY SIDE (top)", fill=(255, 255, 0), font=load_font(11), stroke_width=1, stroke_fill=(0, 0, 0))
    draw.text(
        (8, HEIGHT - 22),
        "YOUR SIDE (bottom)",
        fill=(255, 255, 0),
        font=load_font(11),
        stroke_width=1,
        stroke_fill=(0, 0, 0),
    )
    out_img.paste(legend_rgb, (0, HEIGHT))
    out.parent.mkdir(parents=True, exist_ok=True)
    out_img.save(out, quality=95)
    print(f"Wrote overlay: {out} (background: {background})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--background",
        type=Path,
        default=DEFAULT_BACKGROUND,
        help=f"Battle screenshot at {WIDTH}x{HEIGHT} (default: {DEFAULT_BACKGROUND})",
    )
    parser.add_argument("--labels", action="store_true", help="Short profile labels on left-side points")
    parser.add_argument("--schematic-only", action="store_true", help="Only write schematic fallback")
    args = parser.parse_args()

    play_coords = load_play_coords()

    if args.schematic_only:
        render_schematic(play_coords, OUT_SCHEMATIC)
        return

    try:
        render_overlay(args.background, play_coords, OUT_OVERLAY, show_labels=args.labels)
    except FileNotFoundError:
        print(f"No screenshot at {args.background}")
        print("Save a mid-battle 419x633 PNG there, or pass --background /path/to.png")
        print("See docs/reference/README.md for capture steps.")
        render_schematic(play_coords, OUT_SCHEMATIC)
        return

    # Also refresh schematic for comparison
    render_schematic(play_coords, OUT_SCHEMATIC)


if __name__ == "__main__":
    main()
