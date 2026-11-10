# Feature: ui-new-features

> UI usability enhancements: autocomplete for meals & recipe ingredients, clean recipe initialization, and interactive calendar date pickers.

## Spec
> What and why (no technology)

### Context
- The Fitness AI web artifact allows logging meals, building recipes, logging workouts, and viewing summaries.
- Entering item names manually can lead to typos and doesn't leverage already saved catalog data.
- The recipe builder currently comes pre-populated with arbitrary default ingredients ("Pechuga de Pollo" and "Arroz") which users have to manually delete when crafting their own recipes.
- Manual text entry of dates (e.g. `DD-MM-YYYY`) is prone to formatting mistakes and lacks a visual calendar picker.

### Objective
- In the Meal tab, equip the `meal-item` input with a searchable datalist of saved items (ingredients or recipes depending on selected food type).
- In the Recipe tab, remove hardcoded default ingredients so the builder starts clean.
- In the Recipe tab, attach an ingredient catalog search/autocomplete datalist to `rec-item-name` in dynamic recipe rows.
- Equip date inputs with interactive calendar selectors so clicking anywhere on the input opens a visual calendar picker, seamlessly formatting to `DD-MM-YYYY` for the backend.

### Acceptance Criteria
- [x] C1: **Meal Item Autocomplete**: `meal-item` input provides autocomplete suggestions populated from saved ingredients or recipes based on the selected `meal-type`.
- [x] C2: **Clean Recipe Builder Initialization**: The recipe builder starts with an empty item row instead of hardcoded chicken and rice.
- [x] C3: **Recipe Item Autocomplete**: Dynamic ingredient rows in the recipe builder provide autocomplete suggestions from saved ingredients in `rec-item-name`.
- [x] C4: **Interactive Calendar Date Picker**: Date inputs (`meal-date`, `workout-date`, `summary-date`) display native calendar pickers on click, while formatting the submitted payload to `DD-MM-YYYY` (and `DD-MM-YYYY HH:MM` for workouts).
- [x] C5: **Integration Test Verification**: `tests/integration/test_ui_web_routes.py` verifies presence of datalists, date picker input types, clean recipe rows, and end-to-end dispatch.

## Clarify
> Resolved ambiguities

- **Q1. How should date picker inputs behave with the backend's `DD-MM-YYYY` requirement?**
  - A: Use standard HTML5 `<input type="date">` (and `<input type="datetime-local">` for workouts) with `showPicker()` on click. The JavaScript client automatically converts ISO format `YYYY-MM-DD` to `DD-MM-YYYY` on payload dispatch.
- **Q2. When should the meal autocomplete datalist update?**
  - A: When `meal-type` changes (between 'ingredient' and 'recipe') and whenever catalog data is fetched or updated.
- **Q3. What should dynamic recipe rows start with?**
  - A: One clean empty row with quantity 100 and unit 'gr', without pre-filling ingredient names.
- **Q4. Execution mode?**
  - A: Fast mode (default). Implement all UI enhancements, update integration tests, and provide pre-commit report.

## Plan
> Technical decisions + classification

- **Classification**: Small (HTML template, CSS/JS interactivity enhancements, integration tests).
- **D1 (Datalists)**: Add `<datalist id="meal-items-datalist">` and `<datalist id="recipe-ingredients-datalist">`. Update them dynamically from `allIngredients` and `allRecipes`.
- **D2 (Date Inputs & Conversion)**: Change date inputs to `type="date"` and `type="datetime-local"` with `onclick="this.showPicker && this.showPicker()"`. Add helper functions `toBackendDate()` and `toBackendDateTime()` before calling `executeAction()`.
- **D3 (Recipe Builder Clean Rows)**: Update `addRecipeRow()` default call to `addRecipeRow('', 100, 'gr')` and reset to 1 empty row in `cancelEditRecipe()`.
- **D4 (Tests)**: Extend `tests/integration/test_ui_web_routes.py` to assert date input types, datalist elements, and proper dispatch with converted dates.

## Tasks
> Implementation checklist

- [x] T1: Update date inputs to native date/datetime-local pickers and add date conversion helpers → verify: `pytest tests/integration/test_ui_web_routes.py`
- [x] T2: Add datalist and autocomplete for `meal-item` and `rec-item-name` → verify: `pytest tests/integration/test_ui_web_routes.py`
- [x] T3: Remove default chicken/rice rows from recipe builder initialization → verify: `pytest tests/integration/test_ui_web_routes.py`
- [x] T4: Update and expand integration tests in `test_ui_web_routes.py` → verify: `pytest`
- [x] T5: Verify live running server

## Verification
> Comparison against the spec (filled in at close)

- [x] C1: `<datalist id="meal-items-datalist">` attached to `meal-item` input, dynamically populated with ingredient or recipe suggestions and auto-selecting unit when matched.
- [x] C2: Removed default hardcoded chicken and rice rows. The recipe builder initializes and resets to a single empty row ready for input.
- [x] C3: `<datalist id="recipe-ingredients-datalist">` attached to dynamic `rec-item-name` inputs with auto-unit synchronization on selection.
- [x] C4: Native date and datetime-local calendar pickers implemented with `showPicker()` click handlers, formatted transparently to `DD-MM-YYYY` via `toBackendDate()` and `toBackendDateTime()`.
- [x] C5: Verified by `tests/integration/test_ui_web_routes.py::test_ui_new_features_elements_and_interactions`. Full test suite passes: **156 passed in 1.80s**.
- [x] T5: Verified live running server on `http://127.0.0.1:9700/ui` serving all autocomplete datalists and date picker controls.

## Close
> Close (filled in at close)

- Date: 2026-11
- Implemented: Usability enhancements in HTML artifacts: interactive calendar date pickers, meal item autocomplete, recipe ingredient autocomplete, clean recipe builder initialization, and integration tests.
- Next step: Review remaining backlog items (#7 `db-robustness`, #8 `seed-data`, #9 `odd-merge-back`).
