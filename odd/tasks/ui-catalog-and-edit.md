# Feature: ui-catalog-and-edit

> Consult and edit saved ingredients and recipes directly from HTML artifacts.

## Spec
> What and why (no technology)

### Context
- The Fitness AI system provides interactive HTML artifacts rendered via the Hermes GUI and local web routes (`/ui`).
- While users can create ingredients and build recipes, there is currently no way within the artifact UI to consult already registered ingredients or recipes, nor edit their attributes or compositions once saved.
- Users have to rely on chat queries or external inspection to review existing items.

### Objective
- Enable direct in-artifact consultation and interactive editing of saved ingredients and recipes in the HTML artifacts.
- Provide searchable catalog tables for ingredients and recipes in their respective tabs.
- Provide a 1-click "Edit" action on any item that populates the form, toggles update mode, and saves changes back to the system via the existing update APIs.

### Acceptance Criteria
- [x] C1: **Ingredient Catalog**: The Ingredient tab displays a searchable table/list of all saved ingredients with their unit, kcal, macros, price, and status.
- [x] C2: **Ingredient Interactive Editing**: Clicking "Edit" on an ingredient populates the form with its current values, shows an active editing indicator with a "Cancel" option, and changes submission to update the existing ingredient (via `/api/update_ingredient`).
- [x] C3: **Recipe Catalog**: The Recipe tab displays a searchable catalog of saved recipes with their total kcal, macros, price, and ingredient breakdowns.
- [x] C4: **Recipe Interactive Editing**: Clicking "Edit" on a recipe loads its name and ingredients table with exact quantities and units, allowing modifications and updating via `/api/update_recipe`.
- [x] C5: **Live Auto-Refresh & Fallbacks**: Creating or updating an ingredient/recipe automatically reloads the catalogs without a page refresh, and preserves the offline/Hermes prompt copy fallback.
- [x] C6: **Test Coverage**: Integration tests verify the UI includes catalog and editing elements and validates update flows via Starlette routes.

## Clarify
> Resolved ambiguities

- **Q1. Where should the catalog be positioned within the tabs?**
  - A: Directly below the form in both the Ingredient and Recipe tabs, with a search input and table/card layout matching the dark theme.
- **Q2. How does the editing state behave?**
  - A: Inline form loading. Clicking "Edit" scrolls smoothly to the form, populates the fields, displays an "Editing: <name>" badge with a "Cancel" button to return to create mode, and toggles the primary submit button to "Actualizar".
- **Q3. How are recipes' ingredient names resolved?**
  - A: `RecipeItem` includes the ingredient name or resolves against the ingredients catalog, ensuring the Recipe Builder rows display actual ingredient names when editing.
- **Q4. Execution mode?**
  - A: Fast mode (default). Full implementation in one pass with TDD and pre-commit report.

## Plan
> Technical decisions + classification

- **Classification**: Small (UI generator enhancement, domain model enrichment with backwards compatibility, integration tests).
- **D1 (Model/Service enrichment)**: Add `name: Optional[str] = None` to `RecipeItem` domain dataclass and populate `name=i.ingredient.name` in `RecipeService._to_domain` to cleanly transmit ingredient names in `list_recipes`.
- **D2 (UI Template)**: In `src/ui/html_generator.py`, add catalog sections, search filtering, edit state management (tracking `currentEditingIngredientId` and `currentEditingRecipeId`), and auto-loading on tab switch / page load.
- **D3 (Tests)**: Update `tests/integration/test_ui_web_routes.py` and unit/integration tests to assert the new catalog and editing features.

## Tasks
> Implementation checklist

- [x] T1: Enrich `RecipeItem` dataclass and `RecipeService._to_domain` with ingredient `name` → verify: `pytest tests/unit/test_recipe_service.py`
- [x] T2: Add Ingredient Catalog and Edit mode to `src/ui/html_generator.py` → verify: `pytest tests/integration/test_ui_web_routes.py`
- [x] T3: Add Recipe Catalog and Edit mode to `src/ui/html_generator.py` → verify: `pytest tests/integration/test_ui_web_routes.py`
- [x] T4: Add integration tests for catalog rendering and update API dispatch → verify: `pytest`
- [x] T5: Manual validation of running server on `http://127.0.0.1:9700/ui`

## Verification
> Comparison against the spec (filled in at close)

- [x] C1 & C2: Added Ingredient Catalog table with real-time text filter and "✏️ Editar" action. Clicking "Editar" populates the form, reveals the `ing-edit-banner`, toggles submit button to `Actualizar Ingrediente`, and saves via `/api/update_ingredient` with live table reload.
- [x] C3 & C4: Added Recipe Catalog table with search filter and "✏️ Editar" action. Clicking "Editar" populates the recipe name and all ingredient rows (with actual ingredient names, quantities, and units), reveals `recipe-edit-banner`, toggles submit button to `Actualizar Receta`, and saves via `/api/update_recipe`.
- [x] C5: Successful creation and update operations automatically refresh the catalogs asynchronously. Copy prompt for Hermes fallback is preserved if the client environment is offline/sandboxed.
- [x] C6: Verified by `tests/integration/test_ui_web_routes.py::test_ui_catalogs_and_editing_flow`. Full suite passes: **155 passed in 1.76s**.
- [x] T5: Verified live server running on `http://127.0.0.1:9700/ui` serving both banners and catalog elements.

## Close
> Close (filled in at close)

- Date: 2026-11
- Implemented: Searchable ingredient and recipe catalogs with inline editing in HTML artifacts, enriched `RecipeItem` with ingredient name, and added integration tests for the full consultation and update lifecycle.
- Next step: Review remaining backlog items (#7 `db-robustness`, #8 `seed-data`, #9 `odd-merge-back`).
