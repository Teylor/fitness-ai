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

- [ ] C1: Database migration (`002_health_metrics.sql`) and Peewee models (`SleepLog`, `WeightLog`) to persist inbound Google Health data with timestamp indexing.
- [ ] C2: `GoogleHealthClient` implementing REST calls to `https://health.googleapis.com/v4/users/me/dataTypes/{dataType}/dataPoints` for `nutrition`, `sleep`, and `weight`, supporting Bearer auth and sandbox simulation.
- [ ] C3: Outbound Meal Synchronization: Service formats meal entries into Google Health nutrition dataPoints (calories, protein, carbs, fat) and successfully uploads them.
- [ ] C4: Inbound Sleep Synchronization: Service fetches sleep sessions from Google Health (duration, start/end timestamps, sleep stages if available), saves to `sleep_logs`, and returns summary.
- [ ] C5: Inbound Weight Synchronization: Service fetches weight measurements (weight in kg, timestamp), saves to `weight_logs`, and returns latest readings.
- [ ] C6: MCP Tools registered in `src/mcp/server.py`:
  - `sync_meals_to_google_health(date)`
  - `fetch_google_health_sleep(date, days)`
  - `fetch_google_health_weight(date, days)`
  - `sync_google_health(date)` (composite sync)
- [ ] C7: Full test suite green (unit tests for client/service, integration tests for MCP tools, and E2E sync scenarios).

## Clarify
> Ambiguities and resolutions (filled interactively with the user)

- **Q1. Google Health Authentication method?**
- **Q2. Local persistence for sleep and weight?**
- **Q3. Offline / Sandbox mode for tests and development?**

## Plan
> Implementation plan (filled after clarify)

- (pending clarification)

## Tasks
> Check the box as each task is completed.

- [ ] T1: Clarify authentication, database models, and sandbox behavior with user
- [ ] T2: Database migration `002_health_metrics.sql` and Peewee models (`SleepLog`, `WeightLog`)
- [ ] T3: Implement `GoogleHealthClient` & `GoogleHealthService` (push nutrition, pull sleep & weight)
- [ ] T4: Implement MCP tools and register in `server.py`
- [ ] T5: Integration tests, E2E tests, spec updates, and verification

## Verification
> Spec contrast (filled at close)

- (pending)

## Close
> Close (filled at close)

- (pending)
