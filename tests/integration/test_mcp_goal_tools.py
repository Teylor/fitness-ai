"""Integration tests: MCP goal tools."""

from src.mcp.tools.goal_tools import get_daily_goal, set_daily_goal, toggle_day_off


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


def test_day_off_goal_tools_flow(db):
    set_daily_goal(
        kcal=2600.0,
        protein=185.0,
        carbs=300.0,
        fat=75.0,
        default=True,
    )
    off_def = set_daily_goal(
        kcal=2100.0,
        protein=185.0,
        carbs=175.0,
        fat=75.0,
        day_off_default=True,
    )
    assert off_def["status"] == "ok"
    assert off_def["goal"]["is_day_off_default"] is True
    assert off_def["profiles"]["training_default"]["kcal"] == 2600.0
    assert off_def["profiles"]["day_off_default"]["kcal"] == 2100.0

    # Toggle Day Off ON for 23-05-2026
    toggled_on = toggle_day_off(date="23-05-2026", is_day_off=True)
    assert toggled_on["status"] == "ok"
    assert toggled_on["is_day_off"] is True
    assert toggled_on["goal"]["kcal"] == 2100.0

    # Toggle Day Off OFF (flip) -> reverts to 2600.0
    toggled_off = toggle_day_off(date="23-05-2026")
    assert toggled_off["status"] == "ok"
    assert toggled_off["is_day_off"] is False
    assert toggled_off["goal"]["kcal"] == 2600.0

