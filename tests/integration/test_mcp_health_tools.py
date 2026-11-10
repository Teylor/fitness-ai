"""Integration tests: MCP Google Health tools."""

import httpx2
import pytest

from src.config import settings
from src.db.models import Ingredient, MealEntry
from src.mcp.tools.health_tools import (
    fetch_google_health_sleep,
    fetch_google_health_weight,
    sync_google_health,
    sync_meals_to_google_health,
)


def test_health_tools_unauthenticated_return_error(db, monkeypatch):
    monkeypatch.setattr(settings, "google_health_token", None)
    monkeypatch.setattr(settings, "google_health_refresh_token", None)

    res = sync_meals_to_google_health("10-11-2026")
    assert res["status"] == "error"
    assert res["code"] == "invalid_input"
    assert "Missing Google Health credentials" in res["message"]

    res_sleep = fetch_google_health_sleep("10-11-2026")
    assert res_sleep["status"] == "error"
    assert res_sleep["code"] == "invalid_input"

    res_weight = fetch_google_health_weight("10-11-2026")
    assert res_weight["status"] == "error"
    assert res_weight["code"] == "invalid_input"


def test_sync_meals_tool_success(db, monkeypatch):
    monkeypatch.setattr(settings, "google_health_token", "test-bearer-token")

    ing = Ingredient.create(
        name="Eggs", unit="u", kcal=70.0, protein=6.0, carbs=0.5, fat=5.0
    )
    MealEntry.create(
        date="10-11-2026",
        item_type="ingredient",
        item_id=ing.id,
        quantity=3.0,
        unit="u",
    )

    def mock_handler(request: httpx2.Request) -> httpx2.Response:
        assert request.headers.get("authorization") == "Bearer test-bearer-token"
        assert "/dataTypes/nutrition-log/dataPoints" in str(request.url)
        return httpx2.Response(200, json={"status": "ok"})

    transport = httpx2.MockTransport(mock_handler)
    mock_http = httpx2.Client(transport=transport)

    from src.services.google_health_client import GoogleHealthClient
    orig_init = GoogleHealthClient.__init__

    def patched_init(self, *args, **kwargs):
        orig_init(self, token="test-bearer-token", http_client=mock_http)

    monkeypatch.setattr(GoogleHealthClient, "__init__", patched_init)

    res = sync_meals_to_google_health("10-11-2026")
    assert res["status"] == "ok"
    assert res["synced_count"] == 1
    assert res["total_kcal"] == 210.0


def test_fetch_sleep_and_weight_tools_success(db, monkeypatch):
    monkeypatch.setattr(settings, "google_health_token", "test-bearer-token")

    def mock_handler(request: httpx2.Request) -> httpx2.Response:
        url_str = str(request.url)
        if "/dataTypes/sleep/dataPoints" in url_str:
            return httpx2.Response(
                200,
                json={
                    "dataPoints": [
                        {
                            "sleep": {
                                "interval": {
                                    "startTime": "2026-11-09T22:30:00Z",
                                    "endTime": "2026-11-10T06:30:00Z",
                                },
                                "summary": {
                                    "minutesAsleep": 480,
                                    "stagesSummary": [
                                        {"type": "DEEP", "minutes": 90},
                                        {"type": "REM", "minutes": 90},
                                        {"type": "LIGHT", "minutes": 300},
                                    ],
                                },
                            }
                        }
                    ]
                },
            )
        elif "/dataTypes/weight/dataPoints" in url_str:
            return httpx2.Response(
                200,
                json={
                    "dataPoints": [
                        {
                            "weight": {
                                "sampleTime": {
                                    "physicalTime": "2026-11-10T07:30:00Z",
                                    "utcOffset": "3600s",
                                },
                                "weightGrams": 75200,
                            }
                        }
                    ]
                },
            )
        return httpx2.Response(404)

    transport = httpx2.MockTransport(mock_handler)
    mock_http = httpx2.Client(transport=transport)

    from src.services.google_health_client import GoogleHealthClient
    orig_init = GoogleHealthClient.__init__

    def patched_init(self, *args, **kwargs):
        orig_init(self, token="test-bearer-token", http_client=mock_http)

    monkeypatch.setattr(GoogleHealthClient, "__init__", patched_init)

    # 1. Fetch sleep tool
    sleep_res = fetch_google_health_sleep("10-11-2026")
    assert sleep_res["status"] == "ok"
    assert sleep_res["count"] == 1
    assert sleep_res["records"][0]["duration_minutes"] == 480.0

    # 2. Fetch weight tool
    weight_res = fetch_google_health_weight("10-11-2026")
    assert weight_res["status"] == "ok"
    assert weight_res["count"] == 1
    assert weight_res["latest_weight_kg"] == 75.2

    # 3. Full sync tool
    # (sleep sessions already persisted by step 1; weight records already
    # persisted by step 2, so no new rows are created during full sync.)
    sync_res = sync_google_health("10-11-2026")
    assert sync_res["status"] == "ok"
    assert sync_res["sleep_sessions_fetched"] == 1
    assert sync_res["weight_records_fetched"] == 0


def test_log_steps_and_get_health_metrics_tools(db):
    from src.db.models import SleepLog, WeightLog
    from src.mcp.tools.health_tools import get_health_metrics, log_steps

    # 1. Log steps
    res_steps = log_steps(steps=8500, date="10-11-2026", distance_km=6.2)
    assert res_steps["status"] == "ok"
    assert res_steps["steps"] == 8500
    assert res_steps["distance_km"] == 6.2

    # 2. Add local sleep and weight logs
    SleepLog.create(
        date="10-11-2026",
        start_time="2026-11-09T23:00:00Z",
        end_time="2026-11-10T07:00:00Z",
        duration_minutes=480.0,
        deep_sleep_minutes=90.0,
        rem_sleep_minutes=100.0,
        light_sleep_minutes=290.0,
        source="google_health",
    )
    WeightLog.create(
        date="10-11-2026",
        weight_kg=74.5,
        bmi=22.5,
        body_fat_pct=15.0,
        source="google_health",
    )

    # 3. Query health metrics
    metrics = get_health_metrics("10-11-2026")
    assert metrics["status"] == "ok"
    assert metrics["date"] == "10-11-2026"
    assert metrics["steps"]["steps"] == 8500
    assert metrics["sleep"]["duration_hours"] == 8.0
    assert metrics["weight"]["weight_kg"] == 74.5

    # 4. Update steps
    updated_steps = log_steps(steps=10200, date="10-11-2026", distance_km=7.5)
    assert updated_steps["status"] == "ok"
    assert updated_steps["steps"] == 10200
    metrics2 = get_health_metrics("10-11-2026")
    assert metrics2["steps"]["steps"] == 10200

