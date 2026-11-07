"""Servicio de sesiones de entrenamiento."""

from typing import Optional

from src.models.workout_session import WorkoutSession
from src.models.exercise_set import ExerciseSet
from src.models.personal_record import PersonalRecord


class WorkoutService:
    """Registro y consulta de entrenamientos."""

    def register_session(self, session: WorkoutSession, sets: list) -> dict:
        """Registra sesión + sets. Auto-calcular PRs. Devuelve session + new_prs."""
        ...

    def get_last_workout(self, exercise_name: str) -> dict:
        """Último entreno de un ejercicio."""
        ...

    def get_personal_record(self, exercise_name: str) -> Optional[PersonalRecord]:
        ...

    def get_by_day(self, date: str) -> list:
        """Todas las sesiones de un día con sus sets."""
        ...

    def _check_and_update_pr(self, exercise_id: int, sets: list, session_id: int) -> list:
        """Compara sets con PR actual. Devuelve lista de PRs actualizados."""
        ...