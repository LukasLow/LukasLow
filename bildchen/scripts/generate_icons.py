#!/usr/bin/env python3
"""
Generate README icons from local SVG/PNG originals.

Workflow:
1. Reads bildchen/originals/colors.csv
2. Converts SVG -> PNG with rsvg-convert (only when PNG is missing)
3. Renders a card-style icon for each entry and writes it to bildchen/icons/

Usage:
    make icons

Dependencies (installed by the Makefile in a throwaway Docker container):
    Pillow rsvg-convert
"""

import csv
import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:
    raise SystemExit("Pillow is required. Run: python -m pip install Pillow") from exc

BASE = Path(__file__).resolve().parent.parent
ORIGINALS_DIR = BASE / "originals"
OUTPUT_DIR = BASE / "icons"
SCRIPTS_DIR = BASE / "scripts"

FONT_PATH = ORIGINALS_DIR / "Righteous-Regular.ttf"

CONFIG_CSV = ORIGINALS_DIR / "colors.csv"

CARD_W, CARD_H = 500, 750
CANVAS_W, CANVAS_H = 580, 800
RADIUS = 100
BORDER = 4
SEPARATOR_Y = 480
LOGO_BOX = (400, 400)
TEXT_AREA_HEIGHT = CARD_H - SEPARATOR_Y


def ensure_dirs():
    for directory in (ORIGINALS_DIR, OUTPUT_DIR, SCRIPTS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def ensure_font():
    if not FONT_PATH.exists():
        raise SystemExit(f"Font not found: {FONT_PATH}. Please place Righteous-Regular.ttf in {ORIGINALS_DIR}")


def find_case_insensitive(directory: Path, stem: str):
    """Return the first file in directory whose stem matches stem case-insensitively."""
    for ext in (".png", ".svg"):
        for path in directory.iterdir():
            if path.is_file() and path.stem.lower() == stem.lower() and path.suffix.lower() == ext:
                return path
    return None


def svg_to_png(svg_path: Path, png_path: Path, size: int = 480):
    print(f"Converting {svg_path.name} -> {png_path.name}")
    subprocess.run(
        [
            "rsvg-convert",
            "--width", str(size),
            "--height", str(size),
            "--keep-aspect-ratio",
            "--output", str(png_path),
            str(svg_path),
        ],
        check=True,
    )


def load_config():
    rows = []
    with CONFIG_CSV.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append(row)
    return rows


def fit_font(text: str, max_width: int, max_height: int, min_size: int) -> ImageFont.FreeTypeFont:
    """Find the largest font size so text fits within max_width and max_height."""
    for size in range(min(max_width, max_height), min_size - 1, -2):
        font = ImageFont.truetype(str(FONT_PATH), size)
        bbox = font.getbbox(text)
        if bbox and (bbox[2] - bbox[0]) <= max_width and (bbox[3] - bbox[1]) <= max_height:
            return font
    return ImageFont.truetype(str(FONT_PATH), min_size)



def make_card(filename: str, text: str, bg_hex: str, logo_png: Path):
    img = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    x0 = (CANVAS_W - CARD_W) // 2
    y0 = (CANVAS_H - CARD_H) // 2
    x1, y1 = x0 + CARD_W, y0 + CARD_H

    # Card background with rounded corners and thin black border
    draw.rounded_rectangle(
        [x0, y0, x1, y1],
        radius=RADIUS,
        fill=bg_hex,
        outline="black",
        width=BORDER,
    )

    # Thin separator line
    margin = 20
    draw.line(
        [(x0 + margin, y0 + SEPARATOR_Y), (x1 - margin, y0 + SEPARATOR_Y)],
        fill="black",
        width=2,
    )

    # Logo centered in the upper area
    logo = Image.open(logo_png).convert("RGBA")
    logo.thumbnail(LOGO_BOX, getattr(Image, "Resampling", Image).LANCZOS)
    lx = x0 + (CARD_W - logo.width) // 2
    ly = y0 + (SEPARATOR_Y - logo.height) // 2
    img.paste(logo, (lx, ly), logo)

    # Label text in black Righteous font, centered in lower area
    text_margin_x = 30
    text_margin_top = 60
    text_margin_bottom = 70
    max_text_width = CARD_W - 2 * text_margin_x
    max_text_height = CARD_H - SEPARATOR_Y - text_margin_top - text_margin_bottom
    font = fit_font(text, max_text_width, max_text_height, 85)
    bbox = font.getbbox(text)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = x0 + (CARD_W - tw) // 2
    # font.getbbox returns top relative to baseline; shift up so the bbox top sits at the desired area top
    area_top = y0 + SEPARATOR_Y + text_margin_top
    area_center_y = area_top + max_text_height // 2
    baseline_y = area_center_y + th // 2 - bbox[3]
    draw.text((tx, baseline_y), text, font=font, fill="black")

    out_path = OUTPUT_DIR / f"{filename}.png"
    img.save(out_path)
    print(f"Generated {out_path}")


def main():
    ensure_dirs()
    ensure_font()

    if not CONFIG_CSV.exists():
        raise SystemExit(f"Config not found: {CONFIG_CSV}")

    for item in load_config():
        filename = item["filename"].strip()
        text = item["text"].strip()
        bg = (item.get("bg") or "#FFFFFF").strip()

        png_path = ORIGINALS_DIR / f"{filename}.png"
        svg_path = find_case_insensitive(ORIGINALS_DIR, filename)

        if not png_path.exists():
            if svg_path:
                svg_to_png(svg_path, png_path)
            else:
                print(f"Skipping {filename}: no PNG/SVG found in {ORIGINALS_DIR}")
                continue

        make_card(filename, text, bg, png_path)


if __name__ == "__main__":
    main()
