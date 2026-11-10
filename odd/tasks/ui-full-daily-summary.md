# Feature: ui-full-daily-summary

> Comprehensive daily summary dashboard: auto-load today's overview, goals vs remaining macros, meals list, workouts breakdown, and health metrics (steps, sleep, weight).

## Spec
> What and why (no technology)

### Context
- The Fitness AI summary tab previously required manual button clicks and only rendered partial macro consumed numbers and a basic meals table.
- Users want an automatic overview for today as soon as they navigate to the summary.
- Users need to see their full fitness picture in one place: daily macro goals, remaining allowances, meals eaten, workouts completed, and body/activity metrics (steps, sleep, weight).

### Objective
- Automatically load today's summary on page load and tab switch.
- Display macro goals, consumed amounts, and remaining balances (with warning states when exceeded).
- Show individual meals logged for the selected date.
- Show workout sessions completed on the selected date, including exercises, sets, weights, and estimated 1RM.
- Persist and display daily activity/health metrics: step count, sleep duration/stages, and body weight.

### Acceptance Criteria
- [x] C1: **Auto-load Today's Summary**: The summary tab automatically fetches and displays today's metrics on tab switch or page load, and updates dynamically when selecting a new date.
- [x] C2: **Macro Goals, Consumed & Remaining**: Clearly displays daily target, consumed, and remaining values for kcal, protein, carbs, and fat.
- [x] C3: **Day's Meals Listing**: Detailed breakdown of every meal registered on that date with portion, unit, calories, and macros.
- [x] C4: **Day's Workouts**: Lists workout sessions recorded on that date, detailing exercises, sets (reps, weight), notes, and 1RM calculations.
- [x] C5: **Health & Activity Tracking (Steps, Sleep, Weight)**:
  - Add `StepLog` model and `003_step_metrics.sql` migration.
  - Implement `log_steps` and `get_health_metrics` MCP tools and API routes.
  - Render cards for Steps, Sleep, and Weight in the summary tab.
- [x] C6: **Integration Tests**: Verify tools `log_steps`, `get_health_metrics`, and the expanded summary web route.

## Clarify
> Resolved ambiguities

- **Q1. How should steps be recorded?**
  - A: Persisted in SQLite `step_logs` table (date, steps, distance_km, source). A new MCP tool `log_steps` allows Hermes and the UI to log or update daily steps.
- **Q2. How are health metrics retrieved for a given date?**
  - A: A dedicated MCP tool `get_health_metrics(date)` queries local `step_logs`, `sleep_logs`, and `weight_logs` for that date, returning clean structured JSON.
- **Q3. What happens if there are no workouts or health metrics recorded for a day?**
  - A: Render friendly placeholder states ("Sin entrenamientos registrados", "Sin registro de sueño", etc.) rather than broken or blank cards.
- **Q4. Execution mode?**
  - A: Fast mode (default). Implement DB migration, models, MCP tools, UI generator changes, and integration tests.

## Plan
> Technical decisions + classification

- **Classification**: Substantial (DB migration, new `StepLog` entity, new MCP tools `log_steps` and `get_health_metrics`, UI dashboard overhaul, integration tests).
- **D1 (Database & Models)**:
  - Migration `src/db/migrations/003_step_metrics.sql`.
  - Add `StepLog` model in `src/db/models.py` and include in `ALL_MODELS`.
- **D2 (MCP Tools)**:
  - Implement `log_steps(steps, date=None, distance_km=None)` and `get_health_metrics(date=None)` in `src/mcp/tools/health_tools.py`.
  - Register tools in `src/mcp/server.py` (total 25 tools).
- **D3 (UI Dashboard Overhaul)**:
  - Update `src/ui/html_generator.py`:
    - Auto-call `fetchSummary()` on load, tab switch, and date change (`onchange="fetchSummary()"`).
    - Render Goals vs Consumed vs Remaining grid with dynamic badges (green for remaining, red/amber if exceeded).
    - Render Health & Activity grid (Steps with quick log input, Sleep hours & phases, Weight in kg & BMI).
    - Render Meals table with full macronutrient details.
    - Render Workouts container with sessions, exercises, and sets tables.
- **D4 (Tests)**:
  - Tests in `tests/integration/test_mcp_health_tools.py` for `log_steps` and `get_health_metrics`.
  - Tests in `tests/integration/test_ui_web_routes.py` asserting dashboard elements and health metrics flow.

## Tasks
> Implementation checklist

- [x] T1: Create `003_step_metrics.sql` and `StepLog` Peewee model → verify: `pytest tests/unit/test_db_smoke.py`
- [x] T2: Implement `log_steps` and `get_health_metrics` in `src/mcp/tools/health_tools.py` and register in `server.py` → verify: `pytest tests/integration/test_mcp_health_tools.py`
- [x] T3: Overhaul summary dashboard in `src/ui/html_generator.py` with auto-load, remaining macros, meals, workouts, and health metrics → verify: `pytest tests/integration/test_ui_web_routes.py`
- [x] T4: Run full test suite → verify: `pytest tests/ -v`
- [x] T5: Verify live running server on `http://127.0.0.1:9700/ui/summary`

## Verification
> Comparison against the spec

- **C1 (Auto-load Today's Summary)**: `fetchSummary()` executes immediately upon loading the `/ui/summary` view and when switching tabs to `summary`, defaulting to today's date formatted for HTML date picker and automatically querying backend in `DD-MM-YYYY`. Verified via `test_ui_full_daily_summary_dashboard` and live HTTP GET.
- **C2 (Macro Goals, Consumed & Remaining)**: The UI renders 4 macro cards (Calories, Protein, Carbs, Fat) comparing Consumed against Target, computing Remaining, and visually styling exceeded values with warning badges. Verified via `test_ui_full_daily_summary_dashboard`.
- **C3 (Day's Meals Listing)**: Daily meals table lists every logged item with quantity, unit, kcal, macros, and total spend badge. Verified via integration test.
- **C4 (Day's Workouts)**: Lists workout sessions for the date with exercise breakdown, sets, weights, reps, and calculated 1RM. Verified via integration test.
- **C5 (Health & Activity Tracking)**: Steps, sleep duration/stages, and body weight/BMI cards rendered with quick logging functionality. Backed by `StepLog` model, migration `003_step_metrics.sql`, and MCP tools `log_steps` and `get_health_metrics`.
- **C6 (Integration Tests & Full Suite)**: All 158 tests pass (`pytest tests/ -v`).

## Close
> Close

- **Date**: 2026-11-10
- **Result**: Complete and verified.
- **Artifacts**:
  - `src/db/migrations/003_step_metrics.sql`
  - `src/models/health.py` (`StepRecord`)
  - `src/db/models.py` (`StepLog`)
  - `src/mcp/tools/health_tools.py` (`log_steps`, `get_health_metrics`)
  - `src/mcp/server.py` (registered new tools, total 25 tools, added `_to_jsonable` serialization)
  - `src/services/meal_service.py` (serialized dataclass entries in daily summary)
  - `src/ui/html_generator.py` (overhauled summary tab dashboard)
  - `tests/integration/test_mcp_health_tools.py`
  - `tests/integration/test_mcp_server.py`
  - `tests/integration/test_ui_web_routes.py`
  - `tests/e2e/test_hermes_e2e.py`
