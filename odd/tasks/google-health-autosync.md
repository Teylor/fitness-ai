# Feature: google-health-autosync

> Automatic background meal synchronization to Google Health upon intake registration and UI one-click sync button.

## Spec
> What and why (no technology)

### Context
- Users currently register meals via the web UI or voice agent, which stores the meals in local SQLite.
- Meal synchronization to Google Health currently requires an explicit manual command (`sync_meals_to_google_health` or `sync_google_health`).
- Users expect real-time synchronization so that as soon as a meal is logged, it reflects in Google Health without extra steps.
- Additionally, users want a visible, one-click "Sincronizar Google Health" button in the web UI dashboard to trigger full synchronization (meals, sleep, weight) and immediately refresh metrics.

### Objective
- When registering a meal (`register_meal`), automatically sync the day's meals to Google Health if Google Health credentials are configured, without failing local meal registration if cloud synchronization encounters transient network issues.
- When deleting a meal (`delete_meal`), automatically synchronize the updated day's meals with Google Health.
- Add a prominent "Sincronizar Google Health" button in the web UI header/dashboard that triggers `sync_google_health` for the active date and refreshes the daily summary view upon completion.

### Acceptance Criteria
- [x] C1: **Automatic Sync on Meal Registration**: Calling `register_meal` when Google Health credentials are configured automatically pushes the meal to Google Health API v4 as a `nutrition-log` data point.
- [x] C2: **Local Fault Tolerance**: Network or API errors during Google Health auto-sync do not roll back or fail the local meal creation.
- [x] C3: **Automatic Re-sync on Meal Deletion**: Calling `delete_meal` re-synchronizes the date's meals with Google Health so deleted entries are cleared from Google Health.
- [x] C4: **UI One-Click Sync Button**: An interactive button "Sincronizar Google Health" is present in the web UI header/dashboard.
- [x] C5: **UI Feedback and View Refresh**: Clicking the UI sync button executes `sync_google_health`, displays progress and results (meals uploaded, sleep, weight), and refreshes the active day's summary.
- [x] C6: **Test Coverage**: Unit and integration tests verify automatic synchronization triggers, fault tolerance, and UI elements.

## Clarify
> Ambiguities resolved

- **Q1. Should auto-sync block the response of `register_meal`?**
  - A: It runs synchronously within the tool handler (or catches exceptions gracefully), returning a `google_health_synced` status in the response without failing the core `register_meal` transaction if Google Health returns an error.
- **Q2. What should the UI button sync?**
  - A: It should call `sync_google_health(date=currentDate)` so it uploads meals AND fetches the latest sleep and weight records from Google Health, refreshing the entire dashboard.

## Plan
> Technical decisions + classification

- **Classification**: Normal (adds auto-trigger in meal tool/service and UI button in HTML generator).
- **D1 (Meal Tool Auto-Sync)**:
  - In `src/mcp/tools/meal_tools.py`:
    - After `meal_service.register_meal` succeeds, if `settings.google_health_token` or `settings.google_health_refresh_token` is present, attempt `GoogleHealthService().sync_meals(date)`.
    - Catch any `Exception` and include `google_health_synced: True/False` in response.
    - In `delete_meal`: perform `sync_meals(date)` or clear/resync for that date.
- **D2 (UI Button & Feedback)**:
  - In `src/ui/html_generator.py`:
    - Add a button in the header toolbar: `<button onclick="syncGoogleHealth()" class="btn btn-secondary">... Sincronizar Google Health</button>`.
    - Implement `syncGoogleHealth()` in JS to call `/api/sync_google_health` with the current date, show visual toast/status, and invoke `fetchSummary()`.
- **D3 (Tests)**:
  - Add tests in `tests/unit/test_meal_service.py` or `tests/integration/test_mcp_health_tools.py`.
  - Verify full test suite passes.

## Tasks
> Implementation checklist

- [x] T1: Add auto-sync to `register_meal` and `delete_meal` in `src/mcp/tools/meal_tools.py`.
- [x] T2: Add "Sincronizar Google Health" button and JS handler in `src/ui/html_generator.py`.
- [x] T3: Add unit and integration tests verifying auto-sync and resilience.
- [x] T4: Verify full test suite and live UI.

## Verification
> Spec contrast (filled at close)

- **C1 (Automatic Sync on Meal Registration)**: `register_meal` triggers `GoogleHealthService().sync_meals(date)` when Google Health credentials are configured. Verified by integration test `test_register_and_delete_meal_with_google_health_autosync`.
- **C2 (Local Fault Tolerance)**: If cloud synchronization raises an exception, the meal registration still completes and succeeds locally, returning `google_health_synced: False`. Verified by integration test `test_register_meal_google_health_failure_is_fault_tolerant`.
- **C3 (Automatic Re-sync on Meal Deletion)**: Deleting a meal via `delete_meal` re-synchronizes the date's meals with Google Health. Verified by integration test `test_register_and_delete_meal_with_google_health_autosync`.
- **C4 (UI One-Click Sync Button)**: Added "☁️ Sincronizar Google Health" buttons in both the top header and the Daily Summary action bar. Verified in `test_ui_web_routes_and_api_dispatch`.
- **C5 (UI Feedback and View Refresh)**: Clicking the UI button invokes `POST /api/sync_google_health`, disables buttons during execution, displays toast notifications with sync metrics, and calls `fetchSummary()` to refresh active dashboard metrics.
- **C6 (Test Coverage)**: 170/170 tests passing.

## Close
> Close (filled at close)

- **Date**: 2026-11-10
- **Status**: Closed. 4/4 tasks ✅, 6/6 spec criteria ✅.
- **Artifacts**:
  - `src/mcp/tools/meal_tools.py`
  - `src/services/google_health_service.py`
  - `src/ui/html_generator.py`
  - `tests/integration/test_mcp_meal_tools.py`
  - `tests/integration/test_ui_web_routes.py`
  - `docs/specs/openspec/requirements.md`
