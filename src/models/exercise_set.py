"""Modelo ExerciseSet."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ExerciseSet:
    """Un set dentro de una sesión."""

    session_id: int
    exercise_id: int
    set_number: int
    reps: Optional[int] = None
    weight: Optional[float] = None
    duration: Optional[float] = None  # segundos
    distance: Optional[float] = None  # metros
    id: Optional[int] = None