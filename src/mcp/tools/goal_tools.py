"""Tools MCP: objetivos diarios."""

from typing import Optional


def set_daily_goal(
    kcal: float,
    protein: float,
    carbs: float,
    fat: float,
    date: Optional[str] = None,
) -> dict:
    """Configurar objetivo diario."""
    ...


def get_daily_goal(date: Optional[str] = None) -> dict:
    """Obtener objetivo del día (con fallback: explicit → inherited → default)."""
    ...