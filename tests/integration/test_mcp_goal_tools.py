"""Integration tests: MCP goal tools."""

from src.mcp.tools.goal_tools import get_daily_goal, set_daily_goal


def test_set_daily_goal_tool(db):
    res = set_daily_goal(
        kcal=2000.0,
        protein=150.0,
        carbs=200.0,
        fat=60.0,
        date="15-05-2026",
    )
    assert res["status"] == "ok"
    assert res["goal"]["kcal"] == 2000.0
    assert res["goal"]["date"] == "15-05-2026"

    # Default goal flag
    res_def = set_daily_goal(
        kcal=2200.0,
        protein=160.0,
        carbs=220.0,
        fat=70.0,
        default=True,
    )
    assert res_def["status"] == "ok"
    assert res_def["goal"]["is_default"] is True


def test_get_daily_goal_tool(db):
    set_daily_goal(
        kcal=2100.0,
        protein=155.0,
        carbs=210.0,
        fat=65.0,
        date="16-05-2026",
    )
    res = get_daily_goal(date="16-05-2026")
    assert res["status"] == "ok"
    assert res["goal"]["kcal"] == 2100.0
    assert res["goal"]["date"] == "16-05-2026"


def test_get_daily_goal_fallback(db):
    # Fallback to default
    set_daily_goal(
        kcal=1800.0,
        protein=140.0,
        carbs=180.0,
        fat=50.0,
        default=True,
    )
    res_default = get_daily_goal(date="25-05-2026")
    assert res_default["status"] == "ok"
    assert res_default["goal"]["kcal"] == 1800.0

    # Fallback to closest previous dated goal
    set_daily_goal(
        kcal=1950.0,
        protein=145.0,
        carbs=190.0,
        fat=55.0,
        date="20-05-2026",
    )
    res_inherited = get_daily_goal(date="22-05-2026")
    assert res_inherited["status"] == "ok"
    assert res_inherited["goal"]["kcal"] == 1950.0
