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
        return httpx2.Response(200, json={"status": "ok"})

    transport = httpx2.MockTransport(mock_handler)
    mock_http = httpx2.Client(transport=transport)

    # Monkeypatch the client instantiation inside service
    from src.services.google_health_client import GoogleHealthClient
    orig_init = GoogleHealthClient.__init__

    def patched_init(self, *args, **kwargs):
        orig_init(self, token="test-bearer-token", http_client=mock_http)

    monkeypatch.setattr(GoogleHealthClient, "__init__", patched_init)

    res = sync_meals_to_google_health("10-11-2026")
    assert res["status"] == "ok"
    assert res["date"] == "10-11-2026"
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
                            "startTime": "2026-11-09T22:30:00Z",
                            "endTime": "2026-11-10T06:30:00Z",
                            "value": {
                                "duration_minutes": 480.0,
                                "deep_sleep_minutes": 90.0,
                                "rem_sleep_minutes": 90.0,
                                "light_sleep_minutes": 300.0,
                            },
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
                            "startTime": "2026-11-10T07:30:00Z",
                            "value": {"weight_kg": 75.2, "bmi": 22.8},
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
    sync_res = sync_google_health("10-11-2026")
    assert sync_res["status"] == "ok"
    assert sync_res["sleep_sessions_fetched"] == 1
    assert sync_res["weight_records_fetched"] == 1
