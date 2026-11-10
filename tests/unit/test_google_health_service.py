"""Unit tests: Google Health service and client."""

import httpx2
import pytest

from src.db.models import Ingredient, MealEntry, SleepLog, WeightLog
from src.services.google_health_client import GoogleHealthClient
from src.services.google_health_service import GoogleHealthService
from src.utils.errors import ValidationError


def test_client_missing_token_raises_validation_error():
    client = GoogleHealthClient(token="", refresh_token="")
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


def test_sync_meals_with_meals_uploads_nutrition_log(db):
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

    posted_payloads = []

    def mock_handler(request: httpx2.Request) -> httpx2.Response:
        import json
        assert request.headers.get("authorization") == "Bearer mock-token"
        assert "/dataTypes/nutrition-log/dataPoints" in str(request.url)
        posted_payloads.append(json.loads(request.content.decode("utf-8")))
        return httpx2.Response(200, json={"status": "ok"})

    transport = httpx2.MockTransport(mock_handler)
    mock_http = httpx2.Client(transport=transport)
    client = GoogleHealthClient(token="mock-token", http_client=mock_http)
    service = GoogleHealthService(client=client)

    res = service.sync_meals(date="10-11-2026")
    assert res["status"] == "ok"
    assert res["synced_count"] == 1
    assert res["total_kcal"] == 416.0
    assert len(posted_payloads) == 1
    p = posted_payloads[0]["nutritionLog"]
    assert p["foodDisplayName"] == "Salmon"
    assert p["mealType"] == "MEAL_TYPE_UNSPECIFIED"
    assert p["energy"]["kcal"] == 416.0
    assert p["totalFat"]["grams"] == 26.0
    assert p["totalCarbohydrate"]["grams"] == 0.0
    assert p["nutrients"][0]["nutrient"] == "PROTEIN"
    assert p["nutrients"][0]["quantity"]["grams"] == 40.0


def test_clear_nutrition_logs(db):
    batch_delete_calls = []

    def mock_handler(request: httpx2.Request) -> httpx2.Response:
        import json
        url_str = str(request.url)
        if request.method == "GET" and "/dataTypes/nutrition-log/dataPoints" in url_str:
            return httpx2.Response(
                200,
                json={
                    "dataPoints": [
                        {"name": "users/me/dataTypes/nutrition-log/dataPoints/dp-1"},
                        {"name": "users/me/dataTypes/nutrition-log/dataPoints/dp-2"},
                    ]
                },
            )
        elif request.method == "POST" and ":batchDelete" in url_str:
            batch_delete_calls.append(json.loads(request.content.decode("utf-8")))
            return httpx2.Response(200, json={"status": "ok"})
        return httpx2.Response(404)

    transport = httpx2.MockTransport(mock_handler)
    mock_http = httpx2.Client(transport=transport)
    client = GoogleHealthClient(token="mock-token", http_client=mock_http)
    service = GoogleHealthService(client=client)

    res = service.clear_nutrition_logs()
    assert res["status"] == "ok"
    assert res["deleted_count"] == 2
    assert len(batch_delete_calls) == 1
    assert batch_delete_calls[0]["names"] == [
        "users/me/dataTypes/nutrition-log/dataPoints/dp-1",
        "users/me/dataTypes/nutrition-log/dataPoints/dp-2",
    ]


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


def test_client_refresh_token_on_401():
    attempts = []

    def mock_handler(request: httpx2.Request) -> httpx2.Response:
        url_str = str(request.url)
        if "oauth2.googleapis.com/token" in url_str:
            return httpx2.Response(200, json={"access_token": "new-fresh-token"})
        if "dataTypes/sleep/dataPoints" in url_str:
            attempts.append(request.headers.get("authorization"))
            if len(attempts) == 1:
                return httpx2.Response(401, json={"error": "unauthorized"})
            return httpx2.Response(200, json={"dataPoints": []})
        return httpx2.Response(404)

    transport = httpx2.MockTransport(mock_handler)
    mock_http = httpx2.Client(transport=transport)
    client = GoogleHealthClient(
        token="expired-token",
        refresh_token="my-refresh-token",
        client_id="my-client-id",
        client_secret="my-secret",
        http_client=mock_http,
    )

    dps = client.get_sleep_datapoints()
    assert dps == []
    assert len(attempts) == 2
    assert attempts[0] == "Bearer expired-token"
    assert attempts[1] == "Bearer new-fresh-token"
    assert client.token == "new-fresh-token"


