"""Integration tests: MCP recipe tools."""

from src.mcp.tools.ingredient_tools import create_ingredient
from src.mcp.tools.recipe_tools import (
    create_recipe,
    delete_recipe,
    list_recipes,
    update_recipe,
)


def test_create_recipe_compound_tool(db):
    create_ingredient(name="Flour", unit="gr", kcal=364.0, protein=10.0, carbs=76.0, fat=1.0, price=0.001)
    create_ingredient(name="Sugar", unit="gr", kcal=387.0, protein=0.0, carbs=100.0, fat=0.0, price=0.002)

    res = create_recipe(
        name="Pancake",
        ingredients=[
            {"name": "Flour", "quantity": 100, "unit": "gr"},
            {"name": "Sugar", "quantity": 50, "unit": "gr"},
        ],
    )
    assert res["status"] == "ok"
    assert res["recipe"]["id"] is not None
    assert len(res["recipe"]["items"]) == 2
    assert res["recipe"]["kcal"] > 0
    orig_id = res["recipe"]["id"]

    dup = create_recipe(name="Pancake", price=5.0)
    assert dup["status"] == "ok"
    assert dup["recipe"]["id"] == orig_id


def test_create_recipe_opaque_tool(db):
    res = create_recipe(
        name="Protein Shake",
        price=3.5,
        kcal=250.0,
        protein=30.0,
        carbs=10.0,
        fat=3.0,
    )
    assert res["status"] == "ok"
    assert res["recipe"]["price"] == 3.5
    assert res["recipe"]["kcal"] == 250.0
    assert len(res["recipe"]["items"]) == 0


def test_update_recipe_tool(db):
    res = create_recipe(name="Coffee", price=1.5, kcal=5.0)
    rec_id = res["recipe"]["id"]

    updated = update_recipe(recipe_id=rec_id, price=2.0)
    assert updated["status"] == "ok"
    assert updated["recipe"]["price"] == 2.0

    not_found = update_recipe(recipe_id=9999, name="Missing")
    assert not_found["status"] == "error"
    assert not_found["code"] == "not_found"


def test_delete_recipe_tool(db):
    res = create_recipe(name="Snack", price=1.0, kcal=100.0)
    rec_id = res["recipe"]["id"]

    deleted = delete_recipe(recipe_id=rec_id)
    assert deleted["status"] == "ok"
    assert deleted["recipe_id"] == rec_id
    assert deleted["deleted_entries"] == 0

    deleted_again = delete_recipe(recipe_id=rec_id)
    assert deleted_again["status"] == "error"
    assert deleted_again["code"] == "not_found"


def test_list_recipes_tool(db):
    create_ingredient(name="Egg", unit="u", kcal=70.0, protein=6.0, carbs=0.5, fat=5.0, price=0.3)
    create_recipe(
        name="Omelette",
        ingredients=[{"name": "Egg", "quantity": 2, "unit": "u"}],
    )
    create_recipe(name="Store Bar", price=2.5, kcal=200.0)

    compounds = list_recipes(type="compound")
    assert compounds["status"] == "ok"
    assert any(r["name"] == "Omelette" for r in compounds["recipes"])

    filtered = list_recipes(search="Omelette")
    assert filtered["status"] == "ok"
    assert len(filtered["recipes"]) == 1
    assert filtered["recipes"][0]["name"] == "Omelette"
