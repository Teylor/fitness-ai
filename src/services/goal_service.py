"""Servicio de objetivos diarios."""

from datetime import datetime

from src.db.models import DailyGoal as DailyGoalModel
from src.models.daily_goal import DailyGoal


class GoalService:
    """Gestión de objetivos diarios."""

    @staticmethod
    def _parse_date(value: str) -> datetime:
        try:
            parsed = datetime.strptime(value, "%d-%m-%Y")
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid date '{value}' (expected DD-MM-YYYY)") from exc
        if parsed.strftime("%d-%m-%Y") != value:
            raise ValueError(f"invalid date '{value}' (expected DD-MM-YYYY)")
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
            is_default=row.is_default,
            created_at=str(row.created_at) if row.created_at is not None else None,
        )

    def _save(self, goal: DailyGoal, is_default: bool) -> DailyGoal:
        self._parse_date(goal.date)
        with DailyGoalModel._meta.database.atomic():
            row = DailyGoalModel.get_or_none(DailyGoalModel.date == goal.date)
            values = {
                "kcal": goal.kcal,
                "protein": goal.protein,
                "carbs": goal.carbs,
                "fat": goal.fat,
                "is_default": is_default,
            }
            if is_default:
                DailyGoalModel.update(is_default=False).where(
                    DailyGoalModel.is_default
                ).execute()
            if row is None:
                row = DailyGoalModel.create(date=goal.date, **values)
            else:
                for field, value in values.items():
                    setattr(row, field, value)
                row.save()
        return self._to_domain(row)

    def set_goal(self, goal: DailyGoal) -> DailyGoal:
        """Crea o actualiza el goal de un día."""
        return self._save(goal, is_default=False)

    def get_goal(self, date: str) -> DailyGoal:
        """Obtiene goal del día. Si no existe → hereda del anterior o default."""
        target = self._parse_date(date)
        row = DailyGoalModel.get_or_none(DailyGoalModel.date == date)
        if row is None:
            dated_goals = [
                candidate
                for candidate in DailyGoalModel.select().where(
                    ~DailyGoalModel.is_default
                )
                if self._parse_date(candidate.date) < target
            ]
            if dated_goals:
                row = max(dated_goals, key=lambda candidate: self._parse_date(candidate.date))
            else:
                row = DailyGoalModel.get_or_none(DailyGoalModel.is_default)
        if row is None:
            raise ValueError(f"no goal found for '{date}'")
        return self._to_domain(row)

    def set_default(self, goal: DailyGoal) -> DailyGoal:
        """Configura el goal global por defecto."""
        return self._save(goal, is_default=True)
