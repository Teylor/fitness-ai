"""Workout Service (session registration + PR tracking)."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from src.db.models import (
    Exercise as ExerciseModel,
    ExerciseSet as ExerciseSetModel,
    PersonalRecord as PersonalRecordModel,
    WorkoutSession as WorkoutSessionModel,
)
from src.models.exercise import Exercise
from src.models.personal_record import PersonalRecord
from src.models.workout_session import WorkoutSession
from src.services.exercise_service import ExerciseService
from src.utils.errors import ValidationError
from src.utils.macros import estimate_1rm


class WorkoutService:
    """Workout session registration and personal records."""

    def __init__(self) -> None:
        self.exercises = ExerciseService()

    def register_session(
        self, session: WorkoutSession, exercises: List[Dict]
    ) -> dict:
        """Register a workout session with its exercises and sets.

        Args:
            session: WorkoutSession domain object. date: DD-MM-YYYY[ HH:MM[:SS]],
                empty/None defaults to now.
            exercises: [{"name": str, "sets": [
                {"set_number": int, "reps"?, "weight"?} |
                {"set_number": int, "duration"?} |
                {"set_number": int, "distance"?}]}]

        Returns:
            {"session": {...}, "sets": [...], "new_prs": [...], "auto_created": [...]}

        Unknown exercises are auto-created with muscle_group="unknown".
        Raises ValidationError on invalid input; the session rolls back atomically.
        """
        session_dt, public_date, date_only = self._parse_session_date(session.date)
        auto_created: List[str] = []
        new_prs: List[dict] = []

        with WorkoutSessionModel._meta.database.atomic():
            session_row = WorkoutSessionModel.create(
                date=session_dt, notes=session.notes
            )
            resolved: Dict[str, Exercise] = {}
            seen: Dict[str, set] = {}
            rows: List[Tuple[Exercise, dict]] = []
            for item in exercises:
                name = (item.get("name") or "").strip()
                if not name:
                    raise ValidationError("exercise name is required for every entry")
                if name not in resolved:
                    ex = self.exercises.find_exact(name)
                    if ex is None:
                        ex = self.exercises.create(
                            Exercise(
                                name=name,
                                muscle_group="unknown",
                                type=self._infer_type(item.get("sets")),
                            )
                        )
                        auto_created.append(name)
                    resolved[name] = ex
                for set_input in item.get("sets") or []:
                    self._validate_set(ex, set_input, seen)
                    ExerciseSetModel.create(
                        session=session_row.id,
                        exercise=ex.id,
                        set_number=set_input["set_number"],
                        reps=set_input.get("reps"),
                        weight=set_input.get("weight"),
                        duration=set_input.get("duration"),
                        distance=set_input.get("distance"),
                    )
                    rows.append((ex, set_input))

            by_exercise: Dict[str, Tuple[Exercise, List[dict]]] = {}
            for ex, set_input in rows:
                if ex.type == "weight_reps":
                    by_exercise.setdefault(ex.name, (ex, []))[1].append(set_input)
            for ex, set_inputs in by_exercise.values():
                pr = self._check_and_update_pr(ex, set_inputs, session_row, date_only)
                if pr is not None:
                    new_prs.append(pr)

            return {
                "session": {
                    "id": session_row.id,
                    "date": public_date,
                    "notes": session_row.notes,
                },
                "sets": [
                    {
                        "exercise": ex.name,
                        "set_number": set_input["set_number"],
                        "reps": set_input.get("reps"),
                        "weight": set_input.get("weight"),
                        "duration": set_input.get("duration"),
                        "distance": set_input.get("distance"),
                    }
                    for ex, set_input in rows
                ],
                "new_prs": new_prs,
                "auto_created": auto_created,
            }

    def get_last_workout(self, exercise_name: str) -> Optional[dict]:
        """Most recent session containing the exercise (fuzzy name match). None if absent."""
        ex = self.exercises.find_by_name(exercise_name)
        if ex is None:
            return None
        session = (
            WorkoutSessionModel.select()
            .join(ExerciseSetModel)
            .where(ExerciseSetModel.exercise == ex.id)
            .order_by(WorkoutSessionModel.date.desc())
            .first()
        )
        if session is None:
            return None
        sets = (
            ExerciseSetModel.select()
            .where(
                (ExerciseSetModel.session == session.id)
                & (ExerciseSetModel.exercise == ex.id)
            )
            .order_by(ExerciseSetModel.set_number)
        )
        return {
            "exercise": ex.name,
            "session_id": session.id,
            "date": self._format_datetime(session.date),
            "sets": [
                {
                    "set_number": s.set_number,
                    "reps": s.reps,
                    "weight": s.weight,
                    "duration": s.duration,
                    "distance": s.distance,
                }
                for s in sets
            ],
        }

    def get_personal_record(self, exercise_name: str) -> Optional[PersonalRecord]:
        """Personal record for the exercise (fuzzy name match). None if absent."""
        ex = self.exercises.find_by_name(exercise_name)
        if ex is None:
            return None
        row = PersonalRecordModel.get_or_none(
            PersonalRecordModel.exercise == ex.id
        )
        if row is None:
            return None
        return PersonalRecord(
            id=row.id,
            exercise_id=row.exercise_id,
            max_weight=row.max_weight,
            max_reps=row.max_reps,
            estimated_1rm=row.estimated_1rm,
            date=row.date,
            session_id=row.session_id,
        )

    def get_by_day(self, date: str) -> List[dict]:
        """All sessions of a day (DD-MM-YYYY), each with its sets. Empty list if none."""
        day_dt, _, _ = self._parse_session_date(date)
        start = datetime(day_dt.year, day_dt.month, day_dt.day)
        end = start + timedelta(days=1)
        rows = (
            WorkoutSessionModel.select()
            .where(
                (WorkoutSessionModel.date >= start)
                & (WorkoutSessionModel.date < end)
            )
            .order_by(WorkoutSessionModel.date)
        )
        return [self._session_to_dict(s) for s in rows]

    def _session_to_dict(self, session_row) -> dict:
        sets = (
            ExerciseSetModel.select()
            .where(ExerciseSetModel.session == session_row.id)
        )
        rows = list(sets)
        names = {
            r.id: r.name
            for r in ExerciseModel.select().where(
                ExerciseModel.id.in_({s.exercise_id for s in rows})
            )
        }
        rows.sort(key=lambda s: (names.get(s.exercise_id, ""), s.set_number))
        return {
            "id": session_row.id,
            "date": self._format_datetime(session_row.date),
            "notes": session_row.notes,
            "sets": [
                {
                    "exercise": names.get(s.exercise_id, ""),
                    "set_number": s.set_number,
                    "reps": s.reps,
                    "weight": s.weight,
                    "duration": s.duration,
                    "distance": s.distance,
                }
                for s in sets
            ],
        }

    @staticmethod
    def _format_datetime(dt) -> str:
        s = dt.strftime("%d-%m-%Y")
        if dt.time() != datetime.min.time():
            s += " " + dt.strftime("%H:%M:%S")
        return s

    @staticmethod
    def _parse_session_date(value: Optional[str]) -> Tuple[datetime, str, str]:
        """Parse DD-MM-YYYY[ HH:MM[:SS]]; empty/None defaults to now.

        Returns (datetime, public date string, date-only DD-MM-YYYY).
        """
        if value is None or not value.strip():
            now = datetime.now()
            return now, now.strftime("%d-%m-%Y"), now.strftime("%d-%m-%Y")
        v = value.strip()
        has_time = len(v) > 10
        if has_time:
            fmt = "%d-%m-%Y %H:%M:%S" if len(v) == 19 else "%d-%m-%Y %H:%M"
        else:
            fmt = "%d-%m-%Y"
        try:
            dt = datetime.strptime(v, fmt)
        except ValueError:
            raise ValidationError(
                f"invalid date '{value}' (expected DD-MM-YYYY[ HH:MM[:SS]])"
            )
        public = dt.strftime("%d-%m-%Y") + (dt.strftime(" %H:%M:%S") if has_time else "")
        return dt, public, dt.strftime("%d-%m-%Y")

    @staticmethod
    def _infer_type(sets: Optional[List[dict]]) -> str:
        """Infer the exercise type from a set payload (auto-created exercises).

        weight_reps: any set with reps/weight · time: duration · distance: distance.
        """
        for set_input in sets or []:
            if set_input.get("reps") is not None or set_input.get("weight") is not None:
                return "weight_reps"
        for set_input in sets or []:
            if set_input.get("duration") is not None:
                return "time"
        for set_input in sets or []:
            if set_input.get("distance") is not None:
                return "distance"
        return "weight_reps"

    @staticmethod
    def _validate_set(ex: Exercise, set_input: dict, seen: Dict[str, set]) -> None:
        number = set_input.get("set_number")
        if not isinstance(number, int) or number < 1:
            raise ValidationError(
                f"set_number must be a positive integer for exercise '{ex.name}'"
            )
        seen.setdefault(ex.name, set())
        if number in seen[ex.name]:
            raise ValidationError(
                f"duplicate set_number {number} for exercise '{ex.name}'"
            )
        seen[ex.name].add(number)
        if ex.type == "weight_reps":
            reps = set_input.get("reps")
            if not isinstance(reps, int) or reps < 1:
                raise ValidationError(
                    f"reps is required for weight_reps exercise '{ex.name}'"
                )
            if set_input.get("weight") is None:
                raise ValidationError(
                    f"weight is required for weight_reps exercise '{ex.name}'"
                )
        elif ex.type == "time":
            duration = set_input.get("duration")
            if duration is None or duration <= 0:
                raise ValidationError(
                    f"duration is required for time exercise '{ex.name}'"
                )
        elif ex.type == "distance":
            distance = set_input.get("distance")
            if distance is None or distance <= 0:
                raise ValidationError(
                    f"distance is required for distance exercise '{ex.name}'"
                )

    @staticmethod
    def _check_and_update_pr(
        ex: Exercise, set_inputs: List[dict], session_row, date_only: str
    ) -> Optional[dict]:
        """Upsert the personal record for a weight_reps exercise.

        Best set = highest estimated 1RM (reps=1 uses exact weight).
        Updates only when the new estimated 1RM is strictly greater.
        """
        best: Optional[Tuple[Tuple, dict, float]] = None
        for set_input in set_inputs:
            weight = float(set_input["weight"])
            reps = int(set_input["reps"])
            e1rm = weight if reps == 1 else estimate_1rm(weight, reps)
            key = (e1rm, weight, reps)
            if best is None or key > best[0]:
                best = (key, set_input, e1rm)
        if best is None:
            return None
        _, best_set, e1rm = best

        pr = PersonalRecordModel.get_or_none(
            PersonalRecordModel.exercise == ex.id
        )
        if pr is not None and e1rm <= pr.estimated_1rm:
            return None
        if pr is None:
            pr = PersonalRecordModel.create(
                exercise=ex.id,
                max_weight=best_set["weight"],
                max_reps=best_set["reps"],
                estimated_1rm=e1rm,
                date=date_only,
                session=session_row.id,
            )
        else:
            pr.max_weight = best_set["weight"]
            pr.max_reps = best_set["reps"]
            pr.estimated_1rm = e1rm
            pr.date = date_only
            pr.session = session_row.id
            pr.save()
        return {
            "exercise": ex.name,
            "max_weight": pr.max_weight,
            "max_reps": pr.max_reps,
            "estimated_1rm": pr.estimated_1rm,
            "date": date_only,
        }
