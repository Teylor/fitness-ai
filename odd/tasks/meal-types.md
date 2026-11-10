# meal-types

> Feature: meal-types

## Spec
> WHAT and WHY (no technology)

### Context
- Users consume food across distinct eating occasions throughout the day (breakfast, lunch, afternoon snack, dinner, and snacks).
- Currently, meal entries do not store a meal type category, grouping all consumed items together into a single flat list.
- Users want to categorize meals by type: `desayuno`, `comida`, `merienda`, `cena`, or `tentempie`, with `tentempie` as the default.
- In Google Health API (`health.googleapis.com/v4`), `nutrition-log` data points support a `mealType` enum (`BREAKFAST`, `LUNCH`, `BEFORE_DINNER`, `DINNER`, `SNACK`).
- The user requests:
  1. Adding `mealType` with allowed values (`desayuno`, `comida`, `merienda`, `cena`, `tentempie`) defaulting to `tentempie`.
  2. Mapping `merienda` to Google Health `BEFORE_DINNER`, `desayuno` to `BREAKFAST`, `comida` to `LUNCH`, `cena` to `DINNER`, and `tentempie` to `SNACK`.
  3. Updating the meal registration form in the UI with a meal type selector.
  4. Updating the daily summary UI to group and divide meals by `mealType`, with subtotals per category.

### Objective
Extend meal entries with a `meal_type` attribute, persist it in SQLite, support it in MCP tools and Google Health synchronization, and update the UI registration form and daily summary view with categorized grouping.

### Acceptance criteria

- [x] C1: Database migration (`004_meal_types.sql`) adding column `meal_type VARCHAR(50) NOT NULL DEFAULT 'tentempie'` to `meal_entries`. Models (`MealEntryModel`, `MealEntry` dataclass) updated.
- [x] C2: `MealService.register` and `register_meal` MCP tool accept optional `meal_type` (default `'tentempie'`), validating that it belongs to (`desayuno`, `comida`, `merienda`, `cena`, `tentempie`).
- [x] C3: `MealService.get_day_summary` returns meals categorized by `meal_type` with subtotals for calories and macros, while preserving the flat `meals` list.
- [x] C4: `GoogleHealthService.sync_meals` sets `mealType` on each Google Health `nutritionLog` payload using the official enum:
  - `desayuno` -> `BREAKFAST`
  - `comida` -> `LUNCH`
  - `merienda` -> `BEFORE_DINNER`
  - `cena` -> `DINNER`
  - `tentempie` -> `SNACK`
- [x] C5: Web UI (`src/ui/html_generator.py`):
  - Meal registration form contains a dropdown selector `<select id="meal-eating-type">` with `tentempie` preselected by default.
  - Daily Summary divides meals into blocks/sections by `mealType`, displaying items and category subtotals.
- [x] C6: Test suite green with unit, integration, and E2E tests covering meal type validation, summary breakdown, and Google Health sync payloads.
- [x] C7: Specifications updated in `docs/specs/openspec/` (`requirements.md`, `data-model.md`, `api-spec.md`).

## Clarify
> Ambiguities and resolutions

- **Q1: What are the exact allowed meal type values?**
  - **A**: `desayuno`, `comida`, `merienda`, `cena`, `tentempie`. Default is `tentempie`.
- **Q2: How does `merienda` map to Google Health API v4?**
  - **A**: Per user decision, `merienda` maps to `BEFORE_DINNER`.
- **Q3: What happens to existing meal entries created before this migration?**
  - **A**: The migration sets `DEFAULT 'tentempie'`, so existing entries seamlessly have `meal_type = 'tentempie'`.
- **Q4: How should Daily Summary render empty meal categories?**
  - **A**: Categories with logged meals are prominently displayed with their item rows and macro totals. If a category has no meals, it can either be hidden or show an empty state.

## Plan
> Implementation plan

- **T1 — Database Migration & Models**:
  - Create `src/db/migrations/004_meal_types.sql`.
  - Update `MealEntry` in `src/db/models.py` and `src/models/meal_entry.py`.
- **T2 — Domain Services & MCP Tools**:
  - Update `src/services/meal_service.py` to validate and store `meal_type`, and compute `meals_by_type` in `get_day_summary`.
  - Update `src/mcp/tools/meal_tools.py` `register_meal` to accept `meal_type`.
  - Update `src/services/google_health_service.py` to map `meal_type` to Google Health enums (`BREAKFAST`, `LUNCH`, `BEFORE_DINNER`, `DINNER`, `SNACK`).
- **T3 — Web UI**:
  - Add `<select id="meal-type">` in meal logging form with default `tentempie`.
  - Update `renderSummaryMeals` to group items by meal type with category headers, subtotals, and delete buttons.
- **T4 — Tests & Verification**:
  - Update unit tests in `test_meal_service.py`, `test_mcp_meal_tools.py`, `test_google_health_service.py`, `test_ui_web_routes.py`.
  - Verify all 172+ tests green.
- **T5 — OpenSpec Updates & Task Closure**:
  - Update `requirements.md`, `data-model.md`, `api-spec.md`.
  - Update `odd/BACKLOG.md` and submit PR.

## Tasks
> Check the box as each task is completed.

- [x] T1: Database migration `004_meal_types.sql` & models update
- [x] T2: MealService & MCP `register_meal` & Google Health mapping
- [x] T3: Web UI update (registration dropdown & grouped summary)
- [x] T4: Test suite updates and verification
- [x] T5: OpenSpec documentation updates and task closure

## Verification
> Spec contrast (filled at close)

- [x] C1: Migration `004_meal_types.sql` created and applied; `MealEntryModel` and `MealEntry` domain dataclass include `meal_type` default `'tentempie'`.
- [x] C2: `MealService.register` validates `meal_type in ('desayuno', 'comida', 'merienda', 'cena', 'tentempie')`; MCP `register_meal` tool accepts `meal_type`.
- [x] C3: `MealService.get_day_summary` calculates `meals_by_type` subtotals for calories, macros, and spend per meal type category.
- [x] C4: `GoogleHealthService.sync_meals` correctly maps `desayuno` -> `BREAKFAST`, `comida` -> `LUNCH`, `merienda` -> `BEFORE_DINNER`, `cena` -> `DINNER`, `tentempie` -> `SNACK`. Verified in `test_sync_meals_maps_all_meal_types_to_google_health`.
- [x] C5: Web UI meal registration form has `<select id="meal-eating-type">` with default `tentempie`; Daily Summary renders distinct categorized sections per meal type.
- [x] C6: 176 tests passing across unit, integration, and Hermes E2E suites.
- [x] C7: OpenSpec documentation updated in `requirements.md` (FR2.4, FR2.6, FR7.2), `data-model.md`, and `api-spec.md`.

## Close
> Close (filled at close)

- Date: 2026-11
- Branch: `feat/meal-types`
- Next step: Submit PR to `main`.
