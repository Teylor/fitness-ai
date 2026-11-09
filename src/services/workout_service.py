"""Workout session domain service."""

from typing import Optional

from src.models.exercise_set import ExerciseSet
from src.models.personal_record import PersonalRecord
from src.models.workout_session import WorkoutSession


class WorkoutService:
    """Workout tracking and historical analysis."""

    def register_session(self, session: WorkoutSession, sets: list) -> dict:
        """Register session and sets. Auto-calculates PRs. Returns session + new_prs."""
        ...

    def get_last_workout(self, exercise_name: str) -> dict:
        """Get the most recent workout for an exercise."""
        ...

    def get_personal_record(self, exercise_name: str) -> Optional[PersonalRecord]:
        ...

    def get_by_day(self, date: str) -> list:
        """Get all sessions of a given day with their sets."""
        ...

    def _check_and_update_pr(self, exercise_id: int, sets: list, session_id: int) -> list:
        """Compare sets with current PR. Returns list of updated PRs."""
        ...
