# Feature: ui-body-progress-tracking

> Implement full body progress tracking in `#tab-progress`: allow logging daily body measurements (Weight, Waist, Chest, Arm, Leg), visualizing them in an interactive monthly chart with clickable day points, and inspecting/editing/deleting the measurements for any selected day.

## Spec
> What and why (no technology)

- [x] C1: Persist daily body progress records containing `date` (`DD-MM-YYYY`, unique per day) and optional numeric measurements: **Weight (kg)**, **Waist (cm)**, **Chest (cm)**, **Arm (cm)**, **Leg (cm)**, plus optional **Notes**. At least one measurement must be provided and any provided measurement must be strictly positive (`> 0`).
- [x] C2: Logging progress for a date that already has a record updates (upserts) that day's entry cleanly instead of creating duplicates.
- [x] C3: Expose MCP tools (and corresponding `/api/*` endpoints) to log (`log_body_progress`), list by month (`list_body_progress`), and delete (`delete_body_progress`) body progress records.
- [x] C4: Replace the "Coming Soon" placeholder in `#tab-progress` with a self-contained Body Progress view containing:
  - A form to log or edit measurements (`Fecha`, `Peso (kg)`, `Cintura (cm)`, `Pecho (cm)`, `Brazo (cm)`, `Pierna (cm)`, `Notas`).
  - A monthly interactive chart (`1..N` days of the selected month) with previous/next month navigation and a metric selector (`Peso`, `Cintura`, `Pecho`, `Brazo`, `Pierna`) plotting a trend line and clickable points on every day with recorded progress.
  - A selected-day detail panel that opens/updates when clicking any point on the chart, displaying all 5 measurements (and notes) for that date, plus quick **Edit** and **Delete** actions.
- [x] C5: Selecting a month automatically loads its records and pre-selects the most recent logged day in that month (or displays a clear empty state if no entries exist).
- [x] C6: Unit tests for `BodyProgressService` and integration tests for MCP tools, HTTP API, and `#tab-progress` UI rendering pass alongside the full test suite.

## Clarify
> Resolved ambiguities

- Q1: Allow partial measurements per day? → A: Yes, at least 1 positive measurement required; unlogged metrics display `-`.
- Q2: Duplicate entries on the same date? → A: Upsert by `date` (one entry per day).
- Q3: Plotting 5 metrics with different units? → A: Weight (`kg`) plotted by default with quick selector pills (`Peso`, `Cintura`, `Pecho`, `Brazo`, `Pierna`); clicking any day point always shows all 5 measurements.
- Q4: Chart library? → A: Self-contained responsive inline SVG (zero external dependencies, offline/PWA-ready).
- Q5: Extra fields? → A: Optional `Notas` included alongside the 5 requested measurements.

## Plan
> Technical decisions + classification

- Classification: **Substantial** — introduces a new database table + SQL migration, domain model, service, 3 MCP tools, and a full interactive UI view with custom SVG chart.
- D1 (DB & Migration): `src/db/migrations/009_body_progress.sql` + `BodyProgressLog` Peewee model in `src/db/models.py` (added to `ALL_MODELS`).
- D2 (Domain & Service): `src/models/body_progress.py` (`BodyProgressRecord`) + `src/services/body_progress_service.py` (`BodyProgressService`).
- D3 (MCP Tools & API): `src/mcp/tools/body_progress_tools.py` (`log_body_progress`, `list_body_progress`, `delete_body_progress`) registered in `src/mcp/server.py`.
- D4 (Web UI): Full `#tab-progress` form, monthly SVG chart (`renderProgressChart()`), clickable points (`selectProgressDay()`), and selected-day detail card (`renderProgressDayDetail()`) in `src/ui/html_generator.py`.
- D5 (Docs): Updated `docs/specs/openspec/data-model.md`, `docs/specs/openspec/api-spec.md`, and `docs/design/odd-models.md`.

## Tasks
> Implementation checklist

- [x] T1: Create migration `009_body_progress.sql`, Peewee model `BodyProgressLog` in `src/db/models.py`, and domain dataclass `BodyProgressRecord` in `src/models/body_progress.py` → verify: `pytest tests/unit/test_db_smoke.py tests/unit/test_db_robustness.py -v` → PASSED
- [x] T2: Implement `BodyProgressService` in `src/services/body_progress_service.py` and unit tests in `tests/unit/test_body_progress_service.py` → verify: `pytest tests/unit/test_body_progress_service.py -v` → PASSED (5 tests)
- [x] T3: Add MCP tools in `src/mcp/tools/body_progress_tools.py`, register them in `src/mcp/server.py`, update `tests/integration/test_mcp_server.py` & `tests/e2e/test_hermes_e2e.py`, and add `tests/integration/test_mcp_body_progress_tools.py` → verify: `pytest tests/integration/test_mcp_body_progress_tools.py tests/integration/test_mcp_server.py tests/e2e/test_hermes_e2e.py -v` → PASSED
- [x] T4: Implement `#tab-progress` form, monthly interactive SVG chart, and clickable day detail panel in `src/ui/html_generator.py`, and add integration tests in `tests/integration/test_ui_web_routes.py` → verify: `pytest tests/integration/test_ui_web_routes.py -v` + `node --check` → PASSED (`JS_SYNTAX_OK`)
- [x] T5: Update OpenSpec / ODD docs (`data-model.md`, `api-spec.md`, `odd-models.md`) and run full test suite → verify: `pytest tests/ -v` → PASSED (232 passed)

## Verification
> Comparison against the spec (filled in at close)

- **C1 & C2**: `body_progress_logs` table + `BodyProgressService.log_progress()` enforces `DD-MM-YYYY`, positive values, at least one metric, and upserts by `date` (verified by `tests/unit/test_body_progress_service.py`).
- **C3**: `log_body_progress`, `list_body_progress`, and `delete_body_progress` registered in MCP server and `/api/*` (verified by `tests/integration/test_mcp_body_progress_tools.py`, `test_mcp_server.py`, and `test_hermes_e2e.py`).
- **C4 & C5**: `#tab-progress` renders the form, monthly SVG chart with clickable points and metric pills, and selected-day detail card with Edit/Delete actions (verified by `test_ui_body_progress_tracking_view_and_api` and `node --check`).
- **C6**: Full suite `pytest tests/ -v` → **232 passed**.

## Close
> Close (filled in at close)

- **Date**: 2026-11-20
- **Implemented**: Full body progress tracking (DB migration, service, 3 MCP tools, interactive monthly SVG chart with clickable day points and full measurement details in `#tab-progress`).
- **Next step**: Commit on `feat/ui-body-progress-tracking`, push, and open a PR to `main`.
