# Color and contrast utilities for card rendering
from __future__ import annotations

from typing import Optional, Tuple


def hex_to_rgb(h: str) -> Optional[Tuple[int, int, int]]:
    try:
        h = h.strip()
        if h.startswith("#") and len(h) == 7:
            return int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)
        return None
    except Exception:
        return None


def mix(a: Tuple[int, int, int], b: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    return (
        int(a[0] * (1 - t) + b[0] * t),
        int(a[1] * (1 - t) + b[1] * t),
        int(a[2] * (1 - t) + b[2] * t),
    )


def rel_luminance(rgb: Tuple[int, int, int]) -> float:
    def ch(c: int) -> float:
        c = c / 255.0
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> float:
    la = rel_luminance(a)
    lb = rel_luminance(b)
    l1, l2 = (la, lb) if la > lb else (lb, la)
    return (l1 + 0.05) / (l2 + 0.05)


def best_fg_for_bg(bg: Tuple[int, int, int]) -> Tuple[int, int, int]:
    white = (255, 255, 255)
    black = (0, 0, 0)
    return white if contrast(bg, white) >= contrast(bg, black) else black


def is_neutral_rgb(rgb: Tuple[int, int, int]) -> bool:
    r, g, b = rgb
    maxmin = max(r, g, b) - min(r, g, b)
    lum = rel_luminance(rgb)
    near_grey = maxmin <= 8
    near_white = lum >= 0.92
    near_black = lum <= 0.08
    return near_grey or near_white or near_black
