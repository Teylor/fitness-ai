"""Tests: RecipeService."""

import pytest

from src.models.ingredient import Ingredient
from src.models.recipe import Recipe, RecipeItem
from src.utils.errors import DuplicateError, NotFoundError


def _mk_ingredient(service, name, unit="gr", kcal=100.0, protein=10.0, carbs=80.0, fat=0.0, price=1.0):
    return service.create(Ingredient(name=name, unit=unit, kcal=kcal, protein=protein,
                                     carbs=carbs, fat=fat, price=price))


def test_create_recipe_compound(db, recipe_service, ingredient_service):
    flour = _mk_ingredient(ingredient_service, "Flour")
    water = _mk_ingredient(ingredient_service, "Water", unit="ml")
    r = recipe_service.create(
        Recipe(name="Bread", price=None),
        items=[RecipeItem(ingredient_id=flour.id, quantity=200, unit="gr"),
               RecipeItem(ingredient_id=water.id, quantity=150, unit="ml")],
    )
    assert r.id is not None
    # 200g flour (kcal 100/100g) + 150ml water (kcal 100/100ml)
    assert r.kcal == 200 + 150
    assert r.protein == 20 + 15
    assert r.carbs == 160 + 120
    assert r.price == 0.35
    assert r.items[0].name == "Flour"
    assert r.items[1].name == "Water"


def test_create_recipe_opaque(db, recipe_service):
    r = recipe_service.create(
        Recipe(name="Takeaway", price=5.5, kcal=800, protein=30, carbs=90, fat=25),
    )
    assert r.id is not None
    assert r.price == 5.5
    assert r.kcal == 800
    assert r.protein == 30
    # opaque: no items, no recomputation
    assert recipe_service.calculate_macros(r.id)["kcal"] == 800


def test_calculate_macros_compound(db, recipe_service, ingredient_service):
    egg = _mk_ingredient(ingredient_service, "Egg", unit="u",
                         kcal=78, protein=6.3, carbs=0.4, fat=5.3, price=0.2)
    r = recipe_service.create(
        Recipe(name="Omelette"),
        items=[RecipeItem(ingredient_id=egg.id, quantity=2, unit="u")],
    )
    m = recipe_service.calculate_macros(r.id)
    # 2 units: kcal 78*2, protein 6.3*2, carbs 0.4*2, fat 5.3*2, price 0.2*2
    assert m["kcal"] == 156
    assert m["protein"] == 12.6
    assert m["carbs"] == 0.8
    assert m["fat"] == 10.6
    assert m["price"] == 0.4


def test_update_recipe_replaces_items(db, recipe_service, ingredient_service):
    egg = _mk_ingredient(ingredient_service, "Egg", unit="u",
                         kcal=78, protein=6.3, carbs=0.4, fat=5.3, price=0.2)
    milk = _mk_ingredient(ingredient_service, "Milk", unit="ml",
                          kcal=42, protein=3.3, carbs=4.8, fat=1, price=0.9)
    r = recipe_service.create(
        Recipe(name="Eggs"),
        items=[RecipeItem(ingredient_id=egg.id, quantity=3, unit="u")],
    )
    # update: cambia name y reemplaza items (1 milk 250ml)
    updated = recipe_service.update(
        r.id, name="Milk eggs",
        items=[RecipeItem(ingredient_id=milk.id, quantity=250, unit="ml")],
    )
    assert updated.name == "Milk eggs"
    # macros recomputed from milk only (egg no longer counts)
    assert updated.kcal == 42 * 2.5
    assert updated.price == round(0.9 * 0.25, 2)
    # the old egg item must have been removed
    assert recipe_service.calculate_macros(updated.id)["protein"] == round(3.3 * 2.5, 2)


def test_delete_recipe_cascades(db, recipe_service, ingredient_service):
    from src.db.models import MealEntry
    egg = _mk_ingredient(ingredient_service, "Egg", unit="u")
    r = recipe_service.create(
        Recipe(name="Scrambled"),
        items=[RecipeItem(ingredient_id=egg.id, quantity=2, unit="u")],
    )
    # two meal entries pointing at the recipe
    MealEntry.create(date="01-01-2026", item_type="recipe", item_id=r.id,
                     quantity=1, unit="u")
    MealEntry.create(date="02-01-2026", item_type="recipe", item_id=r.id,
                     quantity=1, unit="u")
    deleted = recipe_service.delete(r.id)
    # returns the number of meal entries deleted
    assert deleted == 2
    assert recipe_service.get_by_id(r.id) is None


def test_list_recipes_by_type(db, recipe_service, ingredient_service):
    egg = _mk_ingredient(ingredient_service, "Egg", unit="u")
    recipe_service.create(
        Recipe(name="Compound A"),
        items=[RecipeItem(ingredient_id=egg.id, quantity=1, unit="u")],
    )
    recipe_service.create(Recipe(name="Compound B"),
                          items=[RecipeItem(ingredient_id=egg.id, quantity=2, unit="u")])
    recipe_service.create(Recipe(name="Opaque A", price=1.0, kcal=100))
    recipe_service.create(Recipe(name="Opaque B", price=2.0, kcal=200))
    compounds = recipe_service.list(type="compound")
    opaque = recipe_service.list(type="opaque")
    assert {r.name for r in compounds} == {"Compound A", "Compound B"}
    assert {r.name for r in opaque} == {"Opaque A", "Opaque B"}


def test_create_recipe_duplicate_raises(db, recipe_service):
    recipe_service.create(Recipe(name="Pancake"))
    with pytest.raises(DuplicateError) as exc_info:
        recipe_service.create(Recipe(name="Pancake"))
    assert exc_info.value.code == "duplicate"
    assert isinstance(exc_info.value, ValueError)


def test_update_recipe_not_found_raises(db, recipe_service):
    with pytest.raises(NotFoundError) as exc_info:
        recipe_service.update(999, name="Missing")
    assert exc_info.value.code == "not_found"


def test_update_recipe_duplicate_raises(db, recipe_service):
    a = recipe_service.create(Recipe(name="Soup"))
    b = recipe_service.create(Recipe(name="Salad"))
    with pytest.raises(DuplicateError) as exc_info:
        recipe_service.update(b.id, name="Soup")
    assert exc_info.value.code == "duplicate"


def test_delete_recipe_not_found_raises(db, recipe_service):
    with pytest.raises(NotFoundError) as exc_info:
        recipe_service.delete(999)
    assert exc_info.value.code == "not_found"


def test_calculate_macros_not_found_raises(db, recipe_service):
    with pytest.raises(NotFoundError) as exc_info:
        recipe_service.calculate_macros(999)
    assert exc_info.value.code == "not_found"
