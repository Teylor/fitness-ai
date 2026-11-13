"""MCP tools: Exercise catalog operations."""

from dataclasses import asdict
from typing import Optional, Union

from src.models.exercise import Exercise
from src.services.exercise_service import ExerciseService
from src.utils.errors import ToolError


def list_exercises(
    search: str = None,
    muscle_group: str = None,
    limit: int = 50,
    offset: int = 0,
    include_prs: Union[bool, str] = False,
) -> dict:
    """List or search exercises with optional pagination and PR stats."""
    service = ExerciseService()
    try:
        should_include_prs = (
            include_prs.lower() in ("true", "1", "yes")
            if isinstance(include_prs, str)
            else bool(include_prs)
        )
        items = service.list(
            search=search, muscle_group=muscle_group, limit=limit, offset=offset
        )
        exercises_data = [asdict(item) for item in items]
        if should_include_prs:
            from src.services.workout_service import WorkoutService

            stats = WorkoutService().get_exercise_stats()
            for ex in exercises_data:
                ex["pr"] = stats.get(ex.get("id"))
        return {
            "status": "ok",
            "exercises": exercises_data,
            "count": len(exercises_data),
        }
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


def update_exercise(
    exercise_id: int,
    muscle_group: Optional[str] = None,
    type: Optional[str] = None,
) -> dict:
    """Partially update an exercise's muscle group and/or type."""
    service = ExerciseService()
    try:
        updated = service.update(
            exercise_id, muscle_group=muscle_group, type=type
        )
        return {"status": "ok", "exercise": asdict(updated)}
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


def create_exercise(
    name: str,
    muscle_group: str = "unknown",
    type: str = "weight_reps",
) -> dict:
    """Create a new exercise (idempotent: duplicates return the existing one)."""
    service = ExerciseService()
    try:
        created = service.create(
            Exercise(name=name, muscle_group=muscle_group, type=type)
        )
        return {"status": "ok", "exercise": asdict(created)}
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}
