"""Modelo DailyGoal."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DailyGoal:
    """Objetivo diario de macros."""

    date: str  # DD-MM-YYYY
    kcal: float
    protein: float
    carbs: float
    fat: float
    is_default: bool = False
    id: Optional[int] = None
    created_at: Optional[str] = None