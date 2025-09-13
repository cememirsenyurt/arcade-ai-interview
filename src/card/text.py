# Text and font helpers for card rendering
from __future__ import annotations

from typing import List, Optional, Tuple
from PIL import ImageDraw, ImageFont  # type: ignore


def measure(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> Tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
    words = text.split()
    if not words:
        return [""]
    lines: List[str] = []
    cur: List[str] = []
    for w in words:
        test = (" ".join(cur + [w])).strip()
        tw, _ = measure(draw, test, font)
        if tw <= max_width or not cur:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def try_load_font(name_or_path: Optional[str], size: int) -> ImageFont.FreeTypeFont:
    candidates: List[str] = []
    if name_or_path:
        candidates.append(name_or_path)
        if not name_or_path.lower().endswith((".ttf", ".otf")):
            candidates.extend([
                f"{name_or_path}.ttf",
                f"{name_or_path}-Regular.ttf",
                f"{name_or_path}-Medium.ttf",
            ])
    candidates.extend([
        "Inter.ttf",
        "Arial.ttf",
        "Helvetica.ttf",
        "DejaVuSans.ttf",
    ])
    for fp in candidates:
        try:
            return ImageFont.truetype(fp, size)
        except Exception:
            continue
    return ImageFont.load_default()


def fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    max_lines: int,
    start_size: int,
    min_size: int,
    font_name: Optional[str],
) -> Tuple[ImageFont.FreeTypeFont, List[str]]:
    size = start_size
    while size >= min_size:
        font = try_load_font(font_name, size)
        lines = wrap_text(draw, text, font, max_width)
        if len(lines) <= max_lines and all(measure(draw, ln, font)[0] <= max_width for ln in lines):
            return font, lines
        size -= 2
    font = try_load_font(font_name, min_size)
    return font, wrap_text(draw, text, font, max_width)[:max_lines]
