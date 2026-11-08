"""Integration tests: MCP ingredient tools."""

from src.mcp.tools.ingredient_tools import (
    create_ingredient,
    delete_ingredient,
    list_ingredients,
    update_ingredient,
)


def test_create_ingredient_tool(db):
    res = create_ingredient(
        name="Chicken Breast",
        unit="gr",
        kcal=165.0,
        protein=31.0,
        carbs=0.0,
        fat=3.6,
        price=1.2,
    )
    assert res["status"] == "ok"
    assert res["ingredient"]["name"] == "Chicken Breast"
    assert res["ingredient"]["unit"] == "gr"
    assert res["ingredient"]["id"] is not None

    invalid = create_ingredient(name="Bad Unit", unit="kg")
    assert invalid["status"] == "error"
    assert invalid["code"] == "invalid_input"


def test_create_ingredient_tool_duplicate(db):
    res1 = create_ingredient(name="Oats", unit="gr", kcal=389.0)
    assert res1["status"] == "ok"
    orig_id = res1["ingredient"]["id"]

    res2 = create_ingredient(name="OATS", unit="gr", kcal=400.0)
    assert res2["status"] == "ok"
    assert res2["ingredient"]["id"] == orig_id


def test_update_ingredient_tool(db):
    created = create_ingredient(name="Milk", unit="ml", kcal=42.0, price=0.8)
    assert created["status"] == "ok"
    ing_id = created["ingredient"]["id"]

    updated = update_ingredient(ingredient_id=ing_id, kcal=50.0, price=1.0)
    assert updated["status"] == "ok"
    assert updated["ingredient"]["kcal"] == 50.0
    assert updated["ingredient"]["price"] == 1.0

    not_found = update_ingredient(ingredient_id=9999, name="Ghost")
    assert not_found["status"] == "error"
    assert not_found["code"] == "not_found"


def test_delete_ingredient_tool(db):
    created = create_ingredient(name="Butter", unit="gr", kcal=717.0)
    ing_id = created["ingredient"]["id"]

    deleted = delete_ingredient(ingredient_id=ing_id)
    assert deleted["status"] == "ok"
    assert deleted["ingredient_id"] == ing_id
    assert deleted["deleted_entries"] == 0

    deleted_again = delete_ingredient(ingredient_id=ing_id)
    assert deleted_again["status"] == "error"
    assert deleted_again["code"] == "not_found"


def test_list_ingredients_tool_search(db):
    create_ingredient(name="White Rice", unit="gr")
    create_ingredient(name="Brown Rice", unit="gr")
    create_ingredient(name="Eggs", unit="u")

    listed = list_ingredients(search="rice")
    assert listed["status"] == "ok"
    assert len(listed["ingredients"]) == 2
    assert all("rice" in i["name"].lower() for i in listed["ingredients"])
