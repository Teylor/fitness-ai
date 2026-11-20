"""Integration tests: MCP Body Progress tools."""

from src.mcp.tools.body_progress_tools import (
    delete_body_progress,
    list_body_progress,
    log_body_progress,
)


def test_body_progress_mcp_tools_lifecycle(db):
    res1 = log_body_progress(
        date="03-11-2026",
        weight_kg=79.0,
        waist_cm=84.0,
        chest_cm=100.0,
        arm_cm=35.5,
        leg_cm=57.5,
        notes="Baseline",
    )
    assert res1["status"] == "ok"
    rec_id = res1["progress"]["id"]
    assert res1["progress"]["weight_kg"] == 79.0

    res2 = log_body_progress(date="18-11-2026", weight_kg=77.8, waist_cm=82.5)
    assert res2["status"] == "ok"

    listed = list_body_progress(month="2026-11")
    assert listed["status"] == "ok"
    assert listed["count"] == 2
    assert [e["date"] for e in listed["entries"]] == ["03-11-2026", "18-11-2026"]

    deleted = delete_body_progress(progress_id=rec_id)
    assert deleted["status"] == "ok"
    assert deleted["deleted_id"] == rec_id

    after = list_body_progress(month="2026-11")
    assert after["count"] == 1


def test_body_progress_mcp_tools_error_envelopes(db):
    bad = log_body_progress(date="03-11-2026")
    assert bad["status"] == "error"
    assert bad["code"] == "invalid_input"

    bad_month = list_body_progress(month="invalid")
    assert bad_month["status"] == "error"
    assert bad_month["code"] == "invalid_input"

    missing = delete_body_progress(progress_id=99999)
    assert missing["status"] == "error"
    assert missing["code"] == "not_found"
