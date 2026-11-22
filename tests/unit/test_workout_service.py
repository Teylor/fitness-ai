"""Tests: WorkoutService.register_session."""

from datetime import datetime

import pytest

from src.db.models import (
    Exercise as ExerciseModel,
    ExerciseSet as ExerciseSetModel,
    PersonalRecord as PersonalRecordModel,
    WorkoutSession as WorkoutSessionModel,
)
from src.models.exercise import Exercise
from src.models.workout_session import WorkoutSession
from src.utils.errors import ValidationError


@pytest.fixture
def exercises(exercise_service):
    """Bench Press (weight_reps), Plank (time), Run (distance)."""
    return {
        "Bench Press": exercise_service.create(Exercise(name="Bench Press")),
        "Plank": exercise_service.create(Exercise(name="Plank", type="time")),
        "Run": exercise_service.create(Exercise(name="Run", type="distance")),
    }


def test_register_session_basic(db, workout_service, exercises):
    exercises_input = [
        {
            "name": "Bench Press",
            "sets": [
                {"set_number": 1, "reps": 10, "weight": 80},
                {"set_number": 2, "reps": 8, "weight": 85},
            ],
        },
        {"name": "Plank", "sets": [{"set_number": 1, "duration": 60}]},
    ]
    result = workout_service.register_session(
        WorkoutSession(date="15-05-2026", notes="push day"), exercises_input
    )
    assert result["session"]["id"] is not None
    assert result["session"]["date"] == "15-05-2026"
    assert result["session"]["notes"] == "push day"
    assert len(result["sets"]) == 3
    assert result["auto_created"] == []

    assert WorkoutSessionModel.select().count() == 1
    assert ExerciseSetModel.select().count() == 3
    stored = WorkoutSessionModel.get()
    assert stored.date == datetime(2026, 5, 15, 0, 0)


def test_register_session_default_date_now(db, workout_service, exercises):
    workout_service.register_session(WorkoutSession(date=""), [
        {"name": "Bench Press", "sets": [{"set_number": 1, "reps": 5, "weight": 60}]}
    ])
    stored = WorkoutSessionModel.get()
    assert stored.date.year == datetime.now().year
    assert len(stored.date.strftime("%d-%m-%Y")) == 10


def test_register_session_date_with_time(db, workout_service, exercises):
    result = workout_service.register_session(
        WorkoutSession(date="15-05-2026 18:30"),
        [{"name": "Bench Press", "sets": [{"set_number": 1, "reps": 5, "weight": 60}]}],
    )
    stored = WorkoutSessionModel.get()
    assert (stored.date.hour, stored.date.minute) == (18, 30)
    assert result["session"]["date"] == "15-05-2026 18:30:00"


def test_register_session_invalid_date_raises(db, workout_service, exercises):
    with pytest.raises(ValidationError) as exc_info:
        workout_service.register_session(WorkoutSession(date="2026-05-15"), [
            {"name": "Bench Press", "sets": [{"set_number": 1, "reps": 5, "weight": 60}]}
        ])
    assert exc_info.value.code == "invalid_input"
    assert WorkoutSessionModel.select().count() == 0
    assert ExerciseSetModel.select().count() == 0


def test_register_session_auto_creates_exercises(db, workout_service):
    result = workout_service.register_session(WorkoutSession(date="15-05-2026"), [
        {"name": "Zombie Curl", "sets": [{"set_number": 1, "reps": 12, "weight": 10}]}
    ])
    assert result["auto_created"] == ["Zombie Curl"]
    row = ExerciseModel.get(ExerciseModel.name == "Zombie Curl")
    assert row.muscle_group == "unknown"
    assert row.type == "weight_reps"


def test_register_session_duplicate_set_number_raises(db, workout_service, exercises):
    with pytest.raises(ValidationError) as exc_info:
        workout_service.register_session(WorkoutSession(date="15-05-2026"), [
            {
                "name": "Bench Press",
                "sets": [
                    {"set_number": 1, "reps": 10, "weight": 80},
                    {"set_number": 1, "reps": 8, "weight": 85},
                ],
            }
        ])
    assert exc_info.value.code == "invalid_input"
    assert WorkoutSessionModel.select().count() == 0
    assert ExerciseSetModel.select().count() == 0


