"""MCP tools: Workout tracking operations."""

from typing import List, Optional


def register_workout(
    exercises: List[dict],
    date: Optional[str] = None,
    notes: Optional[str] = None,
) -> dict:
    """Register workout session.

    Args:
        exercises: [{name, sets: [{reps, weight} | {duration} | {distance}]}]
        date: ISO date/time. Default: now.
        notes: Optional notes.
    """
    ...


def get_last_workout(exercise_name: str) -> dict:
    """Get the most recent workout for an exercise."""
    ...


def get_personal_record(exercise_name: str) -> dict:
    """Get personal record for an exercise."""
    ...


def get_workouts_by_day(date: Optional[str] = None) -> dict:
    """Get all workouts for a given day."""
    ...
