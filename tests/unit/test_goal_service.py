"""Tests: GoalService."""

import pytest

from src.db.models import DailyGoal as DailyGoalModel
from src.models.daily_goal import DailyGoal
from src.utils.errors import NotFoundError, ValidationError


def make_goal(date, kcal=2000, protein=120, carbs=220, fat=60, is_default=False):
    return DailyGoal(
        date=date,
        kcal=kcal,
        protein=protein,
        carbs=carbs,
        fat=fat,
        is_default=is_default,
    )


def test_set_goal_persists_goal_and_returns_domain_model(db, goal_service):
    goal = goal_service.set_goal(make_goal("10-05-2026"))

    assert goal.id is not None
    assert goal.date == "10-05-2026"
    assert (goal.kcal, goal.protein, goal.carbs, goal.fat) == (2000, 120, 220, 60)
    assert goal.is_default is False
    assert DailyGoalModel.select().count() == 1


def test_get_goal_explicit(db, goal_service):
    saved = goal_service.set_goal(make_goal("10-05-2026", kcal=2100))

    goal = goal_service.get_goal("10-05-2026")

    assert goal.id == saved.id
    assert goal.kcal == 2100


def test_get_goal_inherits_closest_previous_goal(db, goal_service):
    goal_service.set_goal(make_goal("01-05-2026", kcal=1800))
    goal_service.set_goal(make_goal("07-05-2026", kcal=1900))
    goal_service.set_goal(make_goal("12-05-2026", kcal=2300))

    goal = goal_service.get_goal("10-05-2026")

    assert goal.date == "07-05-2026"
    assert goal.kcal == 1900


def test_get_goal_falls_back_to_default(db, goal_service):
    default = goal_service.set_default(make_goal("01-01-2026", kcal=1750))

    goal = goal_service.get_goal("10-05-2026")

    assert goal.id == default.id
    assert goal.is_default is True


def test_set_default_persists_and_marks_default(db, goal_service):
    goal = goal_service.set_default(make_goal("01-01-2026", kcal=2000))

    assert goal.id is not None
    assert goal.is_default is True
    assert DailyGoalModel.select().where(DailyGoalModel.is_default).count() == 1


def test_setting_new_default_clears_previous_default(db, goal_service):
    first = goal_service.set_default(make_goal("01-01-2026", kcal=1800))

    second = goal_service.set_default(make_goal("02-01-2026", kcal=2000))

    assert second.is_default is True
    assert DailyGoalModel.get_by_id(first.id).is_default is False
    assert DailyGoalModel.select().where(DailyGoalModel.is_default).count() == 1


def test_update_goal_same_day(db, goal_service):
    first = goal_service.set_goal(make_goal("10-05-2026", kcal=1800))
    updated = goal_service.set_goal(make_goal("10-05-2026", kcal=2200))

    assert updated.id == first.id
    assert updated.kcal == 2200
    assert DailyGoalModel.select().count() == 1


def test_get_goal_without_matching_or_default_raises(db, goal_service):
    with pytest.raises(NotFoundError) as exc_info:
        goal_service.get_goal("10-05-2026")
    assert exc_info.value.code == "not_found"
    assert "no goal found" in str(exc_info.value)


def test_invalid_goal_date_raises(db, goal_service):
    with pytest.raises(ValidationError) as exc_info:
        goal_service.set_goal(make_goal("2026-05-10"))
    assert exc_info.value.code == "invalid_input"
    assert "invalid date" in str(exc_info.value)


def test_day_off_default_and_toggle_isolation(db, goal_service):
    goal_service.set_default(make_goal("10-05-2026", kcal=2500, protein=180, carbs=280, fat=70))
    goal_service.set_day_off_default(make_goal("01-01-1900", kcal=2000, protein=180, carbs=150, fat=70))

    # Enable Day Off on 10-05-2026 (even though it held the training default)
    off_goal = goal_service.toggle_day_off("10-05-2026", is_day_off=True)
    assert off_goal.is_day_off is True
    assert off_goal.kcal == 2000

    # Next day 11-05-2026 must still inherit Training Day default (not Day Off!)
    next_day = goal_service.get_goal("11-05-2026")
    assert next_day.is_day_off is False
    assert next_day.kcal == 2500

    # Disable Day Off on 10-05-2026 -> reverts to Training Day default
    restored = goal_service.toggle_day_off("10-05-2026", is_day_off=False)
    assert restored.is_day_off is False
    assert restored.kcal == 2500


def test_toggle_day_off_without_day_off_default_raises(db, goal_service):
    goal_service.set_default(make_goal("01-01-2026", kcal=2400))
    with pytest.raises(NotFoundError) as exc_info:
        goal_service.toggle_day_off("10-05-2026", is_day_off=True)
    assert exc_info.value.code == "not_found"