def test_register_session_missing_weight_raises(db, workout_service, exercises):
    with pytest.raises(ValidationError) as exc_info:
        workout_service.register_session(WorkoutSession(date="15-05-2026"), [
            {"name": "Bench Press", "sets": [{"set_number": 1, "reps": 10}]}
        ])
    assert exc_info.value.code == "invalid_input"
    assert WorkoutSessionModel.select().count() == 0
    assert ExerciseSetModel.select().count() == 0


def test_register_session_time_exercise_requires_duration(db, workout_service, exercises):
    with pytest.raises(ValidationError) as exc_info:
        workout_service.register_session(WorkoutSession(date="15-05-2026"), [
            {"name": "Plank", "sets": [{"set_number": 1, "reps": 1, "weight": 0}]}
        ])
    assert exc_info.value.code == "invalid_input"

    result = workout_service.register_session(WorkoutSession(date="16-05-2026"), [
        {"name": "Plank", "sets": [{"set_number": 1, "duration": 90}]}
    ])
    assert len(result["sets"]) == 1


def test_register_session_distance_exercise(db, workout_service, exercises):
    result = workout_service.register_session(WorkoutSession(date="16-05-2026"), [
        {"name": "Run", "sets": [{"set_number": 1, "distance": 5000}]}
    ])
    assert len(result["sets"]) == 1
    assert result["sets"][0]["distance"] == 5000


def test_pr_created_on_first_session(db, workout_service, exercises):
    workout_service.register_session(WorkoutSession(date="15-05-2026"), [
        {
            "name": "Bench Press",
            "sets": [
                {"set_number": 1, "reps": 5, "weight": 20},
                {"set_number": 2, "reps": 3, "weight": 40},
            ],
        }
    ])
    pr = PersonalRecordModel.get(PersonalRecordModel.exercise == exercises["Bench Press"].id)
    assert pr.max_weight == 40
    assert pr.max_reps == 3
    assert pr.estimated_1rm == 44.0
    assert pr.date == "15-05-2026"


def test_pr_updated_when_better(db, workout_service, exercises):
    workout_service.register_session(WorkoutSession(date="15-05-2026"), [
        {"name": "Bench Press", "sets": [{"set_number": 1, "reps": 3, "weight": 40}]}
    ])
    result = workout_service.register_session(WorkoutSession(date="20-05-2026"), [
        {"name": "Bench Press", "sets": [{"set_number": 1, "reps": 2, "weight": 45}]}
    ])
    pr = PersonalRecordModel.get()
    assert pr.max_weight == 45
    assert pr.max_reps == 2
    assert pr.estimated_1rm == 48.0
    assert pr.date == "20-05-2026"
    assert len(result["new_prs"]) == 1


def test_pr_not_updated_when_worse(db, workout_service, exercises):
    workout_service.register_session(WorkoutSession(date="15-05-2026"), [
        {"name": "Bench Press", "sets": [{"set_number": 1, "reps": 3, "weight": 40}]}
    ])
    result = workout_service.register_session(WorkoutSession(date="20-05-2026"), [
        {"name": "Bench Press", "sets": [{"set_number": 1, "reps": 10, "weight": 30}]}
    ])
    pr = PersonalRecordModel.get()
    assert pr.max_weight == 40
    assert pr.estimated_1rm == 44.0
    assert pr.date == "15-05-2026"
    assert result["new_prs"] == []


def test_pr_reps_one_uses_exact_weight(db, workout_service, exercises):
    result = workout_service.register_session(WorkoutSession(date="15-05-2026"), [
        {"name": "Bench Press", "sets": [{"set_number": 1, "reps": 1, "weight": 100}]}
    ])
    pr = PersonalRecordModel.get()
    assert pr.estimated_1rm == 100.0
    assert pr.max_reps == 1
    assert result["new_prs"][0]["estimated_1rm"] == 100.0


