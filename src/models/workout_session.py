"""WorkoutSession domain model."""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class WorkoutSession:
    """Workout session."""

    date: str  # YYYY-MM-DDTHH:MM:SS
    notes: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
    sets: List["ExerciseSet"] = None  # type: ignore