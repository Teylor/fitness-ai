"""Modelo Recipe."""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Recipe:
    """Receta (compuesta con ingredientes, o opaca con precio directo)."""

    name: str
    price: Optional[float] = None
    kcal: Optional[float] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    provisional: bool = False
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    items: List["RecipeItem"] = None  # type: ignore


@dataclass
class RecipeItem:
    """Ingrediente dentro de una receta."""

    ingredient_id: int
    quantity: float
    unit: str
    id: Optional[int] = None
    recipe_id: Optional[int] = None