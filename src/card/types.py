# Lightweight type definitions shared across card modules
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class Style:
    primary: Tuple[int, int, int]
    bg: Tuple[int, int, int]
    fg: Tuple[int, int, int]
    font: Optional[str]
    align: str = "center"
