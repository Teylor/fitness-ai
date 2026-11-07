"""Modelo PersonalRecord."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PersonalRecord:
    """PR de un ejercicio."""

    exercise_id: int
    max_weight: float
    max_reps: int
    estimated_1rm: float
    date: str  # YYYY-MM-DD
    session_id: Optional[int] = None
    id: Optional[int] = None