def test_pr_not_created_for_time_or_distance(db, workout_service, exercises):
    workout_service.register_session(WorkoutSession(date="15-05-2026"), [
        {"name": "Plank", "sets": [{"set_number": 1, "duration": 60}]},
        {"name": "Run", "sets": [{"set_number": 1, "distance": 5000}]},
    ])
    assert PersonalRecordModel.select().count() == 0


# --- Read operations ---


def test_get_last_workout_returns_most_recent(db, workout_service, exercises):
    workout_service.register_session(WorkoutSession(date="10-05-2026"), [
        {"name": "Bench Press", "sets": [{"set_number": 1, "reps": 10, "weight": 80}]}
    ])
    workout_service.register_session(WorkoutSession(date="15-05-2026"), [
        {"name": "Bench Press", "sets": [{"set_number": 1, "reps": 8, "weight": 85}]},
        {"name": "Plank", "sets": [{"set_number": 1, "duration": 60}]},
    ])
    result = workout_service.get_last_workout("Bench Press")
    assert result is not None
    assert result["exercise"] == "Bench Press"
    assert result["date"] == "15-05-2026"
    assert len(result["sets"]) == 1
    assert result["sets"][0]["weight"] == 85


def test_get_last_workout_fuzzy(db, workout_service, exercises):
    workout_service.register_session(WorkoutSession(date="15-05-2026"), [
        {"name": "Bench Press", "sets": [{"set_number": 1, "reps": 8, "weight": 85}]}
    ])
    result = workout_service.get_last_workout("bench pres")
    assert result is not None
    assert result["exercise"] == "Bench Press"


def test_get_last_workout_not_found_returns_none(db, workout_service, exercises):
    assert workout_service.get_last_workout("Nonexistent") is None


def test_get_personal_record_returns_record(db, workout_service, exercises):
    workout_service.register_session(WorkoutSession(date="15-05-2026"), [
        {"name": "Bench Press", "sets": [{"set_number": 1, "reps": 3, "weight": 40}]}
    ])
    pr = workout_service.get_personal_record("Bench Press")
    assert pr is not None
    assert pr.exercise_id == exercises["Bench Press"].id
    assert pr.max_weight == 40
    assert pr.max_reps == 3
    assert pr.estimated_1rm == 44.0
    assert pr.date == "15-05-2026"


def test_get_personal_record_not_found_returns_none(db, workout_service, exercises):
    assert workout_service.get_personal_record("Bench Press") is None
    assert workout_service.get_personal_record("zzz") is None


def test_get_by_day_returns_sessions(db, workout_service, exercises):
    workout_service.register_session(WorkoutSession(date="15-05-2026"), [
        {"name": "Bench Press", "sets": [{"set_number": 1, "reps": 10, "weight": 80}]},
    ])
    workout_service.register_session(WorkoutSession(date="16-05-2026"), [
        {"name": "Plank", "sets": [{"set_number": 1, "duration": 60}]},
    ])
    results = workout_service.get_by_day("15-05-2026")
    assert len(results) == 1
    assert results[0]["date"] == "15-05-2026"
    assert len(results[0]["sets"]) == 1
    assert results[0]["sets"][0]["exercise"] == "Bench Press"
    assert results[0]["sets"][0]["estimated_1rm"] == 106.7
    plank_results = workout_service.get_by_day("16-05-2026")
    assert plank_results[0]["sets"][0]["estimated_1rm"] is None
    assert workout_service.get_by_day("14-05-2026") == []


def test_get_by_day_invalid_date_raises(db, workout_service, exercises):
    with pytest.raises(ValidationError) as exc_info:
        workout_service.get_by_day("2026-05-15")
    assert exc_info.value.code == "invalid_input"


