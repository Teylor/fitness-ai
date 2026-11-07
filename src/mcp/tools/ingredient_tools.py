"""Tools MCP: CRUD de ingredientes."""

from typing import Optional


def create_ingredient(
    name: str,
    unit: str,
    kcal: float = 0,
    protein: float = 0,
    carbs: float = 0,
    fat: float = 0,
    price: float = 0,
    provisional: bool = False,
) -> dict:
    """Crear un ingrediente nuevo."""
    ...


def update_ingredient(
    ingredient_id: int,
    name: str = None,
    unit: str = None,
    kcal: float = None,
    protein: float = None,
    carbs: float = None,
    fat: float = None,
    price: float = None,
    provisional: bool = None,
) -> dict:
    """Editar un ingrediente existente."""
    ...


def delete_ingredient(ingredient_id: int) -> dict:
    """Eliminar un ingrediente y sus meal_entries."""
    ...


def list_ingredients(
    search: str = None,
    provisional_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """Listar o buscar ingredientes."""
    ...