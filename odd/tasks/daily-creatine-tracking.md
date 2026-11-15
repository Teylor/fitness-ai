# daily-creatine-tracking

> Feature: daily-creatine-tracking

## Spec

### Context
Currently (`odd/tasks/supplements-and-water.md`), `MealService.get_day_summary(date)` includes a fixed daily baseline for **water** (`3L` at `1.25 €`, `0 kcal`) inside `water_and_supplements["water"]` and adds `DAILY_WATER_PRICE` (`1.25`) to daily `spend`. Both `#tab-ingredient` ("Agua y Suplementos") and `#tab-summary` ("Agua (3L) y Suplementos") render that fixed daily water row alongside any manually logged supplements.

Creatine is taken daily (1 unit / 5g at 0.30 €) just like water, and having to log it manually every day is repetitive.

### Objective
Include **creatine** as a daily supplement consumption alongside water in the **Agua y Suplementos** section (both in `#tab-ingredient` and `#tab-summary`) and in daily `spend` calculation, enabled by default for every day with a per-day toggle, and using the existing `"Creatina"` ingredient from the catalog when present (falling back to 1 unit / 5g at 0.30 €).

### Acceptance Criteria
- [x] C1: Migration `007_daily_creatine.sql` + `DailyCreatine` model (`date` unique, `enabled` bool default `True`, `updated_at`) registered in `ALL_MODELS`.
- [x] C2: `MealService.toggle_daily_creatine(date, enabled=None) -> bool` (and `is_daily_creatine_enabled(date) -> bool`, defaulting to `True` when no row exists).
- [x] C3: `MealService.get_day_summary(date)` includes `water_and_supplements["creatine"]` (`enabled`, `name`, `quantity`, `unit`, `price`, `kcal`, `protein`, `carbs`, `fat`, `already_logged`). Resolves `"Creatina"` from `Ingredient` catalog if present (1 `u` or 5 `gr`/`ml`), else fallback `1 u (5g)` at `0.30 €`. When `enabled` is `True` (and not already manually logged that day), adds its price to `water_and_supplements["spend"]` and daily `spend` (and its macros to `consumed`).
- [x] C4: MCP tool `toggle_daily_creatine(date: Optional[str] = None, enabled: Optional[bool] = None)` registered in `src/mcp/server.py` (auto-exposed at `POST /api/toggle_daily_creatine`).
- [x] C5: UI (`src/ui/html_generator.py`):
  - `#tab-ingredient` ("💧💊 Agua y Suplementos") shows the daily creatine baseline alongside the 3L water row.
  - `#tab-summary` ("💧💊 Agua y Suplementos") shows the daily creatine row alongside water with a toggle button/switch (`POST /api/toggle_daily_creatine`) that refreshes the summary; subtotal and daily spend update accordingly.
- [x] C6: Unit, integration, and UI tests green (`pytest tests -q`); OpenSpec (`api-spec.md`, `data-model.md`, `requirements.md`) updated.

## Clarify

- **Q1 (Dosis y precio diario)**: Dosis diaria `1 unidad (5gr)` a `0.30 €`.
- **Q2 (Toggle por día)**: Sí, toggle por fecha, **activo por defecto** (`enabled = True` si no hay registro para esa fecha).
- **Q3 (Catálogo)**: Usar el ingrediente `"Creatina"` del catálogo si ya existe (1 `u` -> `ing.price`, o 5 `gr`/`ml` -> `ing.price * 5 / 100`), con fallback a `1 u (5g)` / `0.30 €` si no existe. Si además ese día ya se registró `"Creatina"` manualmente en `meal_entries`, no duplicar su precio/macros.

## Plan

- **T1**: Add `src/db/migrations/007_daily_creatine.sql` and `DailyCreatine` model in `src/db/models.py` (`ALL_MODELS`).
- **T2**: Add `is_daily_creatine_enabled`, `toggle_daily_creatine`, and `water_and_supplements["creatine"]` logic in `src/services/meal_service.py` + unit tests in `tests/unit/test_meal_service.py`.
- **T3**: Add `toggle_daily_creatine` MCP tool in `src/mcp/tools/meal_tools.py`, register in `src/mcp/server.py` + integration tests in `tests/integration/test_mcp_meal_tools.py` & `tests/integration/test_mcp_server.py`.
- **T4**: Update `#tab-ingredient` and `#tab-summary` (`renderSummaryWaterAndSupplements` + `toggleDailyCreatineUI`) in `src/ui/html_generator.py` + UI integration test in `tests/integration/test_ui_web_routes.py`.
- **T5**: Update OpenSpec (`docs/specs/openspec/api-spec.md`, `data-model.md`, `requirements.md`), run full `pytest tests -q`, and close task + `odd/BACKLOG.md`.

## Tasks

- [x] T1: DB migration `007_daily_creatine.sql` + `DailyCreatine` model
- [x] T2: `MealService` daily creatine toggle + `get_day_summary` integration + unit tests
- [x] T3: MCP tool `toggle_daily_creatine` + registration + integration tests
- [x] T4: UI updates in `#tab-ingredient` and `#tab-summary` + UI integration tests
- [x] T5: OpenSpec docs, full `pytest tests -q`, and ODD close

## Verification
- **Tests**: Full pytest suite passing (`209 passed in 3.14s`), including `test_daily_creatine_default_enabled_toggle_and_catalog_lookup`, `test_toggle_daily_creatine_tool`, and `test_ui_daily_creatine_toggle_integration`.
- **MCP**: 30 tools registered (`toggle_daily_creatine` exposed at `POST /api/toggle_daily_creatine`).

## Close
- Closed 2026-11: T1–T5 ✅ and Verification filled.
- Backlog item moved to Done; branch `feat/daily-creatine-tracking` committed and pushed.
