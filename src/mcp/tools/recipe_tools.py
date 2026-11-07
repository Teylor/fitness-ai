"""Tools MCP: CRUD de recetas."""

from typing import Optional, List


def create_recipe(
    name: str,
    ingredients: List[dict] = None,
    price: float = None,
    kcal: float = None,
    protein: float = None,
    carbs: float = None,
    fat: float = None,
    provisional: bool = False,
) -> dict:
    """Crear receta (compuesta con ingredientes, o opaca con precio directo).

    Args:
        name: Nombre de la receta.
        ingredients: Lista de {name, quantity, unit}. Si None → receta opaca.
        price: Precio directo (obligatorio si no hay ingredients).
        kcal/protein/carbs/fat: Solo para recetas opacas.
    """
    ...


def update_recipe(
    recipe_id: int,
    name: str = None,
    price: float = None,
    kcal: float = None,
    protein: float = None,
    carbs: float = None,
    fat: float = None,
    provisional: bool = None,
    ingredients: List[dict] = None,
) -> dict:
    """Editar una receta existente."""
    ...


def delete_recipe(recipe_id: int) -> dict:
    """Eliminar una receta y sus meal_entries."""
    ...


def list_recipes(
    search: str = None,
    provisional_only: bool = False,
    type: str = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """Listar o buscar recetas."""
    ...