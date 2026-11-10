# Feature: google-health-food-sync

> Fix Google Health food synchronization by uploading meals as `nutrition-log` data points to Google Health API v4.

## Spec
> What and why (no technology)

### Context
- Users log food items (ingredients and recipes) with nutritional values (calories, protein, carbohydrates, fat) in Fitness AI.
- Users expect their daily logged meals to synchronize with the Google Health / Health Connect ecosystem when calling `sync_meals_to_google_health` or `sync_google_health`.
- Currently, meal synchronization is rejected because the client was previously pointing to `food/dataPoints` (which is a read-only food database) and raising `sync_unsupported`.
- The official Google Health API v4 allows recording custom nutritional entries using the `nutrition-log` data type.

### Objective
- Enable bidirectional meal synchronization by pushing recorded meals as `nutrition-log` dataPoints to `POST https://health.googleapis.com/v4/users/me/dataTypes/nutrition-log/dataPoints`.
- Map local meal entries with their food name (`foodDisplayName`), energy (`energy` in KILOCALORIES), fat (`totalFat` in GRAMS and `energyFromFat`), carbohydrates (`totalCarbohydrate` in GRAMS), and protein (`nutrients` array with PROTEIN in GRAMS).
- Update `sync_meals` and `sync_google_health` to report actual counts and total calories synchronized.

### Acceptance Criteria
- [x] C1: **HTTP Client Updates**: `GoogleHealthClient.post_nutrition_datapoint` successfully sends HTTP POST to `{base_url}/users/me/dataTypes/nutrition-log/dataPoints` with Bearer auth and JSON payload, returning the response or status ok.
- [x] C2: **Nutrition Log Payload Formatting**: `GoogleHealthService.sync_meals` generates valid Google Health v4 `nutrition-log` data points for each meal entry on the specified date, including `interval`, `foodDisplayName`, `energy`, `energyFromFat`, `totalCarbohydrate`, `totalFat`, and `nutrients` (protein).
- [x] C3: **Bidirectional Sync Integration**: `sync_google_health` reports the actual count of meals pushed (`meals_synced`) and total calories (`total_kcal_synced`) along with sleep and weight records fetched.
- [x] C4: **Unit & Integration Test Coverage**: Unit tests (`test_google_health_service.py`), integration tests (`test_mcp_health_tools.py`), and E2E tests (`test_hermes_e2e.py`) verify the `nutrition-log` endpoint, payloads, batch deletion, and automatic token refresh on 401.
- [x] C5: **Clear Nutrition Logs & Token Auto-Refresh**: Added `batch_delete_datapoints` and `clear_nutrition_logs` to wipe previous entries, and automatic OAuth token refresh using `GOOGLE_HEALTH_REFRESH_TOKEN`.

## Clarify
> Resolved ambiguities

- **Q1. Which endpoint and data type in Google Health API v4 accepts meal uploads?**
  - A: `POST https://health.googleapis.com/v4/users/me/dataTypes/nutrition-log/dataPoints`. The `food` data type is a read-only food reference database; the user's personal dietary intake sessions are tracked via `nutrition-log`.
- **Q2. What permissions / OAuth scope are required?**
  - A: `https://www.googleapis.com/auth/googlehealth.nutrition.writeonly` (already configured in `scripts/get_google_token.py`).
- **Q3. What time interval should be used for logged meals?**
  - A: If no explicit time is stored, default to noon UTC on the meal date (`{iso_date}T12:00:00Z` to `{iso_date}T12:30:00Z`).

## Plan
> Technical decisions + classification

- **Classification**: Normal (fixes endpoint and payload mapping in existing client and service, updates mock tests).
- **D1 (Client Update)**:
  - In `src/services/google_health_client.py`: Remove `sync_unsupported` error in `post_nutrition_datapoint`. Send POST to `{self.base_url}/users/me/dataTypes/nutrition-log/dataPoints`.
- **D2 (Service Mapping)**:
  - In `src/services/google_health_service.py`: Format payload according to `nutrition-log` schema.
  - In `sync_google_health`: Set `meals_synced = meals_res["synced_count"]` and `total_kcal_synced = meals_res["total_kcal"]`.
- **D3 (Tests)**:
  - Update `tests/unit/test_google_health_service.py` to assert POST to `/dataTypes/nutrition-log/dataPoints`.
  - Update `tests/integration/test_mcp_health_tools.py` to verify `sync_meals_tool_success`.
  - Update `tests/e2e/test_hermes_e2e.py` to verify full sync flow with meals uploaded.

## Tasks
> Implementation checklist

- [x] T1: Update `post_nutrition_datapoint` in `google_health_client.py` to call `nutrition-log/dataPoints` → verify: `pytest tests/unit/test_google_health_service.py`
- [x] T2: Update `sync_meals` and `sync_google_health` in `google_health_service.py` with `nutrition-log` payload mapping → verify: `pytest tests/unit/test_google_health_service.py`
- [x] T3: Update integration tests in `tests/integration/test_mcp_health_tools.py` and `tests/e2e/test_hermes_e2e.py` → verify: `pytest tests/integration/test_mcp_health_tools.py tests/e2e/test_hermes_e2e.py`
- [x] T4: Run full test suite → verify: `pytest tests/ -v`
- [x] T5: Verify live running server

## Verification
> Comparison against the spec

- **C1 (HTTP Client Updates)**: Replaced read-only restriction with HTTP POST to `{base_url}/users/me/dataTypes/nutrition-log/dataPoints`. Verified by `test_sync_meals_with_meals_uploads_nutrition_log`.
- **C2 (Nutrition Log Payload Formatting)**: Mapped local meal entries to official Google Health v4 `nutrition-log` dataPoint schema with `foodDisplayName`, `energy` in kcal, `energyFromFat`, `totalCarbohydrate`, `totalFat`, and `nutrients` (protein). Verified by unit test.
- **C3 (Bidirectional Sync Integration)**: `sync_google_health` now reports `meals_synced` and `total_kcal_synced` from `sync_meals`. Verified by E2E test `test_hermes_google_health_sync_flow`.
- **C4 (Unit & Integration Test Coverage)**: Full test suite passing 162/162 tests without warnings or regressions.
- **C5 (Clear Nutrition Logs & Auto-Refresh)**: Verified live batch delete and synchronization against Google Health API v4, and unit tested 401 retry with refresh token.

## Close
> Close

- **Date**: 2026-11-10
- **Result**: Complete and verified against live Google Health API v4.
- **Artifacts**:
  - `src/config.py`
  - `src/services/google_health_client.py`
  - `src/services/google_health_service.py`
  - `tests/unit/test_google_health_service.py`
  - `tests/integration/test_mcp_health_tools.py`
  - `tests/e2e/test_hermes_e2e.py`

