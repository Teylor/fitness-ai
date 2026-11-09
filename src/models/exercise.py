"""Modelo Exercise."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Exercise:
    """Ejercicio del catálogo."""

    name: str
    muscle_group: str = "unknown"
    type: str = "weight_reps"  # 'weight_reps' | 'time' | 'distance'
    id: Optional[int] = None
    created_at: Optional[str] = None