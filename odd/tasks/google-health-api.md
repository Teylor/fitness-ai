# google-health-api

> Feature: google-health-api

## Spec
> WHAT and WHY (no technology)

### Context

- The fitness AI system tracks nutrition (ingredients, recipes, meals, daily goals) and workouts.
- Users want seamless interoperability with Google's health ecosystem using the **Google Health API** (cloud REST `health.googleapis.com/v4`), strictly avoiding the deprecated Google Fit API.
- Two core integration directions are required:
  1. **Outbound / Push:** Sync meals logged in this app to Google Health as nutrition data points (calories, protein, carbs, fat, meal names, and timestamps).
  2. **Inbound / Pull:** Fetch user weight records and sleep sessions from Google Health, bringing body metrics and recovery tracking into the system.
- Backlog item #10 specifies: "Connect Google Health API to sync and add meals. Sync meals added from this app and receive sleep and weight data from the Google Health API."

### Objective

Build a `GoogleHealthService` and client adapter integrated with Peewee storage (`sleep_logs`, `weight_logs`) and exposed via MCP tools (`sync_meals_to_google_health`, `fetch_google_health_sleep`, `fetch_google_health_weight`, `sync_google_health`). Ensure support for OAuth2 token authorization with an automated mock/sandbox adapter for offline testing and development.

### Acceptance criteria

- [x] C1: Database migration (`002_health_metrics.sql`) and Peewee models (`SleepLog`, `WeightLog`) to persist inbound Google Health data with timestamp indexing.
- [x] C2: `GoogleHealthClient` implementing REST calls to `https://health.googleapis.com/v4/users/me/dataTypes/{dataType}/dataPoints` for `nutrition`, `sleep`, and `weight`, supporting Bearer auth.
- [x] C3: Outbound Meal Synchronization: Service formats meal entries into Google Health nutrition dataPoints (calories, protein, carbs, fat) and successfully uploads them.
- [x] C4: Inbound Sleep Synchronization: Service fetches sleep sessions from Google Health (duration, start/end timestamps, sleep stages if available), saves to `sleep_logs`, and returns summary.
- [x] C5: Inbound Weight Synchronization: Service fetches weight measurements (weight in kg, timestamp), saves to `weight_logs`, and returns latest readings.
- [x] C6: MCP Tools registered in `src/mcp/server.py`:
  - `sync_meals_to_google_health(date)`
  - `fetch_google_health_sleep(date, days)`
  - `fetch_google_health_weight(date, days)`
  - `sync_google_health(date)` (composite sync)
- [x] C7: Full test suite green (unit tests for client/service, integration tests for MCP tools, and E2E sync scenarios).

## Clarify
> Ambiguities and resolutions (filled interactively with the user)

- **Q1. Google Health Authentication method?** A: Environment variables (`GOOGLE_HEALTH_ACCESS_TOKEN` or `.env` configuration for `client_id` / `client_secret` / `refresh_token`), read via `src.config.settings`.
- **Q2. Local persistence for sleep and weight?** A: Yes, create migration `002_health_metrics.sql` with tables `sleep_logs` and `weight_logs` plus Peewee models (`SleepLog`, `WeightLog`) so Hermes can query historical body metrics.
- **Q3. Offline / Sandbox mode for tests and development?** A: No sandbox fallback in production code. If no token/credentials are configured, raise an explicit authentication error (`code: "auth_error"` or `code: "invalid_input"`). Unit and integration tests mock HTTP requests using a test access token.

## Plan
> Implementation plan (filled after clarify)

- **Mode:** fast — TDD per task, migration, service + client, MCP tools, and full suite pass.
- **T1 — Clarification & Architecture:** (Completed) User alignment on env token, DB persistence (`002_health_metrics.sql`), and strict error on missing credentials.
- **T2 — Database Migration & Models:** Create `src/db/migrations/002_health_metrics.sql`, add `SleepLog` and `WeightLog` to `src/db/models.py` and `ALL_MODELS`, create domain dataclasses in `src/models/health.py`.
- **T3 — Google Health Client & Service:** Implement `GoogleHealthClient` in `src/services/google_health_client.py` and `GoogleHealthService` in `src/services/google_health_service.py`:
  - `sync_meals(date)`: Formats meal entries into `nutrition` dataPoints (`calories`, `protein`, `carbs`, `fat`, `name`) and POSTs to `health.googleapis.com/v4/users/me/dataTypes/nutrition/dataPoints`.
  - `fetch_sleep(date, days)`: Queries `sleep` dataPoints from Google Health, stores sessions in `sleep_logs`.
  - `fetch_weight(date, days)`: Queries `weight` dataPoints from Google Health, stores measurements in `weight_logs`.
  - `sync_all(date)`: Coordinates meal sync and fetches sleep & weight.
- **T4 — MCP Tools:** Implement tools in `src/mcp/tools/health_tools.py`:
  - `sync_meals_to_google_health(date)`
  - `fetch_google_health_sleep(date, days)`
  - `fetch_google_health_weight(date, days)`
  - `sync_google_health(date)`
  Register them in `src/mcp/server.py`.
- **T5 — Tests, Polish & Spec updates:** Unit tests with mocked HTTP endpoints, integration tests for MCP tools, update `api-spec.md` and `data-model.md`, full test suite pass.

## Tasks
> Check the box as each task is completed.

- [x] T1: Clarify authentication, database models, and sandbox behavior with user
- [x] T2: Database migration `002_health_metrics.sql` and Peewee models (`SleepLog`, `WeightLog`)
- [x] T3: Implement `GoogleHealthClient` & `GoogleHealthService` (push nutrition, pull sleep & weight)
- [x] T4: Implement MCP tools (`health_tools.py`) and register on server
- [x] T5: Tests, polish, spec updates, and full suite pass

## Verification
> Spec contrast (filled at close)

- [x] C1: `src/db/migrations/002_health_metrics.sql` created and applied; `SleepLog` and `WeightLog` models added to `src/db/models.py` and `ALL_MODELS`. Verified in `tests/unit/test_db_smoke.py` (11 tables).
- [x] C2: `GoogleHealthClient` implemented in `src/services/google_health_client.py` using `health.googleapis.com/v4/users/me/dataTypes/{dataType}/dataPoints` for `nutrition`, `sleep`, and `weight` with Bearer auth; raises `ValidationError` when unauthenticated.
- [x] C3: `sync_meals` computes meal macros and uploads nutrition dataPoints; verified in `test_google_health_service.py` and `test_mcp_health_tools.py`.
- [x] C4: `fetch_sleep` retrieves sleep sessions and saves them into `SleepLog`; verified in `test_google_health_service.py`.
- [x] C5: `fetch_weight` retrieves body weight records and saves them into `WeightLog`; verified in `test_google_health_service.py`.
- [x] C6: 4 MCP tools (`sync_meals_to_google_health`, `fetch_google_health_sleep`, `fetch_google_health_weight`, `sync_google_health`) implemented in `src/mcp/tools/health_tools.py` and registered in `src/mcp/server.py` (23 total tools).
- [x] C7: Test suite passes with 153 tests green across unit, integration, and E2E suites; OpenSpec documentation updated in `api-spec.md`, `data-model.md`, and `requirements.md`.

## Close
> Close (filled at close)

- Date: 2026-11
- Next step: Review remaining backlog items (#7 `db-robustness`, #9 `odd-merge-back`, #8 `seed-data`).
