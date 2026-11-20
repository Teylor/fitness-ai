"""Unit tests: BodyProgressService."""

import pytest

from src.services.body_progress_service import BodyProgressService
from src.utils.errors import NotFoundError, ValidationError


def test_log_progress_creates_record_and_upserts_same_date(db):
    svc = BodyProgressService()

    created = svc.log_progress(
        date="05-11-2026",
        weight_kg=78.4,
        waist_cm=82.5,
        chest_cm=101.0,
        arm_cm=36.2,
        leg_cm=58.0,
        notes="Morning fasted",
    )
    assert created.id is not None
    assert created.date == "05-11-2026"
    assert created.weight_kg == 78.4
    assert created.waist_cm == 82.5
    assert created.chest_cm == 101.0
    assert created.arm_cm == 36.2
    assert created.leg_cm == 58.0
    assert created.notes == "Morning fasted"

    # Re-logging the same date updates in place (upsert)
    updated = svc.log_progress(
        date="05-11-2026",
        weight_kg=78.1,
        waist_cm=82.0,
        chest_cm=101.5,
        arm_cm=36.5,
        leg_cm=58.2,
        notes="Updated",
    )
    assert updated.id == created.id
    assert updated.weight_kg == 78.1
    assert updated.waist_cm == 82.0
    assert updated.notes == "Updated"
    assert len(svc.list_progress()) == 1


def test_log_progress_allows_partial_measurements(db):
    svc = BodyProgressService()
    rec = svc.log_progress(date="10-11-2026", weight_kg=77.5)
    assert rec.weight_kg == 77.5
    assert rec.waist_cm is None
    assert rec.chest_cm is None
    assert rec.arm_cm is None
    assert rec.leg_cm is None


def test_log_progress_validation_errors(db):
    svc = BodyProgressService()

    with pytest.raises(ValidationError):
        svc.log_progress(date="10-11-2026")  # no measurements

    with pytest.raises(ValidationError):
        svc.log_progress(date="2026-11-10", weight_kg=77.0)  # wrong date format

    with pytest.raises(ValidationError):
        svc.log_progress(date="10-11-2026", weight_kg=0)

    with pytest.raises(ValidationError):
        svc.log_progress(date="10-11-2026", waist_cm=-5)


def test_list_progress_filters_by_month_and_orders_chronologically(db):
    svc = BodyProgressService()
    svc.log_progress(date="20-11-2026", weight_kg=77.0)
    svc.log_progress(date="02-11-2026", weight_kg=78.5)
    svc.log_progress(date="12-10-2026", weight_kg=79.2)

    nov = svc.list_progress(month="2026-11")
    assert [r.date for r in nov] == ["02-11-2026", "20-11-2026"]

    oct_entries = svc.list_progress(month="2026-10")
    assert [r.date for r in oct_entries] == ["12-10-2026"]

    all_entries = svc.list_progress()
    assert [r.date for r in all_entries] == ["12-10-2026", "02-11-2026", "20-11-2026"]

    with pytest.raises(ValidationError):
        svc.list_progress(month="11-2026")


def test_delete_progress_removes_record_or_raises_not_found(db):
    svc = BodyProgressService()
    rec = svc.log_progress(date="15-11-2026", weight_kg=77.8)
    assert svc.delete_progress(rec.id) is True
    assert svc.get_by_date("15-11-2026") is None

    with pytest.raises(NotFoundError):
        svc.delete_progress(rec.id)
