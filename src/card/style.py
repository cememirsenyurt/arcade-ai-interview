# Style inference from flow.json and optional overrides
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from .color import hex_to_rgb, is_neutral_rgb, contrast, mix, best_fg_for_bg


def _collect_candidate_colors(flow: Dict[str, Any]) -> List[str]:
    colors: List[str] = []
    for step in flow.get("steps", []) or []:
        for hs in step.get("hotspots", []) or []:
            for k in ("bgColor", "textColor"):
                v = hs.get(k)
                if isinstance(v, str):
                    colors.append(v)
        for p in step.get("paths", []) or []:
            for k in ("buttonColor", "buttonTextColor"):
                v = p.get(k)
                if isinstance(v, str):
                    colors.append(v)
    return colors


def _pick_primary(colors: List[str]) -> Optional[Tuple[int, int, int]]:
    non_neutral_counts: Dict[str, int] = {}
    all_counts: Dict[str, int] = {}
    for c in colors:
        rgb = hex_to_rgb(c)
        if rgb is None:
            continue
        key = f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        all_counts[key] = all_counts.get(key, 0) + 1
        if not is_neutral_rgb(rgb):
            non_neutral_counts[key] = non_neutral_counts.get(key, 0) + 1
    use_counts = non_neutral_counts if non_neutral_counts else all_counts
    if not use_counts:
        return None
    best_hex = max(use_counts.items(), key=lambda kv: kv[1])[0]
    return hex_to_rgb(best_hex)


def _detect_theme(flow: Dict[str, Any]) -> str:
    theme = None
    for step in flow.get("steps", []) or []:
        if step.get("type") == "CHAPTER" and isinstance(step.get("theme"), str):
            theme = step.get("theme").lower().strip()
    return theme or "dark"


def _preferred_font(flow: Dict[str, Any]) -> Optional[str]:
    f = flow.get("font")
    if isinstance(f, str) and f.strip():
        return f.strip()
    return None


def _preferred_align(flow: Dict[str, Any]) -> str:
    align = None
    for step in flow.get("steps", []) or []:
        if step.get("type") == "CHAPTER" and isinstance(step.get("textAlign"), str):
            align = step.get("textAlign").lower().strip()
    return align if align in ("left", "center", "right") else "center"


def derive_style_from_flow(flow: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Infer style spec from flow.json without hardcoding brands.

    Returns a dict with keys: primary, bg, fg, font, align
    """
    default_bg = (24, 24, 36)
    default_fg = (255, 255, 255)
    default_primary = (33, 66, 231)

    if not isinstance(flow, dict):
        return {"primary": default_primary, "bg": default_bg, "fg": default_fg, "font": None, "align": "center"}

    theme = _detect_theme(flow)
    primary = _pick_primary(_collect_candidate_colors(flow)) or default_primary

    white, black = (255, 255, 255), (0, 0, 0)
    cw = contrast(primary, white)
    cb = contrast(primary, black)

    if max(cw, cb) >= 4.5:
        bg = primary
        fg = white if cw >= cb else black
    else:
        bg = mix(primary, white if theme == "light" else black, 0.85)
        fg = best_fg_for_bg(bg)

    font = _preferred_font(flow)
    align = _preferred_align(flow)
    return {"primary": primary, "bg": bg, "fg": fg, "font": font, "align": align}
