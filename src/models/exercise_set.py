"""ExerciseSet domain model."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ExerciseSet:
    """A set within a workout session."""

    session_id: int
    exercise_id: int
    set_number: int
    reps: Optional[int] = None
    weight: Optional[float] = None
    duration: Optional[float] = None  # seconds
    distance: Optional[float] = None  # meters
    id: Optional[int] = None