def test_get_exercise_stats_picks_highest_weight_and_best_1rm(db, workout_service, exercises):
    # Simulates user's exact case: 20kg x 10, 22kg x 6, 18kg x 12
    # 20kg x 10 reps -> e1rm: 26.7 kg
    # 22kg x 6 reps  -> e1rm: 26.4 kg (highest weight is 22kg with 6 reps)
    # 18kg x 12 reps -> e1rm: 25.2 kg
    workout_service.register_session(WorkoutSession(date="15-05-2026"), [
        {
            "name": "Bench Press",
            "sets": [
                {"set_number": 1, "reps": 10, "weight": 20},
                {"set_number": 2, "reps": 6, "weight": 22},
                {"set_number": 3, "reps": 12, "weight": 18},
            ],
        }
    ])
    bench_id = exercises["Bench Press"].id
    stats = workout_service.get_exercise_stats()
    assert bench_id in stats
    st = stats[bench_id]
    assert st["max_weight"] == 22.0
    assert st["max_weight_reps"] == 6
    assert st["max_weight_date"] == "15-05-2026"
    assert st["estimated_1rm"] == 26.7
    assert st["estimated_1rm_weight"] == 20.0
    assert st["estimated_1rm_reps"] == 10
    assert st["estimated_1rm_date"] == "15-05-2026"


def test_get_exercise_stats_picks_higher_reps_on_tied_max_weight(db, workout_service, exercises):
    workout_service.register_session(WorkoutSession(date="10-05-2026"), [
        {
            "name": "Bench Press",
            "sets": [
                {"set_number": 1, "reps": 3, "weight": 50},
                {"set_number": 2, "reps": 5, "weight": 50},
            ],
        }
    ])
    bench_id = exercises["Bench Press"].id
    stats = workout_service.get_exercise_stats(exercise_id=bench_id)
    assert stats[bench_id]["max_weight"] == 50.0
    assert stats[bench_id]["max_weight_reps"] == 5


def test_get_exercise_stats_ignores_time_and_distance_exercises(db, workout_service, exercises):
    workout_service.register_session(WorkoutSession(date="15-05-2026"), [
        {"name": "Plank", "sets": [{"set_number": 1, "duration": 60}]},
    ])
    stats = workout_service.get_exercise_stats()
    plank_id = exercises["Plank"].id
    assert plank_id not in stats


def test_get_exercise_stats_counts_sets_at_max_weight_in_session(
    db, workout_service, exercise_service, exercises
):
    # Case 1: 2 sets at 75 kg (10 reps and 9 reps) -> 75x10 (2)
    workout_service.register_session(WorkoutSession(date="15-05-2026"), [
        {
            "name": "Bench Press",
            "sets": [
                {"set_number": 1, "reps": 10, "weight": 75},
                {"set_number": 2, "reps": 9, "weight": 75},
                {"set_number": 3, "reps": 12, "weight": 70},
            ],
        }
    ])
    bench_id = exercises["Bench Press"].id
    stats = workout_service.get_exercise_stats(exercise_id=bench_id)
    assert stats[bench_id]["max_weight"] == 75.0
    assert stats[bench_id]["max_weight_reps"] == 10
    assert stats[bench_id]["max_weight_sets"] == 2

    # Case 2: 3 sets at 66 kg (15, 13, 13 reps) -> 66x15 (3)
    incline = exercise_service.create(Exercise(name="Incline Press"))
    workout_service.register_session(WorkoutSession(date="16-05-2026"), [
        {
            "name": "Incline Press",
            "sets": [
                {"set_number": 1, "reps": 15, "weight": 66},
                {"set_number": 2, "reps": 13, "weight": 66},
                {"set_number": 3, "reps": 13, "weight": 66},
            ],
        }
    ])
    stats_inc = workout_service.get_exercise_stats(exercise_id=incline.id)
    assert stats_inc[incline.id]["max_weight"] == 66.0
    assert stats_inc[incline.id]["max_weight_reps"] == 15
    assert stats_inc[incline.id]["max_weight_sets"] == 3


# --- Daily overwrite & PR recalculation ---


