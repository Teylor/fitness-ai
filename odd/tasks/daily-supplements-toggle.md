# daily-supplements-toggle

> Feature: daily-supplements-toggle

## Spec

### Context
Currently (`odd/tasks/daily-creatine-tracking.md`), **Creatina** appears automatically in the Daily Summary **"Agua y Suplementos"** list with a per-day toggle defaulting to ON (`True`). Other catalog supplements (`is_supplement = true`, e.g. Omega 3, Vitamina D, etc.) only appear in the daily list if manually logged via *Registrar Comida*.

### Objective
Show all catalog supplements (`is_supplement = true`) in the Daily Summary **"Agua y Suplementos"** list with a per-day toggle that defaults to **OFF** (`False`) — except **Creatina**, which continues defaulting to **ON** (`True`) — so toggling a supplement ON for a day immediately includes its macros and price in the daily summary and spend.

### Acceptance Criteria
- [x] C1: Migration `008_daily_supplement_toggles.sql` + `DailySupplementToggle` model (`date`, `ingredient` FK, `enabled` bool default `False`, `updated_at`, unique `(date, ingredient)`) in `ALL_MODELS`.
- [x] C2: `MealService.toggle_daily_supplement(date, ingredient_id, enabled=None) -> bool` (delegates to `toggle_daily_creatine` if ingredient is Creatina; otherwise toggles `DailySupplementToggle` defaulting to `False`).
- [x] C3: `MealService.get_day_summary(date)` includes `water_and_supplements["daily_supplements"]` (all non-Creatina catalog supplements with `ingredient_id`, `name`, `quantity`, `unit`, `price`, `kcal`, `protein`, `carbs`, `fat`, `enabled`, `already_logged`). Enabled items (not already manually logged) are added to `consumed`, `spend`, and `water_and_supplements` totals.
- [x] C4: MCP tool `toggle_daily_supplement(ingredient_id: int, date: Optional[str] = None, enabled: Optional[bool] = None)` registered in `src/mcp/server.py` (`POST /api/toggle_daily_supplement`).
- [x] C5: `#tab-summary` (`renderSummaryWaterAndSupplements`) renders each catalog supplement with a checkbox toggle (`toggleDailySupplementUI`) defaulting to unchecked, refreshing the summary on change.
- [x] C6: Unit, integration, and UI tests green (`pytest tests -q`); OpenSpec (`api-spec.md`, `requirements.md`) updated.

## Clarify
- Non-unit (`gr`/`ml`) catalog supplements use `100.0` (1 serving unit per catalog convention) while `u` supplements use `1.0`.
- Creatina continues using `DailyCreatine` (`enabled = True` by default).

## Plan
- **T1**: Add `008_daily_supplement_toggles.sql` and `DailySupplementToggle` in `src/db/models.py`.
- **T2**: Add unit tests (RED) and implement `toggle_daily_supplement` + `daily_supplements` in `src/services/meal_service.py` (GREEN).
- **T3**: Add `toggle_daily_supplement` MCP tool in `src/mcp/tools/meal_tools.py` + `server.py` + integration tests.
- **T4**: Update `renderSummaryWaterAndSupplements` & add `toggleDailySupplementUI` in `src/ui/html_generator.py` + UI test.
- **T5**: Update OpenSpec, run `pytest tests -q`, and close ODD docs.

## Tasks
- [x] T1: Migration `008_daily_supplement_toggles.sql` + `DailySupplementToggle` model
- [x] T2: `MealService.toggle_daily_supplement` + `daily_supplements` in `get_day_summary` + unit tests
- [x] T3: MCP tool `toggle_daily_supplement` + registration + integration tests
- [x] T4: UI rendering + `toggleDailySupplementUI` + UI integration test
- [x] T5: OpenSpec docs, full `pytest tests -q`, and ODD close

## Verification
- `pytest tests -q`: `219 passed in 3.29s`.
- Verified `008_daily_supplement_toggles.sql`, `DailySupplementToggle`, `MealService.toggle_daily_supplement`, `get_day_summary` `daily_supplements`, MCP tool `toggle_daily_supplement` (`POST /api/toggle_daily_supplement`), and Web UI checkbox toggles (`toggleDailySupplementUI`).

## Close
- Closed on branch `feat/daily-supplements-toggle` with OpenSpec (`api-spec.md`, `requirements.md`) and `odd/BACKLOG.md` updated.
