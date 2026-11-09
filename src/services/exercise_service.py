"""Exercise domain service."""

from typing import List, Optional

from src.models.exercise import Exercise


class ExerciseService:
    """CRUD + search for exercises."""

    def create(self, exercise: Exercise) -> Exercise:
        ...

    def get_by_id(self, exercise_id: int) -> Optional[Exercise]:
        ...

    def find_by_name(self, name: str) -> Optional[Exercise]:
        """Fuzzy search by name."""
        ...

    def list(self, search: str = None, muscle_group: str = None,
             limit: int = 50, offset: int = 0) -> List[Exercise]:
        ...
