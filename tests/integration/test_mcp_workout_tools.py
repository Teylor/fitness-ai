"""Integration tests: MCP workout tools."""

from src.mcp.tools.workout_tools import (
    get_last_workout,
    get_personal_record,
    get_workouts_by_day,
    register_workout,
)


def test_register_workout_tool(db):
    res = register_workout(
        exercises=[
            {
                "name": "Bench Press",
                "sets": [
                    {"set_number": 1, "reps": 10, "weight": 80},
                    {"set_number": 2, "reps": 8, "weight": 85},
                ],
            },
            {"name": "Plank", "sets": [{"set_number": 1, "duration": 60}]},
        ],
        date="15-05-2026",
        notes="push day",
    )
    assert res["status"] == "ok"
    assert res["session"]["id"] is not None
    assert res["session"]["date"] == "15-05-2026"
    assert res["session"]["notes"] == "push day"
    assert len(res["sets"]) == 3
    assert res["new_prs"][0]["exercise"] == "Bench Press"
    assert set(res["auto_created"]) == {"Bench Press", "Plank"}


def test_register_workout_missing_weight_error(db):
    res = register_workout(
        exercises=[
            {"name": "Bench Press", "sets": [{"set_number": 1, "reps": 10}]}
        ],
        date="15-05-2026",
    )
    assert res["status"] == "error"
    assert res["code"] == "invalid_input"


def test_register_workout_invalid_date_error(db):
    res = register_workout(
        exercises=[
            {
                "name": "Bench Press",
                "sets": [{"set_number": 1, "reps": 10, "weight": 80}],
            }
        ],
        date="2026-05-15",
    )
    assert res["status"] == "error"
    assert res["code"] == "invalid_input"


def test_get_last_workout_tool(db):
    register_workout(
        exercises=[
            {
                "name": "Bench Press",
                "sets": [{"set_number": 1, "reps": 10, "weight": 80}],
            }
        ],
        date="10-05-2026",
    )
    register_workout(
        exercises=[
            {
                "name": "Bench Press",
                "sets": [{"set_number": 1, "reps": 8, "weight": 85}],
            }
        ],
        date="15-05-2026",
    )
    res = get_last_workout("bench press")
    assert res["status"] == "ok"
    assert res["exercise"] == "Bench Press"
    assert res["date"] == "15-05-2026"
    assert res["sets"][0]["weight"] == 85


def test_get_last_workout_not_found(db):
    res = get_last_workout("Ghost Press")
    assert res["status"] == "error"
    assert res["code"] == "not_found"


def test_get_personal_record_tool(db):
    register_workout(
        exercises=[
            {
                "name": "Bench Press",
                "sets": [{"set_number": 1, "reps": 3, "weight": 40}],
            }
        ],
        date="15-05-2026",
    )
    res = get_personal_record("Bench Press")
    assert res["status"] == "ok"
    pr = res["personal_record"]
    assert pr["max_weight"] == 40
    assert pr["max_reps"] == 3
    assert pr["estimated_1rm"] == 44.0
    assert pr["date"] == "15-05-2026"


def test_get_personal_record_not_found(db):
    res = get_personal_record("Bench Press")
    assert res["status"] == "error"
    assert res["code"] == "not_found"


def test_get_workouts_by_day_tool(db):
    register_workout(
        exercises=[
            {
                "name": "Bench Press",
                "sets": [{"set_number": 1, "reps": 10, "weight": 80}],
            }
        ],
        date="15-05-2026",
    )
    register_workout(
        exercises=[{"name": "Plank", "sets": [{"set_number": 1, "duration": 60}]}],
        date="16-05-2026",
    )
    res = get_workouts_by_day("15-05-2026")
    assert res["status"] == "ok"
    assert res["count"] == 1
    assert res["sessions"][0]["date"] == "15-05-2026"
    assert res["sessions"][0]["sets"][0]["exercise"] == "Bench Press"
    assert res["sessions"][0]["sets"][0]["estimated_1rm"] == 106.7

    empty = get_workouts_by_day("14-05-2026")
    assert empty["status"] == "ok"
    assert empty["count"] == 0


def test_get_workouts_by_day_invalid_date(db):
    res = get_workouts_by_day("2026-05-15")
    assert res["status"] == "error"
    assert res["code"] == "invalid_input"
