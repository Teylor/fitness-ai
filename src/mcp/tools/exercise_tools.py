"""Tools MCP: catálogo de ejercicios."""

from typing import Optional


def list_exercises(
    search: str = None,
    muscle_group: str = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """Listar o buscar ejercicios."""
    ...


def create_exercise(
    name: str,
    muscle_group: str = "desconocido",
    type: str = "weight_reps",
) -> dict:
    """Crear un ejercicio nuevo."""
    ...