def test_register_session_first_of_day_not_overwritten(db, workout_service, exercises):
    result = workout_service.register_session(
        WorkoutSession(date="15-05-2026 09:00", notes="morning"),
        [{"name": "Bench Press", "sets": [{"set_number": 1, "reps": 8, "weight": 80}]}],
    )
    assert result["overwritten"] is False
    assert result["replaced_sessions"] == 0


def test_register_session_same_day_overwrites_existing_regardless_of_time(
    db, workout_service, exercises
):
    first = workout_service.register_session(
        WorkoutSession(date="15-05-2026 09:00", notes="morning push"),
        [
            {"name": "Bench Press", "sets": [{"set_number": 1, "reps": 10, "weight": 80}]},
            {"name": "Plank", "sets": [{"set_number": 1, "duration": 60}]},
        ],
    )
    assert first["overwritten"] is False
    assert first["replaced_sessions"] == 0

    # Other day must remain untouched
    workout_service.register_session(
        WorkoutSession(date="16-05-2026 18:00", notes="next day"),
        [{"name": "Plank", "sets": [{"set_number": 1, "duration": 90}]}],
    )

    # Registering again on 15-05-2026 (different hour) overwrites the 15-05 session
    second = workout_service.register_session(
        WorkoutSession(date="15-05-2026 19:30", notes="evening revised"),
        [{"name": "Bench Press", "sets": [{"set_number": 1, "reps": 6, "weight": 85}]}],
    )
    assert second["overwritten"] is True
    assert second["replaced_sessions"] == 1

    day15 = workout_service.get_by_day("15-05-2026")
    assert len(day15) == 1
    assert day15[0]["id"] == second["session"]["id"]
    assert day15[0]["notes"] == "evening revised"
    assert len(day15[0]["sets"]) == 1
    assert day15[0]["sets"][0]["exercise"] == "Bench Press"
    assert day15[0]["sets"][0]["weight"] == 85
    assert day15[0]["sets"][0]["reps"] == 6

    # Day 16 untouched
    day16 = workout_service.get_by_day("16-05-2026")
    assert len(day16) == 1
    assert day16[0]["notes"] == "next day"


def test_register_session_overwrites_multiple_legacy_sessions_on_same_day(
    db, workout_service, exercises
):
    # Simulate two legacy sessions already present on the same calendar day
    s1 = WorkoutSessionModel.create(date=datetime(2026, 5, 15, 8, 0), notes="legacy 1")
    s2 = WorkoutSessionModel.create(date=datetime(2026, 5, 15, 17, 0), notes="legacy 2")
    ExerciseSetModel.create(
        session=s1.id, exercise=exercises["Bench Press"].id, set_number=1, reps=5, weight=90
    )
    ExerciseSetModel.create(
        session=s2.id, exercise=exercises["Bench Press"].id, set_number=1, reps=5, weight=95
    )

    res = workout_service.register_session(
        WorkoutSession(date="15-05-2026 20:00", notes="clean replacement"),
        [{"name": "Bench Press", "sets": [{"set_number": 1, "reps": 8, "weight": 70}]}],
    )
    assert res["overwritten"] is True
    assert res["replaced_sessions"] == 2
    assert len(workout_service.get_by_day("15-05-2026")) == 1
    assert workout_service.get_by_day("15-05-2026")[0]["notes"] == "clean replacement"


def test_register_session_overwrite_recalculates_pr_on_typo_correction(
    db, workout_service, exercises
):
    # Earlier real session: 100kg x 1 -> e1rm 100.0
    earlier = workout_service.register_session(
        WorkoutSession(date="10-05-2026"),
        [{"name": "Bench Press", "sets": [{"set_number": 1, "reps": 1, "weight": 100}]}],
    )
    # Typo on 15-05-2026: 800kg x 5 -> inflated PR
    workout_service.register_session(
        WorkoutSession(date="15-05-2026"),
        [{"name": "Bench Press", "sets": [{"set_number": 1, "reps": 5, "weight": 800}]}],
    )
    assert workout_service.get_personal_record("Bench Press").max_weight == 800

    # Overwrite 15-05-2026 with corrected 80kg x 5 (e1rm 93.33 < 100.0)
    res = workout_service.register_session(
        WorkoutSession(date="15-05-2026"),
        [{"name": "Bench Press", "sets": [{"set_number": 1, "reps": 5, "weight": 80}]}],
    )
    assert res["overwritten"] is True
    assert res["new_prs"] == []

    pr = workout_service.get_personal_record("Bench Press")
    assert pr is not None
    assert pr.max_weight == 100
    assert pr.max_reps == 1
    assert pr.estimated_1rm == 100.0
    assert pr.date == "10-05-2026"
    assert pr.session_id == earlier["session"]["id"]

    # Also verify get_exercise_stats has no ghost 800kg value
    stats = workout_service.get_exercise_stats(exercise_id=exercises["Bench Press"].id)
    assert stats[exercises["Bench Press"].id]["max_weight"] == 100.0


