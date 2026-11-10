# steps-google-health-pull

> Feature: steps-google-health-pull

## Spec
> WHAT and WHY (no technology)

### Context
- The user wears a fitness tracking device (Google Fit Air) that records daily steps automatically to Google Health.
- Currently, the application allows manual entry of daily steps through an input field in the Web UI (`#quick-steps-input`) and via the `log_steps` tool.
- Entering steps manually is redundant and prone to inconsistencies with the wearable's tracked data.
- The user requests disabling manual step entry and exclusively pulling daily steps from the Google Health API (cloud REST `health.googleapis.com/v4`).

### Objective
Disable manual step creation in the UI and backend tool, implement inbound Google Health steps synchronization (`fetch_steps`), and integrate step synchronization into the global synchronization flow (`sync_all` and UI sync button).

### Acceptance criteria

- [x] C1: `GoogleHealthClient` implements `get_steps_datapoints()` querying `https://health.googleapis.com/v4/users/me/dataTypes/steps/dataPoints`.
- [x] C2: `GoogleHealthService` implements `fetch_steps(date)`:
  - Queries Google Health steps dataPoints.
  - Aggregates (sums) step counts matching the requested date interval.
  - Persists/updates the daily count into `step_logs` with `source="google_health"`.
  - Tolerates absence of data points (defaults to 0 steps or preserves existing if no new data).
- [x] C3: `GoogleHealthService.sync_all(date)` incorporates `fetch_steps` and returns `steps_fetched`.
- [x] C4: New MCP tool `fetch_google_health_steps(date)` registered in `src/mcp/server.py`.
- [x] C5: Manual step entry disabled:
  - In `src/mcp/tools/health_tools.py`, `log_steps` rejects manual step logging with error code `manual_steps_disabled`.
  - In `src/ui/html_generator.py`, remove the manual input field (`#quick-steps-input`) and "+ Guardar" / "Editar" buttons from the 👟 Steps card.
  - Display step counts with a "Google Health" indicator and a prompt to use "☁️ Sincronizar Google Health" when no data is recorded.
- [x] C6: Full test suite passing (all unit, integration, and UI tests updated and green).
- [x] C7: Specifications updated in `docs/specs/openspec/` (`requirements.md` and `api-spec.md`).

## Clarify
> Ambiguities and resolutions

- **Q1: What structure does Google Health API v4 return for steps?**
  - **A**: `GET /users/me/dataTypes/steps/dataPoints` returns `{ "dataPoints": [ { "steps": { "count": "154", "interval": { "startTime": "...", "endTime": "..." } } } ] }`. Daily totals are calculated by summing `int(pt["steps"]["count"])` for intervals occurring on the target date.
- **Q2: Should `log_steps` be deleted or return an error?**
  - **A**: Retain `log_steps` in the tool schema to prevent breaking MCP clients/schemas, but return `{"status": "error", "code": "manual_steps_disabled", "message": "Manual step logging is disabled. Steps are synchronized automatically from Google Health."}`.
- **Q3: What happens when the user clicks the "☁️ Sincronizar Google Health" button in the UI?**
  - **A**: The button calls `POST /api/sync_google_health`, which calls `sync_all(date)`. With this change, `sync_all` will automatically fetch steps from Google Health, store them in the local database, and immediately display them on the dashboard.

## Plan
> Implementation plan

- **T1 — Google Health Client & Service**:
  - Add `get_steps_datapoints()` to `src/services/google_health_client.py`.
  - Add `fetch_steps(date)` to `src/services/google_health_service.py`.
  - Update `sync_all(date)` to invoke `fetch_steps` and report `steps_fetched`.
- **T2 — MCP Tools & Server**:
  - Add `fetch_google_health_steps(date)` tool in `src/mcp/tools/health_tools.py`.
  - Update `log_steps` to return `manual_steps_disabled`.
  - Register `fetch_google_health_steps` in `src/mcp/server.py`.
- **T3 — Web UI Update**:
  - Remove `#quick-steps-input` and save/edit buttons in `src/ui/html_generator.py`.
  - Update 👟 Steps card to display Google Health source attribution and hint to sync.
  - Remove obsolete `quickLogSteps` JS function.
- **T4 — Test Updates & New Tests**:
  - Add unit tests for `get_steps_datapoints` and `fetch_steps` in `tests/unit/test_google_health_service.py`.
  - Add integration tests for `fetch_google_health_steps` and `log_steps` rejection in `tests/integration/test_mcp_health_tools.py`.
  - Update `tests/e2e/test_hermes_e2e.py` tool count (27 tools) and `tests/integration/test_ui_web_routes.py`.
- **T5 — OpenSpec & Backlog**:
  - Update `docs/specs/openspec/requirements.md` and `docs/specs/openspec/api-spec.md`.
  - Update `odd/BACKLOG.md` and close task.

## Tasks
> Check the box as each task is completed.

- [x] T1: Google Health Client `get_steps_datapoints()` & Service `fetch_steps()`
- [x] T2: MCP tools (`fetch_google_health_steps`, `log_steps` rejection) and server registration
- [x] T3: Web UI cleanup (remove manual input, show Google Health source and sync prompt)
- [x] T4: Test suite updates and verification
- [x] T5: OpenSpec documentation updates and task closure

## Verification
> Spec contrast (filled at close)

- [x] C1: `GoogleHealthClient.get_steps_datapoints` verified in unit tests fetching `/users/me/dataTypes/steps/dataPoints`.
- [x] C2: `GoogleHealthService.fetch_steps` aggregates step intervals by date, saves/updates `StepLog(source="google_health")`, verified in `test_fetch_steps_persists_records`.
- [x] C3: `GoogleHealthService.sync_all` includes `fetch_steps` and returns `steps_fetched`, verified in unit and E2E tests.
- [x] C4: `fetch_google_health_steps` registered in `MCPServer` (27 total tools) and verified in `test_server_registers_all_twenty_seven_tools` and Hermes handshake.
- [x] C5: Manual step input field and buttons removed from `src/ui/html_generator.py`; `log_steps` returns `manual_steps_disabled`.
- [x] C6: 172 tests passing across unit, integration, and E2E suites.
- [x] C7: `docs/specs/openspec/requirements.md` (FR7.4) and `docs/specs/openspec/api-spec.md` updated with `fetch_google_health_steps` and `log_steps` deprecation.

## Close
> Close (filled at close)

- Date: 2026-11
- Branch: `fix/steps-google-health-pull`
- Next step: Submit PR to `main`.
