# Feature: ui-delete-actions

> Enable deletion of saved ingredients, saved recipes, and logged daily meals from the UI.

## Spec
> What and why (no technology)

### Context
- Users currently have catalog views to inspect and edit ingredients and recipes, and a summary view to inspect daily meals.
- However, there is no way in the UI to delete an obsolete or mistakenly created ingredient or recipe.
- Similarly, if a meal was logged by mistake or with incorrect portions, users currently cannot remove it from the day's summary.
- Users need direct "Eliminar" actions in the UI for ingredients, recipes, and daily meal entries.

### Objective
- Allow deleting ingredients directly from the ingredient catalog table with confirmation and dependency feedback.
- Allow deleting recipes directly from the recipe catalog table with confirmation.
- Allow deleting registered meals directly from the daily summary table with confirmation and automatic recalculation of macros, goals, and spend.

### Acceptance Criteria
- [x] C1: **Delete Ingredient from UI**: In `/ui/ingredient`, each catalog row includes a "Eliminar" button. Confirming deletion sends `POST /api/delete_ingredient`, removes the row from view, updates the datalists, and handles errors if the ingredient is used in a recipe.
- [x] C2: **Delete Recipe from UI**: In `/ui/recipe`, each catalog row includes a "Eliminar" button. Confirming deletion sends `POST /api/delete_recipe`, removes the recipe from view, and refreshes datalists.
- [x] C3: **Delete Meal Entry Tool & Endpoint**: Add `delete_meal` MCP tool and `/api/delete_meal` endpoint backed by `MealService.delete(entry_id)`.
- [x] C4: **Delete Logged Meal from Daily Summary UI**: In `/ui/summary`, the meals table includes an "Acciones" column with a delete button for each meal. Confirming deletion sends `POST /api/delete_meal` and triggers `fetchSummary()` to recalculate consumed/remaining macros and refresh the table.
- [x] C5: **Integration Tests**: Verify deletion endpoints and UI flows for ingredients, recipes, and meals.

## Clarify
> Resolved ambiguities

- **Q1. What happens if an ingredient is used in existing recipes?**
  - A: `IngredientService.delete` raises `DependencyError` with a message. The UI should catch this error and display a red banner or alert ("No se puede eliminar: este ingrediente se utiliza en una o más recetas").
- **Q2. What happens to the daily summary when a meal is deleted?**
  - A: The meal is deleted from SQLite `meal_entries`. The UI calls `fetchSummary()`, which refreshes the target vs remaining cards and the day's meal list dynamically.
- **Q3. Is user confirmation required before deletion?**
  - A: Yes, a native browser `confirm(...)` dialog prevents accidental deletions across all three views.

## Plan
> Technical decisions + classification

- **Classification**: Normal (new `delete_meal` tool, UI buttons and JavaScript handlers, integration tests).
- **D1 (Backend Tool)**:
  - Add `delete_meal(entry_id: int)` in `src/mcp/tools/meal_tools.py`.
  - Register in `src/mcp/server.py` as `server.add_tool(delete_meal, name="delete_meal")` (total 26 tools).
- **D2 (Ingredient Catalog UI)**:
  - Add "Eliminar" button in `renderIngredientsTable()`.
  - Add JavaScript `deleteIngredient(id, name)`.
- **D3 (Recipe Catalog UI)**:
  - Add "Eliminar" button in `renderRecipesTable()`.
  - Add JavaScript `deleteRecipe(id, name)`.
- **D4 (Daily Summary UI)**:
  - Add "Acciones" column in `renderSummaryMeals()`.
  - Add JavaScript `deleteMeal(entryId, itemName)`.
- **D5 (Tests)**:
  - Add test in `tests/integration/test_mcp_meal_tools.py` for `delete_meal`.
  - Update `test_mcp_server.py` and `test_hermes_e2e.py` for 26 tools.
  - Add integration test in `tests/integration/test_ui_web_routes.py` verifying UI delete handlers and API calls.

## Tasks
> Implementation checklist

- [x] T1: Implement `delete_meal` MCP tool and register in `server.py` → verify: `pytest tests/integration/test_mcp_meal_tools.py`
- [x] T2: Update tool count to 26 in `test_mcp_server.py` and `test_hermes_e2e.py` → verify: `pytest tests/integration/test_mcp_server.py`
- [x] T3: Add delete controls & JS functions in `src/ui/html_generator.py` for ingredients, recipes, and summary meals → verify: `pytest tests/integration/test_ui_web_routes.py`
- [x] T4: Run full test suite → verify: `pytest tests/ -v`
- [x] T5: Verify live UI endpoints on running server

## Verification
> Comparison against the spec

- **C1 (Delete Ingredient from UI)**: Added "🗑️ Eliminar" button to each ingredient catalog row. Calls `POST /api/delete_ingredient`, catches dependency errors if the ingredient is part of a recipe, and reloads the table and datalists. Verified via integration test `test_ui_delete_actions_and_api`.
- **C2 (Delete Recipe from UI)**: Added "🗑️ Eliminar" button to each recipe catalog row. Calls `POST /api/delete_recipe`, removes the recipe, and updates datalists. Verified via integration test `test_ui_delete_actions_and_api`.
- **C3 (Delete Meal Entry Tool & Endpoint)**: Implemented `delete_meal` in `meal_tools.py` and registered in `server.py` (total 26 tools). Verified via `test_delete_meal_tool` in `test_mcp_meal_tools.py`.
- **C4 (Delete Logged Meal from Daily Summary UI)**: Added "Acción" column and delete button to daily summary meals table with confirmation. Calls `POST /api/delete_meal` and refreshes `fetchSummary()`, recalculating goals and remaining calories. Verified via integration test `test_ui_delete_actions_and_api`.
- **C5 (Integration Tests & Full Suite)**: All 160 tests pass (`pytest tests/ -q`).

## Close
> Close

- **Date**: 2026-11-10
- **Result**: Complete and verified.
- **Artifacts**:
  - `src/mcp/tools/meal_tools.py` (`delete_meal`)
  - `src/mcp/server.py` (registered `delete_meal`, total 26 tools)
  - `src/services/meal_service.py` (added `"name"` to `_entry_macros`)
  - `src/ui/html_generator.py` (delete buttons and handlers for ingredients, recipes, and summary meals)
  - `tests/integration/test_mcp_meal_tools.py`
  - `tests/integration/test_mcp_server.py`
  - `tests/integration/test_ui_web_routes.py`
  - `tests/e2e/test_hermes_e2e.py`
