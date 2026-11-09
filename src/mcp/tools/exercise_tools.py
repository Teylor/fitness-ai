"""MCP tools: Exercise catalog operations."""

from dataclasses import asdict
from typing import Optional

from src.models.exercise import Exercise
from src.services.exercise_service import ExerciseService
from src.utils.errors import ToolError


def list_exercises(
    search: str = None,
    muscle_group: str = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """List or search exercises with optional pagination."""
    service = ExerciseService()
    try:
        items = service.list(
            search=search, muscle_group=muscle_group, limit=limit, offset=offset
        )
        return {
            "status": "ok",
            "exercises": [asdict(item) for item in items],
            "count": len(items),
        }
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
