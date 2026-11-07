"""Servicio de objetivos diarios."""

from typing import Optional

from src.models.daily_goal import DailyGoal


class GoalService:
    """Gestión de objetivos diarios."""

    def set_goal(self, goal: DailyGoal) -> DailyGoal:
        """Crea o actualiza el goal de un día."""
        ...

    def get_goal(self, date: str) -> DailyGoal:
        """Obtiene goal del día. Si no existe → hereda del anterior o default."""
        ...

    def set_default(self, goal: DailyGoal) -> DailyGoal:
        """Configura el goal global por defecto."""
        ...