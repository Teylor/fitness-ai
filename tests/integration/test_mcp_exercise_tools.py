"""Integration tests: MCP exercise tools."""

from src.mcp.tools.exercise_tools import (
    create_exercise,
    list_exercises,
    update_exercise,
)


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


def test_update_exercise_tool(db):
    created = create_exercise(name="Bench Press", muscle_group="chest")
    res = update_exercise(
        exercise_id=created["exercise"]["id"], muscle_group="pecho", type="time"
    )
    assert res["status"] == "ok"
    assert res["exercise"]["muscle_group"] == "pecho"
    assert res["exercise"]["type"] == "time"
    assert res["exercise"]["id"] == created["exercise"]["id"]


def test_update_exercise_unknown_id_error(db):
    res = update_exercise(exercise_id=999, muscle_group="chest")
    assert res["status"] == "error"
    assert res["code"] == "invalid_input"


def test_update_exercise_invalid_type_error(db):
    created = create_exercise(name="Bench Press")
    res = update_exercise(exercise_id=created["exercise"]["id"], type="distance_m")
    assert res["status"] == "error"
    assert res["code"] == "invalid_input"


def test_list_exercises_with_prs(db):
    from src.mcp.tools.workout_tools import register_workout

    create_exercise(name="Overhead Press", muscle_group="shoulders")
    create_exercise(name="Plank", muscle_group="core", type="time")

    # Log workout with sets: 20kg x 10, 22kg x 6, 18kg x 12
    register_workout(
        date="15-05-2026",
        exercises=[
            {
                "name": "Overhead Press",
                "sets": [
                    {"set_number": 1, "reps": 10, "weight": 20},
                    {"set_number": 2, "reps": 6, "weight": 22},
                    {"set_number": 3, "reps": 12, "weight": 18},
                ],
            }
        ],
    )

    # When include_prs is False (default)
    res_default = list_exercises(search="Overhead Press")
    assert "pr" not in res_default["exercises"][0]

    # When include_prs is True (or "true")
    res_prs = list_exercises(include_prs=True)
    ohp = next(x for x in res_prs["exercises"] if x["name"] == "Overhead Press")
    assert ohp["pr"] is not None
    assert ohp["pr"]["max_weight"] == 22.0
    assert ohp["pr"]["max_weight_reps"] == 6
    assert ohp["pr"]["estimated_1rm"] == 26.7

    plank = next(x for x in res_prs["exercises"] if x["name"] == "Plank")
    assert plank["pr"] is None

