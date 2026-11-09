"""Exercise Service (CRUD + fuzzy search)."""

from typing import List, Optional

from src.db.models import Exercise as ExerciseModel
from src.models.exercise import Exercise
from src.utils.errors import ValidationError
from src.utils.fuzzy import fuzzy_match, normalize

VALID_TYPES = ("weight_reps", "time", "distance")


class ExerciseService:
    """Exercise CRUD over the database layer."""

    def create(self, exercise: Exercise) -> Exercise:
        """Create an exercise. Idempotent: an exact/normalized-name duplicate returns the existing row.

        Raises ValidationError on empty name or invalid type.
        """
        if not exercise.name or not exercise.name.strip():
            raise ValidationError("exercise name is required")
        if exercise.type not in VALID_TYPES:
            raise ValidationError(
                f"invalid type '{exercise.type}' (expected weight_reps/time/distance)"
            )
        existing = self.find_exact(exercise.name)
        if existing is not None:
            return existing
        row = ExerciseModel.create(
            name=exercise.name,
            muscle_group=exercise.muscle_group or "unknown",
            type=exercise.type,
        )
        return self._to_domain(row)

    def get_by_id(self, exercise_id: int) -> Optional[Exercise]:
        """Return the exercise or None if it does not exist."""
        row = ExerciseModel.get_or_none(ExerciseModel.id == exercise_id)
        return None if row is None else self._to_domain(row)

    def find_exact(self, name: str) -> Optional[Exercise]:
        """Find by exact (case-insensitive) name, then normalized (accent-insensitive) name. No fuzzy."""
        if not name:
            return None
        row = ExerciseModel.get_or_none(ExerciseModel.name == name)
        if row is None:
            q = normalize(name)
            for candidate in ExerciseModel.select():
                if normalize(candidate.name) == q:
                    row = candidate
                    break
        return None if row is None else self._to_domain(row)

    def find_by_name(self, name: str) -> Optional[Exercise]:
        """Find by name: exact (normalized) match first, then fuzzy."""
        row = self.find_exact(name)
        if row is not None:
            return row
        match = fuzzy_match(name, [r.name for r in ExerciseModel.select()])
        if match is not None:
            row = ExerciseModel.get_or_none(ExerciseModel.name == match)
        return None if row is None else self._to_domain(row)

    def list(
        self,
        search: Optional[str] = None,
        muscle_group: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Exercise]:
        """List exercises with optional name search, muscle group filter, and pagination."""
        rows = list(ExerciseModel.select().order_by(ExerciseModel.id))
        if search:
            q = normalize(search)
            rows = [r for r in rows if q in normalize(r.name)]
        if muscle_group:
            mg = muscle_group.lower()
            rows = [r for r in rows if r.muscle_group.lower() == mg]
        return [self._to_domain(r) for r in rows[offset : offset + limit]]

    @staticmethod
    def _to_domain(row) -> Exercise:
        return Exercise(
            id=row.id,
            name=row.name,
            muscle_group=row.muscle_group,
            type=row.type,
            created_at=str(row.created_at) if row.created_at is not None else None,
        )
