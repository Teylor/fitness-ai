# supplements-and-water

> Feature: supplements-and-water

## Spec
> WHAT and WHY (no technology)

### Context
- Users take daily supplements (e.g., Creatine, Omega 3) and consume a fixed daily baseline of 3L of water costing 1.25€.
- Currently, all ingredients are treated identically as regular food items, mixing supplements with culinary ingredients in the catalog and daily meal summaries.
- Furthermore, daily water consumption (3L at 1.25€/day) is not tracked or reflected in the daily summary or daily spend.
- The user requested:
  1. Adding a boolean checkbox flag (`is_supplement`) to ingredients so items like Creatine or Omega 3 can be marked as supplements.
  2. Displaying supplements in a dedicated separate section **"Agua y Suplementos"** (both in the Ingredients catalog and in the Daily Summary).
  3. Including a fixed daily consumption of **3L of water per day with a price of 1.25€** inside the "Agua y Suplementos" section and in the daily spend calculation.
  4. Adding a backlog item for fixing the data mismatch between the UI and Google Health.

### Objective
Extend the `Ingredient` model with an `is_supplement` boolean flag, expose it across services, MCP tools, and the UI form, display supplements together with a fixed 3L daily water entry (1.25€) in a dedicated "Agua y Suplementos" section in both the catalog and daily summary, and register the Google Health / UI data mismatch fix in the backlog.

### Acceptance criteria

- [x] C1: Database migration (`005_supplements_and_water.sql`) adds `is_supplement BOOLEAN NOT NULL DEFAULT 0` to `ingredients`. Models (`IngredientModel`, `Ingredient` dataclass) updated.
- [x] C2: `IngredientService` (`create`, `update`, `_to_domain`, `list`) and MCP tools (`create_ingredient`, `update_ingredient`, `list_ingredients`) support `is_supplement: bool = False`.
- [x] C3: `MealService.get_day_entries` marks each entry with `is_supplement: bool`. `MealService.get_day_summary` includes:
  - Fixed daily water consumption (`3L`, `1.25€`) in `water_and_supplements` and adds `1.25€` to total daily `spend`.
  - Separates supplement entries into `water_and_supplements["supplements"]` while keeping regular food in `meals_by_type`.
- [x] C4: Web UI (`src/ui/html_generator.py`):
  - Ingredient creation/edition form includes a checkbox `#ing-is-supplement` ("💊 Es suplemento (ej: Creatina, Omega 3...)").
  - Ingredients tab (`#tab-ingredient`) displays regular ingredients in "📋 Ingredientes Guardados" and supplements + 3L water (1.25€) in a separate section "💧💊 Agua y Suplementos".
  - Daily Summary tab (`#tab-summary`) displays a dedicated section "💧💊 Agua y Suplementos" showing the daily 3L of water (1.25€) and any supplements logged on that day, separate from the food meal sections.
- [x] C5: `odd/BACKLOG.md` includes the proposed fix item for UI vs Google Health data mismatch (`google-health-ui-data-mismatch`).
- [x] C6: Unit, integration, and UI tests green (`pytest`).
- [x] C7: OpenSpec documentation updated in `docs/specs/openspec/` (`requirements.md`, `data-model.md`, `api-spec.md`).

## Clarify
> Ambiguities and resolutions

- **Q1: How is the 3L of water per day at 1.25€ represented?**
  - **A**: It is a built-in daily baseline (`3L`, `0 kcal`, `1.25€`) automatically included in every day's summary (`water_and_supplements.water`) and added to the daily `spend` (`+1.25€`), as well as displayed in the "💧💊 Agua y Suplementos" section.
- **Q2: Do supplements still contribute to daily macros and spend if they have calories/macros/price (e.g., Omega 3 softgels)?**
  - **A**: Yes. Logged supplements contribute their macros and price to `consumed` and `spend`, while visually rendering in the dedicated "💧💊 Agua y Suplementos" section rather than mixing with regular meals (breakfast, lunch, etc.).
- **Q3: Can supplements still be selected when logging a meal entry in the UI?**
  - **A**: Yes, the meal item datalist includes all ingredients (food and supplements), and when a supplement is logged, it automatically routes to the "💧💊 Agua y Suplementos" section.

## Plan
> Implementation plan

- **T1 — Database Migration & Models**:
  - Create `src/db/migrations/005_supplements_and_water.sql`.
  - Update `Ingredient` in `src/db/models.py` and `src/models/ingredient.py` with `is_supplement: bool = False`.
- **T2 — IngredientService, MealService & MCP Tools**:
  - Update `src/services/ingredient_service.py` and `src/mcp/tools/ingredient_tools.py` to support `is_supplement`.
  - Update `src/services/meal_service.py` (`_entry_macros`, `get_day_summary`) to include `is_supplement`, `water_and_supplements` (with 3L water @ 1.25€), and include `1.25€` in daily `spend`.
- **T3 — Web UI Updates (`src/ui/html_generator.py`)**:
  - Add `#ing-is-supplement` checkbox to the ingredient form and wire it in `submitIngredient`, `startEditIngredient`, and `cancelEditIngredient`.
  - Add dedicated "💧💊 Agua y Suplementos" section in `#tab-ingredient` and `#tab-summary`.
- **T4 — Tests & Verification**:
  - Add/update unit and integration tests in `tests/unit/test_ingredient_service.py`, `tests/unit/test_meal_service.py`, `tests/integration/test_mcp_ingredient_tools.py`, and `tests/integration/test_ui_web_routes.py`.
  - Run full test suite (`pytest`).
- **T5 — OpenSpec & Backlog Updates**:
  - Update `docs/specs/openspec/` (`requirements.md`, `data-model.md`, `api-spec.md`).
  - Update `odd/BACKLOG.md` (add `google-health-ui-data-mismatch` fix and close `supplements-and-water`).

## Tasks

- [x] T1: Create migration `005_supplements_and_water.sql` and update `Ingredient` models
- [x] T2: Update `IngredientService`, `MealService`, and `ingredient_tools.py`
- [x] T3: Update Web UI with supplement checkbox and "Agua y Suplementos" sections
- [x] T4: Add unit/integration tests and verify full test suite
- [x] T5: Update OpenSpec and `odd/BACKLOG.md`

## Verification
- Unit tests: `tests/unit/test_ingredient_service.py` (18/18 passing), `tests/unit/test_meal_service.py` (10/10 passing)
- Integration tests: `tests/integration/test_ui_web_routes.py` (7/7 passing)
- Full suite: 184/184 passing (`pytest`)
