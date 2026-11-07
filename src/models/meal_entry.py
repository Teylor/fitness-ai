"""Modelo MealEntry."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class MealEntry:
    """Registro de una ingesta (polimórfico: ingrediente o receta)."""

    date: str  # YYYY-MM-DD
    item_type: str  # 'ingredient' | 'recipe'
    item_id: int
    quantity: float
    unit: str  # 'gr' | 'ml' | 'u'
    id: Optional[int] = None
    created_at: Optional[str] = None