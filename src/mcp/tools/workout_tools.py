"""MCP tools: Workout tracking operations."""

from dataclasses import asdict
from typing import List, Optional

from src.models.workout_session import WorkoutSession
from src.services.workout_service import WorkoutService
from src.utils.errors import ToolError


def register_workout(
    exercises: List[dict],
    date: Optional[str] = None,
    notes: Optional[str] = None,
) -> dict:
    """Register a workout session.

    Args:
        exercises: [{"name": str, "sets": [{"set_number", "reps"?, "weight"?} |
            {"set_number", "duration"?} | {"set_number", "distance"?}]}]
        date: DD-MM-YYYY[ HH:MM[:SS]]. Default: now.
        notes: Optional notes.
    """
    service = WorkoutService()
    try:
        result = service.register_session(
            WorkoutSession(date=date or "", notes=notes), exercises
        )
        return {"status": "ok", **result}
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


def get_last_workout(exercise_name: str) -> dict:
    """Get the most recent workout for an exercise."""
    service = WorkoutService()
    try:
        result = service.get_last_workout(exercise_name)
        if result is None:
            return {
                "status": "error",
                "code": "not_found",
                "message": f"no workout found for '{exercise_name}'",
            }
        return {"status": "ok", **result}
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


def get_personal_record(exercise_name: str) -> dict:
    """Get the personal record for an exercise."""
    service = WorkoutService()
    try:
        pr = service.get_personal_record(exercise_name)
        if pr is None:
            return {
                "status": "error",
                "code": "not_found",
                "message": f"no personal record for '{exercise_name}'",
            }
        return {"status": "ok", "personal_record": asdict(pr)}
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


def get_workouts_by_day(date: Optional[str] = None) -> dict:
    """Get all workouts for a given day (DD-MM-YYYY). Default: today."""
    service = WorkoutService()
    try:
        sessions = service.get_by_day(date or "")
        return {"status": "ok", "sessions": sessions, "count": len(sessions)}
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}
