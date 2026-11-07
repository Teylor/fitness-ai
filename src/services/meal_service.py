"""Servicio de registro de comidas."""

from typing import Optional

from src.models.meal_entry import MealEntry


class MealService:
    """Registro y consulta de ingesta diaria."""

    def register(self, entry: MealEntry) -> MealEntry:
        """Registra una ingesta. Crea provisional si no existe el item."""
        ...

    def get_day_entries(self, date: str) -> list:
        """Devuelve todas las ingesta de un día con macros calculados."""
        ...

    def get_day_summary(self, date: str) -> dict:
        """Resumen: consumed, goal, remaining, spend, meals."""
        ...

    def delete(self, entry_id: int) -> None:
        ...

    def update(self, entry_id: int, **fields) -> MealEntry:
        ...