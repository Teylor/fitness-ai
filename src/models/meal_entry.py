"""MealEntry domain model."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class MealEntry:
    """Record of a meal entry (polymorphic: ingredient or recipe)."""

    date: str  # DD-MM-YYYY
    item_type: str  # 'ingredient' | 'recipe'
    item_id: int
    quantity: float
    unit: str  # 'gr' | 'ml' | 'u'
    id: Optional[int] = None
    created_at: Optional[str] = None