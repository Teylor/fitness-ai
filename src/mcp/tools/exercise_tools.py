"""MCP tools: Exercise catalog operations."""

from typing import Optional


def list_exercises(
    search: str = None,
    muscle_group: str = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """List or search exercises."""
    ...


def create_exercise(
    name: str,
    muscle_group: str = "unknown",
    type: str = "weight_reps",
) -> dict:
    """Create a new exercise."""
    ...
