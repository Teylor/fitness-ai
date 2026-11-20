"""Body progress domain model (dataclass)."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class BodyProgressRecord:
    """Daily body measurements record."""

    date: str  # DD-MM-YYYY
    weight_kg: Optional[float] = None
    waist_cm: Optional[float] = None
    chest_cm: Optional[float] = None
    arm_cm: Optional[float] = None
    leg_cm: Optional[float] = None
    notes: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
