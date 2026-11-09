"""Integration tests: MCP exercise tools."""

from src.mcp.tools.exercise_tools import create_exercise, list_exercises


def test_create_exercise_tool(db):
    res = create_exercise(name="Squat", muscle_group="legs")
    assert res["status"] == "ok"
    assert res["exercise"]["name"] == "Squat"
    assert res["exercise"]["muscle_group"] == "legs"
    assert res["exercise"]["type"] == "weight_reps"
    assert res["exercise"]["id"] is not None


def test_create_exercise_idempotent(db):
    res1 = create_exercise(name="Squat")
    res2 = create_exercise(name="SQUAT")
    assert res2["status"] == "ok"
    assert res2["exercise"]["id"] == res1["exercise"]["id"]


def test_create_exercise_invalid_type_error(db):
    res = create_exercise(name="Bad Type", type="distance_m")
    assert res["status"] == "error"
    assert res["code"] == "invalid_input"


def test_create_exercise_empty_name_error(db):
    res = create_exercise(name="   ")
    assert res["status"] == "error"
    assert res["code"] == "invalid_input"


def test_list_exercises_tool(db):
    create_exercise(name="Bench Press", muscle_group="chest")
    create_exercise(name="Squat", muscle_group="legs")

    listed = list_exercises()
    assert listed["status"] == "ok"
    assert listed["count"] == 2

    searched = list_exercises(search="bench")
    assert searched["count"] == 1
    assert searched["exercises"][0]["name"] == "Bench Press"

    filtered = list_exercises(muscle_group="legs")
    assert filtered["count"] == 1
    assert filtered["exercises"][0]["name"] == "Squat"

    page = list_exercises(limit=1, offset=1)
    assert page["count"] == 1
    assert page["exercises"][0]["name"] == "Squat"
