"""Tests: IngredientService."""

import pytest

from src.db.models import MealEntry, Recipe, RecipeItem
from src.models.ingredient import Ingredient


def test_create_ingredient(db, ingredient_service):
    created = ingredient_service.create(
        Ingredient(name="Chicken", unit="gr", kcal=165, protein=31, carbs=0, fat=3.6, price=1200)
    )
    assert created.id is not None
    assert created.name == "Chicken"
    assert created.unit == "gr"
    assert created.kcal == 165
    assert created.protein == 31
    assert created.carbs == 0
    assert created.fat == 3.6
    assert created.price == 1200
    assert created.provisional is False

    stored = ingredient_service.get_by_id(created.id)
    assert stored is not None
    assert stored.name == "Chicken"
    assert stored.unit == "gr"
    assert stored.kcal == 165
    assert stored.price == 1200


def test_create_ingredient_duplicate_raises(db, ingredient_service):
    ingredient_service.create(Ingredient(name="Chicken", unit="gr"))
    with pytest.raises(ValueError):
        ingredient_service.create(Ingredient(name="Chicken", unit="gr"))


def test_create_ingredient_duplicate_case_accent_insensitive(db, ingredient_service):
    ingredient_service.create(Ingredient(name="Aguacate", unit="gr"))
    with pytest.raises(ValueError):
        ingredient_service.create(Ingredient(name="AGUACATE", unit="gr"))
    ingredient_service.create(Ingredient(name="Cafe", unit="u"))
    with pytest.raises(ValueError):
        ingredient_service.create(Ingredient(name="CAFÉ", unit="u"))


def test_create_ingredient_same_name_different_unit_ok(db, ingredient_service):
    a = ingredient_service.create(Ingredient(name="Water", unit="ml"))
    b = ingredient_service.create(Ingredient(name="Water", unit="gr"))
    assert a.id != b.id


def test_create_ingredient_invalid_unit_raises(db, ingredient_service):
    with pytest.raises(ValueError):
        ingredient_service.create(Ingredient(name="X", unit="kg"))


def test_get_by_id_not_found_returns_none(db, ingredient_service):
    assert ingredient_service.get_by_id(999) is None


def test_find_by_name_fuzzy(db, ingredient_service):
    ingredient_service.create(Ingredient(name="Chicken Breast", unit="gr"))
    found = ingredient_service.find_by_name("chiken breast")
    assert found is not None
    assert found.name == "Chicken Breast"

    exact = ingredient_service.find_by_name("chicken breast")
    assert exact is not None
    assert exact.name == "Chicken Breast"


def test_find_by_name_no_match_returns_none(db, ingredient_service):
    ingredient_service.create(Ingredient(name="Chicken Breast", unit="gr"))
    assert ingredient_service.find_by_name("zzz") is None


def test_update_ingredient(db, ingredient_service):
    created = ingredient_service.create(Ingredient(name="Rice", unit="gr", price=800))
    updated = ingredient_service.update(created.id, price=950, provisional=True)
    assert updated.id == created.id
    assert updated.price == 950
    assert updated.provisional is True
    assert updated.name == "Rice"

    reloaded = ingredient_service.get_by_id(created.id)
    assert reloaded.price == 950
    assert reloaded.provisional is True


def test_update_ingredient_not_found_raises(db, ingredient_service):
    with pytest.raises(ValueError):
        ingredient_service.update(999, name="X")


def test_update_ingredient_duplicate_raises(db, ingredient_service):
    a = ingredient_service.create(Ingredient(name="Eggs", unit="u"))
    b = ingredient_service.create(Ingredient(name="Milk", unit="u"))
    with pytest.raises(ValueError):
        ingredient_service.update(b.id, name="Eggs")


def test_delete_ingredient_cascades_meals(db, ingredient_service):
    created = ingredient_service.create(Ingredient(name="Oats", unit="gr"))
    for i in range(3):
        MealEntry.create(
            date="01-11-2026", item_type="ingredient", item_id=created.id,
            quantity=100 + i, unit="gr",
        )
    assert MealEntry.select().count() == 3

    deleted_count = ingredient_service.delete(created.id)
    assert deleted_count == 3
    assert MealEntry.select().count() == 0
    assert ingredient_service.get_by_id(created.id) is None


def test_delete_ingredient_not_found_raises(db, ingredient_service):
    with pytest.raises(ValueError):
        ingredient_service.delete(999)


def test_delete_ingredient_used_in_recipe_raises(db, ingredient_service):
    ing = ingredient_service.create(Ingredient(name="Flour", unit="gr"))
    recipe = Recipe.create(name="Bread")
    RecipeItem.create(recipe=recipe, ingredient=ing.id, quantity=500, unit="gr")
    with pytest.raises(ValueError):
        ingredient_service.delete(ing.id)


def test_list_ingredients_search(db, ingredient_service):
    ingredient_service.create(Ingredient(name="Chicken Breast", unit="gr"))
    ingredient_service.create(Ingredient(name="Chicken Thigh", unit="gr"))
    ingredient_service.create(Ingredient(name="Rice", unit="gr"))

    results = ingredient_service.list(search="chicken")
    assert len(results) == 2
    assert all("chicken" in r.name.lower() for r in results)


def test_list_ingredients_provisional_only(db, ingredient_service):
    ingredient_service.create(Ingredient(name="A", unit="gr", provisional=False))
    p = ingredient_service.create(Ingredient(name="B", unit="gr", provisional=True))
    ingredient_service.create(Ingredient(name="C", unit="gr", provisional=False))

    results = ingredient_service.list(provisional_only=True)
    assert len(results) == 1
    assert results[0].id == p.id


def test_list_ingredients_pagination(db, ingredient_service):
    for i in range(10):
        ingredient_service.create(Ingredient(name=f"Item {i}", unit="gr"))

    page = ingredient_service.list(limit=5, offset=2)
    assert len(page) == 5
    all_items = ingredient_service.list(limit=100)
    assert [x.id for x in page] == [x.id for x in all_items[2:7]]