def test_register_session_overwrite_removes_pr_when_exercise_removed_and_no_other_sets(
    db, workout_service, exercises
):
    workout_service.register_session(
        WorkoutSession(date="15-05-2026"),
        [{"name": "Bench Press", "sets": [{"set_number": 1, "reps": 8, "weight": 80}]}],
    )
    assert workout_service.get_personal_record("Bench Press") is not None

    # Overwrite 15-05-2026 with only Plank (Bench Press removed completely)
    res = workout_service.register_session(
        WorkoutSession(date="15-05-2026"),
        [{"name": "Plank", "sets": [{"set_number": 1, "duration": 60}]}],
    )
    assert res["overwritten"] is True
    assert workout_service.get_personal_record("Bench Press") is None
    stats = workout_service.get_exercise_stats(exercise_id=exercises["Bench Press"].id)
    assert exercises["Bench Press"].id not in stats


def test_register_session_overwrite_reverts_pr_when_removed_exercise_exists_on_earlier_day(
    db, workout_service, exercises
):
    workout_service.register_session(
        WorkoutSession(date="10-05-2026"),
        [{"name": "Bench Press", "sets": [{"set_number": 1, "reps": 5, "weight": 60}]}],
    )
    workout_service.register_session(
        WorkoutSession(date="15-05-2026"),
        [{"name": "Bench Press", "sets": [{"set_number": 1, "reps": 5, "weight": 90}]}],
    )
    assert workout_service.get_personal_record("Bench Press").max_weight == 90

    # Overwrite 15-05-2026 removing Bench Press -> PR reverts to 10-05-2026 (60kg)
    workout_service.register_session(
        WorkoutSession(date="15-05-2026"),
        [{"name": "Plank", "sets": [{"set_number": 1, "duration": 90}]}],
    )
    pr = workout_service.get_personal_record("Bench Press")
    assert pr is not None
    assert pr.max_weight == 60
    assert pr.date == "10-05-2026"


def test_register_session_overwrite_rolls_back_on_validation_error(
    db, workout_service, exercises
):
    original = workout_service.register_session(
        WorkoutSession(date="15-05-2026", notes="original valid"),
        [{"name": "Bench Press", "sets": [{"set_number": 1, "reps": 8, "weight": 80}]}],
    )
    original_pr = workout_service.get_personal_record("Bench Press")
    assert original_pr is not None

    # Attempt overwrite with invalid payload (missing weight for weight_reps)
    with pytest.raises(ValidationError) as exc_info:
        workout_service.register_session(
            WorkoutSession(date="15-05-2026", notes="broken"),
            [{"name": "Bench Press", "sets": [{"set_number": 1, "reps": 8}]}],
        )
    assert exc_info.value.code == "invalid_input"

    # Existing session, sets, and PR remain completely intact
    day15 = workout_service.get_by_day("15-05-2026")
    assert len(day15) == 1
    assert day15[0]["id"] == original["session"]["id"]
    assert day15[0]["notes"] == "original valid"
    assert day15[0]["sets"][0]["weight"] == 80
    pr_after = workout_service.get_personal_record("Bench Press")
    assert pr_after is not None
    assert pr_after.max_weight == 80
    assert pr_after.session_id == original["session"]["id"]



