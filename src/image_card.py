# Thin wrapper around card helpers to render a share image
from __future__ import annotations

from typing import Any, Dict, Optional, List
import json

from PIL import Image, ImageDraw  # type: ignore

from src.card.canvas import CANVAS
from src.card.text import fit_text, measure
from src.card.bullets import layout_bullets, draw_bullets
from src.card.color import contrast, rel_luminance, is_neutral_rgb
from src.card.style import derive_style_from_flow
from src.card.types import Style

__all__ = ["compose", "derive_style_from_flow"]


def _as_brief_dict(brief: Any) -> Dict[str, Any]:
    if isinstance(brief, str):
        try:
            return json.loads(brief)
        except Exception:
            return {"overlay": "Arcade Flow", "elements": ["Step 1", "Step 2"]}
    return brief


def _style_from_dict(style: Optional[Dict[str, Any]], flow: Optional[Dict[str, Any]]) -> Style:
    st = style or derive_style_from_flow(flow)
    return Style(
        primary=tuple(st.get("primary", (33, 66, 231))),
        bg=tuple(st.get("bg", (24, 24, 36))),
        fg=tuple(st.get("fg", (255, 255, 255))),
        font=st.get("font"),
        align=st.get("align", "center"),
    )


def compose(brief: Any, path: Any, flow: Optional[Dict[str, Any]] = None, style: Optional[Dict[str, Any]] = None) -> None:
    # Normalize input and resolve style
    b = _as_brief_dict(brief)
    st = _style_from_dict(style, flow)

    W, H = CANVAS.width, CANVAS.height
    bg, fg, primary = st.bg, st.fg, st.primary

    # Promote strong primary as bg when contrast allows
    white, black = (255, 255, 255), (0, 0, 0)
    if is_neutral_rgb(bg) and not is_neutral_rgb(primary):
        cw = contrast(primary, white)
        cb = contrast(primary, black)
        if max(cw, cb) >= 4.5:
            bg = primary
            fg = white if cw >= cb else black

    # Ensure readable contrast on dark backgrounds
    if rel_luminance(bg) < 0.2:
        fg = (255, 255, 255)

    # Canvas
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)

    # Layout
    pad_x, pad_top = CANVAS.pad_x, CANVAS.pad_top
    content_width = W - pad_x * 2
    align = (st.align or "left").lower()

    # Title
    overlay = str(b.get("overlay", "Arcade Flow")).strip()
    title_font, title_lines = fit_text(d, overlay, content_width, 2, 80, 40, st.font)

    def aligned_x(tw: int) -> float:
        if align == "left":
            return float(pad_x)
        if align == "right":
            return float(W - pad_x - tw)
        return float((W - tw) / 2)

    y = pad_top
    for line in title_lines:
        tw, th = measure(d, line, title_font)
        d.text((aligned_x(tw), y), line, fill=fg, font=title_font)
        y += th + 8

    y += CANVAS.pad_between

    # Bullets
    bullets = [str(e).strip() for e in (b.get("elements") or []) if str(e).strip()][:5]
    if not bullets:
        bullets = ["Step 1", "Step 2", "Step 3"]

    body_max_height = H - y - pad_top
    body_font, wrapped = layout_bullets(d, bullets, st.font, content_width, body_max_height, 40, 24)

    draw_bullets(d, y, wrapped, body_font, fg, content_x=pad_x)

    # Save
    img.save(path.__fspath__() if hasattr(path, "__fspath__") else path, "PNG")