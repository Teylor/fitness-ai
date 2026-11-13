"""DailyGoal domain model."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DailyGoal:
    """Daily macro goal."""

    date: str  # DD-MM-YYYY
    kcal: float
    protein: float
    carbs: float
    fat: float
    is_default: bool = False
    is_day_off: bool = False
    is_day_off_default: bool = False
    id: Optional[int] = None
    created_at: Optional[str] = None