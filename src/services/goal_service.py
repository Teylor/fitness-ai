"""Daily Goal domain service."""

from dataclasses import asdict
from datetime import datetime
from typing import Optional

from src.db.models import DailyGoal as DailyGoalModel
from src.models.daily_goal import DailyGoal
from src.utils.errors import NotFoundError, ValidationError

DAY_OFF_DEFAULT_DATE = "01-01-1900"
TRAINING_DEFAULT_BACKUP_DATE = "01-01-1901"


class GoalService:
    """Daily goal management and fallback inheritance."""

    @staticmethod
    def _parse_date(value: str) -> datetime:
        try:
            parsed = datetime.strptime(value, "%d-%m-%Y")
        except (TypeError, ValueError) as exc:
            raise ValidationError(f"invalid date '{value}' (expected DD-MM-YYYY)") from exc
        if parsed.strftime("%d-%m-%Y") != value:
            raise ValidationError(f"invalid date '{value}' (expected DD-MM-YYYY)")
        return parsed

    @staticmethod
    def _to_domain(row) -> DailyGoal:
        return DailyGoal(
            id=row.id,
            date=row.date,
            kcal=row.kcal,
            protein=row.protein,
            carbs=row.carbs,
            fat=row.fat,
            is_default=bool(getattr(row, "is_default", False)),
            is_day_off=bool(getattr(row, "is_day_off", False)),
            is_day_off_default=bool(getattr(row, "is_day_off_default", False)),
            created_at=str(row.created_at) if row.created_at is not None else None,
        )

    def _save(
        self,
        goal: DailyGoal,
        is_default: bool,
        is_day_off: bool = False,
        is_day_off_default: bool = False,
    ) -> DailyGoal:
        self._parse_date(goal.date)
        with DailyGoalModel._meta.database.atomic():
            row = DailyGoalModel.get_or_none(DailyGoalModel.date == goal.date)
            values = {
                "kcal": goal.kcal,
                "protein": goal.protein,
                "carbs": goal.carbs,
                "fat": goal.fat,
                "is_default": is_default,
                "is_day_off": is_day_off,
                "is_day_off_default": is_day_off_default,
            }
            if is_default:
                DailyGoalModel.update(is_default=False).where(
                    DailyGoalModel.is_default
                ).execute()
            if is_day_off_default:
                DailyGoalModel.update(is_day_off_default=False).where(
                    DailyGoalModel.is_day_off_default
                ).execute()
            if row is None:
                row = DailyGoalModel.create(date=goal.date, **values)
            else:
                for field, value in values.items():
                    setattr(row, field, value)
                row.save()
        return self._to_domain(row)

    def set_goal(self, goal: DailyGoal) -> DailyGoal:
        """Create or update a single date goal."""
        return self._save(goal, is_default=False, is_day_off=goal.is_day_off)

    def get_goal(self, date: str) -> DailyGoal:
        """Get goal for a given date with fallback to closest past date or default."""
        target = self._parse_date(date)
        row = DailyGoalModel.get_or_none(
            (DailyGoalModel.date == date) & (~DailyGoalModel.is_day_off_default)
        )
        if row is None:
            dated_goals = [
                candidate
                for candidate in DailyGoalModel.select().where(
                    (~DailyGoalModel.is_default)
                    & (~DailyGoalModel.is_day_off_default)
                    & (~DailyGoalModel.is_day_off)
                )
                if self._parse_date(candidate.date) < target
            ]
            if dated_goals:
                row = max(dated_goals, key=lambda candidate: self._parse_date(candidate.date))
            else:
                row = DailyGoalModel.get_or_none(DailyGoalModel.is_default)
        if row is None:
            raise NotFoundError(f"no goal found for '{date}'")
        return self._to_domain(row)

    def set_default(self, goal: DailyGoal) -> DailyGoal:
        """Set or update the global default (training day) goal."""
        return self._save(goal, is_default=True)

    def set_day_off_default(self, goal: DailyGoal) -> DailyGoal:
        """Set or update the global Day Off default goal."""
        target_goal = DailyGoal(
            date=DAY_OFF_DEFAULT_DATE,
            kcal=goal.kcal,
            protein=goal.protein,
            carbs=goal.carbs,
            fat=goal.fat,
            is_default=False,
            is_day_off=True,
            is_day_off_default=True,
        )
        return self._save(
            target_goal,
            is_default=False,
            is_day_off=True,
            is_day_off_default=True,
        )

    def get_goal_profiles(self) -> dict:
        """Return both configured global defaults (training_default and day_off_default)."""
        tr_row = DailyGoalModel.get_or_none(DailyGoalModel.is_default)
        off_row = DailyGoalModel.get_or_none(DailyGoalModel.is_day_off_default)
        return {
            "training_default": asdict(self._to_domain(tr_row)) if tr_row else None,
            "day_off_default": asdict(self._to_domain(off_row)) if off_row else None,
        }

    def toggle_day_off(self, date: str, is_day_off: Optional[bool] = None) -> DailyGoal:
        """Enable, disable, or flip Day Off mode for a specific date."""
        self._parse_date(date)
        if is_day_off is None:
            try:
                current = self.get_goal(date)
                target_state = not current.is_day_off
            except NotFoundError:
                target_state = True
        else:
            target_state = bool(is_day_off)

        with DailyGoalModel._meta.database.atomic():
            if target_state:
                off_default = DailyGoalModel.get_or_none(DailyGoalModel.is_day_off_default)
                if off_default is None:
                    raise NotFoundError(
                        "no day-off default goal configured; set a day-off goal first"
                    )
                existing = DailyGoalModel.get_or_none(DailyGoalModel.date == date)
                if existing is not None and existing.is_default:
                    # Preserve the training default on a safe sentinel date before overriding this date
                    backup = DailyGoalModel.get_or_none(
                        DailyGoalModel.date == TRAINING_DEFAULT_BACKUP_DATE
                    )
                    if backup is None:
                        DailyGoalModel.create(
                            date=TRAINING_DEFAULT_BACKUP_DATE,
                            kcal=existing.kcal,
                            protein=existing.protein,
                            carbs=existing.carbs,
                            fat=existing.fat,
                            is_default=True,
                            is_day_off=False,
                            is_day_off_default=False,
                        )
                    else:
                        backup.kcal = existing.kcal
                        backup.protein = existing.protein
                        backup.carbs = existing.carbs
                        backup.fat = existing.fat
                        backup.is_default = True
                        backup.save()
                    existing.is_default = False
                    existing.save()

                return self._save(
                    DailyGoal(
                        date=date,
                        kcal=off_default.kcal,
                        protein=off_default.protein,
                        carbs=off_default.carbs,
                        fat=off_default.fat,
                        is_day_off=True,
                    ),
                    is_default=False,
                    is_day_off=True,
                    is_day_off_default=False,
                )

            # Disabling Day Off: remove date-specific day-off override so normal goal chain applies
            existing = DailyGoalModel.get_or_none(DailyGoalModel.date == date)
            if existing is not None and existing.is_day_off and not existing.is_day_off_default:
                existing.delete_instance()

        return self.get_goal(date)
