"""Servicio de recetas."""

from typing import List, Optional

from src.models.recipe import Recipe, RecipeItem


class RecipeService:
    """CRUD + cálculo de macros para recetas."""

    def create(self, recipe: Recipe, items: List[RecipeItem] = None) -> Recipe:
        """Crea receta. Si tiene items → calcula macros. Si no → usa precio directo."""
        ...

    def get_by_id(self, recipe_id: int) -> Optional[Recipe]:
        ...

    def find_by_name(self, name: str) -> Optional[Recipe]:
        """Búsqueda fuzzy por nombre."""
        ...

    def update(self, recipe_id: int, **fields) -> Recipe:
        ...

    def delete(self, recipe_id: int) -> int:
        ...

    def list(self, search: str = None, provisional_only: bool = False,
             type: str = None, limit: int = 50, offset: int = 0) -> List[Recipe]:
        ...

    def calculate_macros(self, recipe_id: int) -> dict:
        """Calcula kcal, P, C, G, price sumando recipe_items × ingredients."""
        ...