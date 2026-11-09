"""Health metrics domain models (dataclasses)."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SleepRecord:
    """Sleep session record."""

    date: str  # DD-MM-YYYY
    start_time: str
    end_time: str
    duration_minutes: float
    deep_sleep_minutes: float = 0.0
    rem_sleep_minutes: float = 0.0
    light_sleep_minutes: float = 0.0
    source: str = "google_health"
    id: Optional[int] = None
    created_at: Optional[str] = None


@dataclass
class WeightRecord:
    """Body weight record."""

    date: str  # DD-MM-YYYY
    weight_kg: float
    bmi: Optional[float] = None
    body_fat_pct: Optional[float] = None
    source: str = "google_health"
    id: Optional[int] = None
    created_at: Optional[str] = None
