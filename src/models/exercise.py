"""Exercise domain model."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Exercise:
    """Exercise in the catalog."""

    name: str
    muscle_group: str = "unknown"
    type: str = "weight_reps"  # 'weight_reps' | 'time' | 'distance'
    id: Optional[int] = None
    created_at: Optional[str] = None