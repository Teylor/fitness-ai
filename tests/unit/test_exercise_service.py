"""Tests: ExerciseService."""

import pytest

from src.models.exercise import Exercise
from src.utils.errors import ValidationError


def test_create_exercise(db, exercise_service):
    created = exercise_service.create(
        Exercise(name="Bench Press", muscle_group="chest", type="weight_reps")
    )
    assert created.id is not None
    assert created.name == "Bench Press"
    assert created.muscle_group == "chest"
    assert created.type == "weight_reps"

    stored = exercise_service.get_by_id(created.id)
    assert stored is not None
    assert stored.name == "Bench Press"
    assert stored.muscle_group == "chest"
    assert stored.type == "weight_reps"


def test_create_exercise_defaults(db, exercise_service):
    created = exercise_service.create(Exercise(name="Plank"))
    assert created.muscle_group == "unknown"
    assert created.type == "weight_reps"


def test_create_exercise_idempotent_duplicate_returns_existing(db, exercise_service):
    a = exercise_service.create(Exercise(name="Bench Press", muscle_group="chest"))
    b = exercise_service.create(Exercise(name="BENCH PRESS", muscle_group="chest"))
    assert a.id == b.id
    assert exercise_service.get_by_id(a.id).name == "Bench Press"


def test_create_exercise_duplicate_accent_insensitive(db, exercise_service):
    a = exercise_service.create(Exercise(name="Cafe con Leche Press"))
    b = exercise_service.create(Exercise(name="CAFÉ CON LECHE PRESS"))
    assert a.id == b.id


def test_create_exercise_empty_name_raises(db, exercise_service):
    with pytest.raises(ValidationError) as exc_info:
        exercise_service.create(Exercise(name="   "))
    assert exc_info.value.code == "invalid_input"
    assert isinstance(exc_info.value, ValueError)


def test_create_exercise_invalid_type_raises(db, exercise_service):
    with pytest.raises(ValidationError) as exc_info:
        exercise_service.create(Exercise(name="X", type="distance_m"))
    assert exc_info.value.code == "invalid_input"
    assert isinstance(exc_info.value, ValueError)


def test_get_by_id_not_found_returns_none(db, exercise_service):
    assert exercise_service.get_by_id(999) is None


def test_find_by_name_case_insensitive(db, exercise_service):
    created = exercise_service.create(Exercise(name="Bench Press"))
    found = exercise_service.find_by_name("bench press")
    assert found is not None
    assert found.id == created.id


def test_find_by_name_fuzzy(db, exercise_service):
    exercise_service.create(Exercise(name="Bench Press"))
    found = exercise_service.find_by_name("bench pres")
    assert found is not None
    assert found.name == "Bench Press"


def test_find_by_name_no_match_returns_none(db, exercise_service):
    exercise_service.create(Exercise(name="Bench Press"))
    assert exercise_service.find_by_name("zzz") is None


def test_find_exact_no_fuzzy(db, exercise_service):
    created = exercise_service.create(Exercise(name="Bench Press"))
    assert exercise_service.find_exact("bench pres") is None
    exact = exercise_service.find_exact("BENCH PRESS")
    assert exact is not None
    assert exact.id == created.id


def test_list_search(db, exercise_service):
    exercise_service.create(Exercise(name="Bench Press"))
    exercise_service.create(Exercise(name="Deadlift"))
    exercise_service.create(Exercise(name="Bench Row"))

    results = exercise_service.list(search="bench")
    assert len(results) == 2
    assert all("bench" in r.name.lower() for r in results)


def test_list_muscle_group_filter(db, exercise_service):
    chest = exercise_service.create(Exercise(name="Bench Press", muscle_group="chest"))
    exercise_service.create(Exercise(name="Deadlift", muscle_group="back"))
    exercise_service.create(Exercise(name="Pull Up", muscle_group="back"))

    results = exercise_service.list(muscle_group="chest")
    assert len(results) == 1
    assert results[0].id == chest.id


def test_list_pagination(db, exercise_service):
    for i in range(10):
        exercise_service.create(Exercise(name=f"Item {i}"))

    page = exercise_service.list(limit=5, offset=2)
    assert len(page) == 5
    all_items = exercise_service.list(limit=100)
    assert [x.id for x in page] == [x.id for x in all_items[2:7]]


def test_update_exercise_muscle_group(db, exercise_service):
    created = exercise_service.create(Exercise(name="Bench Press", muscle_group="chest"))
    updated = exercise_service.update(created.id, muscle_group="pecho")
    assert updated.muscle_group == "pecho"
    assert updated.type == "weight_reps"
    stored = exercise_service.get_by_id(created.id)
    assert stored.muscle_group == "pecho"


def test_update_exercise_type(db, exercise_service):
    created = exercise_service.create(Exercise(name="Plank"))
    updated = exercise_service.update(created.id, type="time")
    assert updated.type == "time"
    assert updated.muscle_group == "unknown"


def test_update_exercise_both_fields(db, exercise_service):
    created = exercise_service.create(Exercise(name="Squat"))
    updated = exercise_service.update(created.id, muscle_group="legs", type="distance")
    assert updated.muscle_group == "legs"
    assert updated.type == "distance"


def test_update_exercise_unknown_id_raises(db, exercise_service):
    with pytest.raises(ValidationError) as exc_info:
        exercise_service.update(999, muscle_group="chest")
    assert exc_info.value.code == "invalid_input"
    assert isinstance(exc_info.value, ValueError)


def test_update_exercise_invalid_type_raises(db, exercise_service):
    created = exercise_service.create(Exercise(name="Bench Press"))
    with pytest.raises(ValidationError) as exc_info:
        exercise_service.update(created.id, type="distance_m")
    assert exc_info.value.code == "invalid_input"
    assert isinstance(exc_info.value, ValueError)


def test_update_exercise_blank_muscle_group_raises(db, exercise_service):
    created = exercise_service.create(Exercise(name="Bench Press"))
    with pytest.raises(ValidationError) as exc_info:
        exercise_service.update(created.id, muscle_group="   ")
    assert exc_info.value.code == "invalid_input"
    assert isinstance(exc_info.value, ValueError)


def test_update_exercise_none_fields_no_change(db, exercise_service):
    created = exercise_service.create(Exercise(name="Bench Press", muscle_group="chest"))
    updated = exercise_service.update(created.id)
    assert updated.muscle_group == "chest"
    assert updated.type == "weight_reps"


def test_list_exercises_accent_insensitive_search_and_muscle_group(db, exercise_service):
    exercise_service.create(Exercise(name="Curl de Bíceps", muscle_group="Bíceps"))
    exercise_service.create(Exercise(name="Extensión de Tríceps", muscle_group="Tríceps"))

    by_search = exercise_service.list(search="biceps")
    assert [e.name for e in by_search] == ["Curl de Bíceps"]

    by_group = exercise_service.list(muscle_group="triceps")
    assert [e.name for e in by_group] == ["Extensión de Tríceps"]
