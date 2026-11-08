"""Tests: MealService."""

import pytest

from src.db.models import (
    Ingredient as IngredientModel,
    MealEntry as MealEntryModel,
    Recipe as RecipeModel,
)
from src.models.daily_goal import DailyGoal
from src.models.ingredient import Ingredient
from src.models.meal_entry import MealEntry
from src.models.recipe import Recipe


def make_entry(item_type, item_id, quantity, date, unit="gr"):
    return MealEntry(
        date=date,
        item_type=item_type,
        item_id=item_id,
        quantity=quantity,
        unit=unit,
    )


def test_register_meal_ingredient(db, meal_service, ingredient_service):
    ing = ingredient_service.create(
        Ingredient(name="rice", unit="gr", kcal=360, protein=7, carbs=78, fat=0.6, price=0.9)
    )

    entry = meal_service.register(
        make_entry("ingredient", ing.id, 200, "10-05-2026", unit="gr")
    )

    assert entry.id is not None
    assert entry.item_type == "ingredient"
    assert entry.item_id == ing.id
    assert entry.quantity == 200
    assert entry.unit == "gr"
    assert entry.date == "10-05-2026"
    assert MealEntryModel.select().count() == 1


def test_register_meal_recipe(db, meal_service, recipe_service):
    rec = recipe_service.create(
        Recipe(name="pasta", price=4.5, kcal=900, protein=30, carbs=120, fat=8)
    )

    entry = meal_service.register(
        make_entry("recipe", rec.id, 1.0, "10-05-2026", unit="u")
    )

    assert entry.id is not None
    assert entry.item_type == "recipe"
    assert entry.item_id == rec.id
    assert MealEntryModel.select().count() == 1


def test_register_meal_creates_provisional(db, meal_service):
    ing_entry = meal_service.register(
        make_entry("ingredient", 99, 50, "10-05-2026", unit="gr")
    )
    rec_entry = meal_service.register(
        make_entry("recipe", 77, 1.0, "10-05-2026", unit="u")
    )

    ing_row = IngredientModel.get_by_id(99)
    assert ing_row is not None
    assert ing_row.name == "provisional-99"
    assert ing_row.provisional is True
    assert ing_row.unit == "gr"
    assert (ing_row.kcal, ing_row.protein, ing_row.carbs, ing_row.fat, ing_row.price) == (
        0, 0, 0, 0, 0
    )
    rec_row = RecipeModel.get_by_id(77)
    assert rec_row is not None
    assert rec_row.name == "provisional-77"
    assert rec_row.provisional is True
    assert (rec_row.price, rec_row.kcal, rec_row.protein) == (None, None, None)
    assert ing_entry.item_id == 99
    assert rec_entry.item_id == 77
    assert MealEntryModel.select().count() == 2


def test_get_day_summary(db, meal_service, ingredient_service, goal_service):
    ing = ingredient_service.create(
        Ingredient(name="rice", unit="gr", kcal=360, protein=7, carbs=78, fat=0.6, price=0.9)
    )
    goal_service.set_goal(
        DailyGoal(date="10-05-2026", kcal=2500, protein=150, carbs=250, fat=80)
    )
    meal_service.register(
        make_entry("ingredient", ing.id, 200, "10-05-2026", unit="gr")
    )

    summary = meal_service.get_day_summary("10-05-2026")

    assert summary["consumed"] == {"kcal": 720.0, "protein": 14.0, "carbs": 156.0, "fat": 1.2}
    assert summary["spend"] == 0.18
    assert summary["goal"]["date"] == "10-05-2026"
    assert summary["goal"]["kcal"] == 2500
    assert summary["remaining"] == {
        "kcal": 1780.0,
        "protein": 136.0,
        "carbs": 94.0,
        "fat": 78.8,
    }
    assert len(summary["meals"]) == 1
    assert summary["meals"][0]["kcal"] == 720.0
    assert summary["meals"][0]["price"] == 0.18


def test_get_day_summary_no_goal_uses_default(db, meal_service, goal_service):
    goal_service.set_default(
        DailyGoal(date="01-01-2026", kcal=2000, protein=130, carbs=230, fat=65)
    )

    summary = meal_service.get_day_summary("10-05-2026")

    assert summary["consumed"] == {"kcal": 0, "protein": 0, "carbs": 0, "fat": 0}
    assert summary["spend"] == 0
    assert summary["goal"]["kcal"] == 2000
    assert summary["remaining"]["kcal"] == 2000
    assert summary["meals"] == []


def test_delete_meal_entry(db, meal_service, ingredient_service):
    ing = ingredient_service.create(
        Ingredient(name="rice", unit="gr", kcal=360, protein=7, carbs=78, fat=0.6, price=0.9)
    )
    entry = meal_service.register(
        make_entry("ingredient", ing.id, 200, "10-05-2026", unit="gr")
    )

    meal_service.delete(entry.id)

    assert MealEntryModel.select().count() == 0
    with pytest.raises(ValueError, match="not found"):
        meal_service.delete(entry.id)


def test_update_meal_entry(db, meal_service, ingredient_service):
    ing = ingredient_service.create(
        Ingredient(name="rice", unit="gr", kcal=360, protein=7, carbs=78, fat=0.6, price=0.9)
    )
    entry = meal_service.register(
        make_entry("ingredient", ing.id, 200, "10-05-2026", unit="gr")
    )

    updated = meal_service.update(entry.id, quantity=350)

    assert updated.id == entry.id
    assert updated.quantity == 350
    assert MealEntryModel.get_by_id(entry.id).quantity == 350
    with pytest.raises(ValueError, match="not found"):
        meal_service.update(999, quantity=1)