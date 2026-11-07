"""Tools MCP: entrenamiento."""

from typing import Optional, List


def register_workout(
    exercises: List[dict],
    date: Optional[str] = None,
    notes: Optional[str] = None,
) -> dict:
    """Registrar sesión de entrenamiento.

    Args:
        exercises: [{name, sets: [{reps, weight} | {duration} | {distance}]}]
        date: Fecha/hora ISO. Default: ahora.
        notes: Notas opcionales.
    """
    ...


def get_last_workout(exercise_name: str) -> dict:
    """Último entrenamiento de un ejercicio."""
    ...


def get_personal_record(exercise_name: str) -> dict:
    """Personal Record de un ejercicio."""
    ...


def get_workouts_by_day(date: Optional[str] = None) -> dict:
    """Todos los entrenamientos de un día."""
    ...