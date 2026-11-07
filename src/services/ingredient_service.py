"""Servicio de ingredientes."""

from typing import List, Optional

from src.models.ingredient import Ingredient


class IngredientService:
    """CRUD + búsqueda de ingredientes."""

    def create(self, ingredient: Ingredient) -> Ingredient:
        """Crea un ingrediente. Lanza error si ya existe (name+unit)."""
        ...

    def get_by_id(self, ingredient_id: int) -> Optional[Ingredient]:
        ...

    def find_by_name(self, name: str) -> Optional[Ingredient]:
        """Búsqueda fuzzy por nombre."""
        ...

    def update(self, ingredient_id: int, **fields) -> Ingredient:
        ...

    def delete(self, ingredient_id: int) -> int:
        """Elimina y devuelve nº de meal_entries afectados."""
        ...

    def list(self, search: str = None, provisional_only: bool = False,
             limit: int = 50, offset: int = 0) -> List[Ingredient]:
        ...