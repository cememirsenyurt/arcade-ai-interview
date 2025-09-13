# Canvas dimensions and layout constants for card rendering
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CanvasSpec:
    width: int = 1200
    height: int = 630
    pad_x: int = 72
    pad_top: int = 72
    pad_between: int = 20
    bullet_gap: int = 14
    bullet_indent: int = 24


CANVAS = CanvasSpec()
