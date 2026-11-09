"""Integration tests: MCP meal tools."""

from src.models.daily_goal import DailyGoal
from src.mcp.tools.ingredient_tools import create_ingredient
from src.mcp.tools.meal_tools import get_day_summary, register_meal
from src.services.goal_service import GoalService
from src.services.ingredient_service import IngredientService


def test_register_meal_tool_returns_json(db):
    GoalService().set_default(
        DailyGoal(date="01-01-2026", kcal=2000, protein=150, carbs=200, fat=60)
    )
    create_ingredient(
        name="Chicken Breast",
        unit="gr",
        kcal=165.0,
        protein=31.0,
        carbs=0.0,
        fat=3.6,
        price=1.2,
    )

    res = register_meal(
        item_name="Chicken Breast",
        quantity=200,
        unit="gr",
        date="10-05-2026",
    )
    assert res["status"] == "ok"
    assert res["entry_id"] is not None
    assert res["macros"]["protein"] == 62.0
    assert res["macros"]["kcal"] == 330.0
    assert res["day_summary"] is not None


def test_register_meal_tool_creates_provisional(db):
    res = register_meal(
        item_name="Mystery Food",
        quantity=50,
        unit="gr",
        date="10-05-2026",
    )
    assert res["status"] == "ok"
    assert res["entry_id"] is not None

    ing = IngredientService().find_by_name("Mystery Food")
    assert ing is not None
    assert ing.provisional is True


def test_get_day_summary_tool(db):
    GoalService().set_default(
        DailyGoal(date="01-01-2026", kcal=2000, protein=150, carbs=200, fat=60)
    )
    create_ingredient(name="Apple", unit="u", kcal=95.0, carbs=25.0, price=0.5)
    register_meal(item_name="Apple", quantity=1, unit="u", date="12-05-2026")

    res = get_day_summary(date="12-05-2026")
    assert res["status"] == "ok"
    assert res["consumed"]["kcal"] == 95.0
    assert "goal" in res
    assert "remaining" in res
    assert len(res["meals"]) == 1
