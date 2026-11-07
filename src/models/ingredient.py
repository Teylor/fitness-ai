"""Modelo Ingredient."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Ingredient:
    """Ingrediente con macros y precio por unidad base."""

    name: str
    unit: str  # 'gr' | 'ml' | 'u'
    kcal: float = 0.0
    protein: float = 0.0
    carbs: float = 0.0
    fat: float = 0.0
    price: float = 0.0
    provisional: bool = False
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None