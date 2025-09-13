# Bullet layout and drawing helpers
from __future__ import annotations

from typing import List, Optional, Tuple
from PIL import ImageDraw, ImageFont  # type: ignore

from .canvas import CANVAS
from .text import measure, wrap_text, try_load_font


def layout_bullets(
    d: ImageDraw.ImageDraw,
    bullets: List[str],
    font_name: Optional[str],
    max_width: int,
    max_height: int,
    start_size: int = 40,
    min_size: int = 24,
) -> Tuple[ImageFont.FreeTypeFont, List[List[str]]]:
    size = start_size
    body_font = try_load_font(font_name, size)
    wrapped: List[List[str]] = []

    while size >= min_size:
        body_font = try_load_font(font_name, size)
        wrapped = []
        total_h = 0
        for e in bullets:
            lines = wrap_text(d, e, body_font, max_width=max_width - 36)
            wrapped.append(lines)
            _, lh = measure(d, "Ag", body_font)
            total_h += max(lh, 28) * len(lines) + 12
        if total_h <= max_height:
            break
        size -= 2

    if size < min_size:
        new_wrapped: List[List[str]] = []
        total_h = 0
        for lines in wrapped:
            _, lh = measure(d, "Ag", body_font)
            block_h = max(lh, 28) * len(lines) + 12
            if total_h + block_h > max_height:
                break
            new_wrapped.append(lines)
            total_h += block_h
        wrapped = new_wrapped

    return body_font, wrapped


def draw_bullets(
    d: ImageDraw.ImageDraw,
    start_y: int,
    wrapped: List[List[str]],
    font: ImageFont.FreeTypeFont,
    fg: Tuple[int, int, int],
    content_x: int,
) -> int:
    y = start_y
    radius = 6
    for lines in wrapped:
        _, lh = measure(d, "Ag", font)
        cy = y + lh // 2
        d.ellipse((content_x, cy - radius, content_x + radius * 2, cy + radius), fill=fg)
        tx = content_x + CANVAS.bullet_indent
        for line in lines:
            d.text((tx, y), line, fill=fg, font=font)
            y += lh
        y += CANVAS.bullet_gap
    return y
