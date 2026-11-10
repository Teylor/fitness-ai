"""Unit tests: Google Health service and client."""

import httpx2
import pytest

from src.db.models import Ingredient, MealEntry, SleepLog, WeightLog
from src.services.google_health_client import GoogleHealthClient
from src.services.google_health_service import GoogleHealthService
from src.utils.errors import ValidationError


def test_client_missing_token_raises_validation_error():
    client = GoogleHealthClient(token="")
    with pytest.raises(ValidationError) as exc:
        client._ensure_authenticated()
    assert "Missing Google Health credentials" in str(exc.value)


def test_sync_meals_without_meals_returns_zero(db):
    client = GoogleHealthClient(token="mock-token")
    service = GoogleHealthService(client=client)
    res = service.sync_meals(date="10-11-2026")
    assert res["status"] == "ok"
    assert res["synced_count"] == 0
    assert res["total_kcal"] == 0.0


def test_sync_meals_with_meals_raises_sync_unsupported(db):
    ing = Ingredient.create(
        name="Salmon", unit="gr", kcal=208.0, protein=20.0, carbs=0.0, fat=13.0
    )
    MealEntry.create(
        date="10-11-2026",
        item_type="ingredient",
        item_id=ing.id,
        quantity=200.0,
        unit="gr",
    )

    client = GoogleHealthClient(token="mock-token")
    service = GoogleHealthService(client=client)

    # Google Health API v4 `food` data type is read-only, so pushing meals
    # is not supported and must fail with a `sync_unsupported` error.
    with pytest.raises(ValidationError) as exc:
        service.sync_meals(date="10-11-2026")
    assert exc.value.code == "sync_unsupported"


def test_fetch_sleep_persists_records(db):
    def mock_handler(request: httpx2.Request) -> httpx2.Response:
        assert "/dataTypes/sleep/dataPoints" in str(request.url)
        mock_data = {
            "dataPoints": [
                {
                    "sleep": {
                        "interval": {
                            "startTime": "2026-11-09T23:00:00Z",
                            "endTime": "2026-11-10T07:15:00Z",
                        },
                        "summary": {
                            "minutesAsleep": 495,
                            "stagesSummary": [
                                {"type": "DEEP", "minutes": 110},
                                {"type": "REM", "minutes": 95},
                                {"type": "LIGHT", "minutes": 290},
                            ],
                        },
                    }
                }
            ]
        }
        return httpx2.Response(200, json=mock_data)

    transport = httpx2.MockTransport(mock_handler)
    mock_http = httpx2.Client(transport=transport)
    client = GoogleHealthClient(token="mock-token", http_client=mock_http)
    service = GoogleHealthService(client=client)

    res = service.fetch_sleep(date="10-11-2026")
    assert res["status"] == "ok"
    assert res["count"] == 1
    rec = res["records"][0]
    assert rec["duration_minutes"] == 495.0
    assert rec["deep_sleep_minutes"] == 110.0

    # Verify saved in SQLite database
    assert SleepLog.select().count() == 1
    db_row = SleepLog.get()
    assert db_row.duration_minutes == 495.0


def test_fetch_weight_persists_records(db):
    def mock_handler(request: httpx2.Request) -> httpx2.Response:
        assert "/dataTypes/weight/dataPoints" in str(request.url)
        mock_data = {
            "dataPoints": [
                {
                    "weight": {
                        "sampleTime": {
                            "physicalTime": "2026-11-10T08:00:00Z",
                            "utcOffset": "3600s",
                        },
                        "weightGrams": 78500,
                    }
                }
            ]
        }
        return httpx2.Response(200, json=mock_data)

    transport = httpx2.MockTransport(mock_handler)
    mock_http = httpx2.Client(transport=transport)
    client = GoogleHealthClient(token="mock-token", http_client=mock_http)
    service = GoogleHealthService(client=client)

    res = service.fetch_weight(date="10-11-2026")
    assert res["status"] == "ok"
    assert res["count"] == 1
    assert res["latest_weight_kg"] == 78.5

    # Verify saved in SQLite database
    assert WeightLog.select().count() == 1
    db_row = WeightLog.get()
    assert db_row.weight_kg == 78.5

