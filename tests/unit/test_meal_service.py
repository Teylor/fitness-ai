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
from src.utils.errors import NotFoundError, ValidationError


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
    # 0.18 (rice) + 1.25 (3L daily water) = 1.43
    assert summary["spend"] == 1.43
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
    assert summary["water_and_supplements"]["water"]["quantity"] == 3.0
    assert summary["water_and_supplements"]["water"]["price"] == 1.25


def test_get_day_summary_no_goal_uses_default(db, meal_service, goal_service):
    goal_service.set_default(
        DailyGoal(date="01-01-2026", kcal=2000, protein=130, carbs=230, fat=65)
    )

    summary = meal_service.get_day_summary("10-05-2026")

    assert summary["consumed"] == {"kcal": 0, "protein": 0, "carbs": 0, "fat": 0}
    assert summary["spend"] == 1.25
    assert summary["goal"]["kcal"] == 2000
    assert summary["remaining"]["kcal"] == 2000
    assert summary["meals"] == []
    assert summary["water_and_supplements"]["spend"] == 1.25


def test_delete_meal_entry(db, meal_service, ingredient_service):
    ing = ingredient_service.create(
        Ingredient(name="rice", unit="gr", kcal=360, protein=7, carbs=78, fat=0.6, price=0.9)
    )
    entry = meal_service.register(
        make_entry("ingredient", ing.id, 200, "10-05-2026", unit="gr")
    )

    meal_service.delete(entry.id)

    assert MealEntryModel.select().count() == 0
    with pytest.raises(NotFoundError) as exc_info:
        meal_service.delete(entry.id)
    assert exc_info.value.code == "not_found"


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
    with pytest.raises(NotFoundError) as exc_info:
        meal_service.update(999, quantity=1)
    assert exc_info.value.code == "not_found"


def test_register_meal_with_meal_type_and_validation(db, meal_service, ingredient_service):
    ing = ingredient_service.create(
        Ingredient(name="oats", unit="gr", kcal=389, protein=16.9, carbs=66.3, fat=6.9)
    )

    # 1. Default meal_type is tentempie
    entry1 = meal_service.register(
        MealEntry(date="10-05-2026", item_type="ingredient", item_id=ing.id, quantity=50, unit="gr")
    )
    assert entry1.meal_type == "tentempie"

    # 2. Explicit meal_type (desayuno)
    entry2 = meal_service.register(
        MealEntry(date="10-05-2026", item_type="ingredient", item_id=ing.id, quantity=80, unit="gr", meal_type="desayuno")
    )
    assert entry2.meal_type == "desayuno"

    # 3. Invalid meal_type raises ValidationError
    with pytest.raises(ValidationError) as exc:
        meal_service.register(
            MealEntry(date="10-05-2026", item_type="ingredient", item_id=ing.id, quantity=80, unit="gr", meal_type="invalid_type")
        )
    assert "invalid meal_type" in str(exc.value)


def test_get_day_summary_groups_by_meal_type(db, meal_service, ingredient_service):
    from src.services.goal_service import GoalService

    GoalService().set_default(
        DailyGoal(date="01-01-2026", kcal=2000, protein=150, carbs=200, fat=60)
    )
    ing = ingredient_service.create(
        Ingredient(name="banana", unit="u", kcal=105, protein=1.3, carbs=27, fat=0.3, price=0.4)
    )

    meal_service.register(
        MealEntry(date="15-05-2026", item_type="ingredient", item_id=ing.id, quantity=1, unit="u", meal_type="desayuno")
    )
    meal_service.register(
        MealEntry(date="15-05-2026", item_type="ingredient", item_id=ing.id, quantity=2, unit="u", meal_type="comida")
    )
    meal_service.register(
        MealEntry(date="15-05-2026", item_type="ingredient", item_id=ing.id, quantity=1, unit="u", meal_type="tentempie")
    )

    summary = meal_service.get_day_summary("15-05-2026")
    assert summary["consumed"]["kcal"] == 420.0
    assert "meals_by_type" in summary

    by_type = summary["meals_by_type"]
    assert len(by_type["desayuno"]["meals"]) == 1
    assert by_type["desayuno"]["kcal"] == 105.0

    assert len(by_type["comida"]["meals"]) == 1
    assert by_type["comida"]["kcal"] == 210.0

    assert len(by_type["tentempie"]["meals"]) == 1
    assert by_type["tentempie"]["kcal"] == 105.0

    assert len(by_type["cena"]["meals"]) == 0
    assert by_type["cena"]["kcal"] == 0.0


def test_get_day_summary_separates_supplements_and_includes_daily_water(
    db, meal_service, ingredient_service
):
    from src.services.goal_service import GoalService

    GoalService().set_default(
        DailyGoal(date="01-01-2026", kcal=2000, protein=150, carbs=200, fat=60)
    )
    banana = ingredient_service.create(
        Ingredient(name="banana", unit="u", kcal=105, protein=1.3, carbs=27, fat=0.3, price=0.4)
    )
    creatine = ingredient_service.create(
        Ingredient(
            name="Creatina",
            unit="gr",
            kcal=0,
            protein=0,
            carbs=0,
            fat=0,
            price=30.0,  # per 1kg -> 5g = 0.15€
            is_supplement=True,
        )
    )
    omega3 = ingredient_service.create(
        Ingredient(
            name="Omega 3",
            unit="u",
            kcal=18,
            protein=0,
            carbs=0,
            fat=2.0,
            price=0.20,
            is_supplement=True,
        )
    )

    meal_service.register(
        MealEntry(
            date="16-05-2026",
            item_type="ingredient",
            item_id=banana.id,
            quantity=1,
            unit="u",
            meal_type="desayuno",
        )
    )
    meal_service.register(
        MealEntry(
            date="16-05-2026",
            item_type="ingredient",
            item_id=creatine.id,
            quantity=5,
            unit="gr",
            meal_type="desayuno",
        )
    )
    meal_service.register(
        MealEntry(
            date="16-05-2026",
            item_type="ingredient",
            item_id=omega3.id,
            quantity=2,
            unit="u",
            meal_type="comida",
        )
    )

    summary = meal_service.get_day_summary("16-05-2026")
    # Consumed includes banana (105 kcal, 0.3g fat) + 2x Omega 3 (36 kcal, 4g fat)
    assert summary["consumed"]["kcal"] == 141.0
    assert summary["consumed"]["fat"] == 4.3

    # Regular meals_by_type only contains banana (supplements excluded)
    assert len(summary["meals_by_type"]["desayuno"]["meals"]) == 1
    assert summary["meals_by_type"]["desayuno"]["meals"][0]["name"] == "banana"
    assert len(summary["meals_by_type"]["comida"]["meals"]) == 0

    # Water and supplements section contains 3L water @ 1.25€ + Creatina + Omega 3
    ws = summary["water_and_supplements"]
    assert ws["water"]["quantity"] == 3.0
    assert ws["water"]["price"] == 1.25
    assert len(ws["supplements"]) == 2
    assert {s["name"] for s in ws["supplements"]} == {"Creatina", "Omega 3"}
    assert ws["kcal"] == 36.0
    assert ws["fat"] == 4.0
    # 1.25 (water) + 0.15 (5g creatine) + 0.40 (2x omega3) = 1.80
    assert ws["spend"] == 1.80

    # Total daily spend = 0.40 (banana) + 1.80 (water + supplements) = 2.20
    assert summary["spend"] == 2.20

