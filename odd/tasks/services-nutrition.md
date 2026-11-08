# Feature: services-nutrition

> Nutrition domain services: Ingredient, Recipe, Meal, DailyGoal.
> Fills in the `...` stubs in `src/services/*` (nutrition subset) and the stub
> tests in `tests/unit/test_*_service.py` (nutrition subset).

## Spec
> What and why (technology-agnostic)

- [ ] C1: Ingredients can be created, updated, listed (search, provisional filter, pagination), found by name exactly and fuzzily, and deleted; duplicates on (name, unit) are rejected.
- [ ] C2: Deleting an ingredient removes its meal entries (count returned) and is rejected if the ingredient is used by any recipe.
- [ ] C3: Recipes can be created as compound (macros/price computed from items) or opaque (direct price/macros); updating a recipe replaces its items and recomputes macros.
- [ ] C4: Deleting a recipe removes its items and its meal entries (count returned).
- [ ] C5: Meals can be registered against an ingredient or a recipe with quantity and date; an unknown item is auto-created as provisional.
- [ ] C6: A daily summary reports consumed macros, spend, goal, remaining, and the day's entries with computed macros.
- [ ] C7: Daily goals can be set per date (upsert) and a default goal can be set; get falls back to the closest past goal, then to the default.
- [ ] C8: All 26 unit tests across the 4 nutrition service test files are green.

## Clarify
> Ambiguities resolved

- Q: What types do services accept/return? → A: dataclasses from `src/models/` (matches stub signatures); mapping to Peewee models is internal to each service.
- Q: Unit assumption for macro math? → A: `quantity` is expressed in the item's base unit; no unit conversion in v0 (consistent with `utils/macros.py`).
- Q: Recipe entry quantity semantics? → A: multiplier of the whole recipe (1.0 = entire recipe); `unit` stored as given, convention `u`. (Assumption — no servings model in v0.)
- Q: What happens to meal entries when an ingredient/recipe is deleted? → A: Service deletes referencing meal entries; `IngredientService.delete` returns the count (per stub docstring); `RecipeService.delete` returns the count too.
- Q: Can an ingredient used in a recipe be deleted? → A: No — DB `ON DELETE RESTRICT` blocks it; the service raises ValueError.
- Q: Goal inheritance semantics? → A: `get_goal(date)` = row for that date, else closest row with date < target, else the `is_default` row, else ValueError.
- Q: Date format? → A: `DD-MM-YYYY` (ADR-007 / data-model.md). Dataclass comments say `YYYY-MM-DD` (stale) — fixed during implementation.
- Q: Error convention? → A: `ValueError` with English messages (duplicate, not found on update/delete, ingredient in use, no goal found, invalid date).
- Q: Rounding? → A: `round(x, 2)` for computed macros/price (matches `utils/macros.py`).
- Q: `list()` `type` filter (Recipe)? → A: `compound` = has `recipe_items` rows; `opaque` = no items (direct price/macros).
- Q: Fuzzy search? → A: exact match on `normalize()` first, else `fuzzy_match` (threshold 0.6) over names in the DB.
- Q: Provisional auto-creation in `MealService.register`? → A: unknown ingredient → provisional Ingredient (macros/price 0, unit = entry unit); unknown recipe → provisional opaque Recipe (price/macros None).

## Plan
> Technical decisions

- **Classification**: Substantial — 4 service modules + 26 tests; no new public API, no migration → no SDD escalation.
- D1: Stub signatures are the public API (dataclasses in/out); kept unchanged.
- D2: Internal `_to_peewee`/`_to_dto` mapping helpers per service module; no shared new layer.
- D3: Reuse `utils/fuzzy.py` (`fuzzy_match`, `normalize`) and `utils/macros.py` (`calc_ingredient_macros`, `calc_recipe_macros`); no duplicated math.
- D4: All writes inside `with get_db():` (provisional create + entry insert in one transaction).
- D5: Date format validated with `datetime.strptime(date, "%d-%m-%Y")` → ValueError on bad format.
- D6: `RecipeService.update` replaces all items (delete + insert) and recomputes macros/price from ingredients.
- D7: Tests fill the existing stub files in place; seed data created via services/models inside tests; `db` fixture already re-points to `:memory:`.
- D8: TDD per task: stubs are trivially green today — each task first rewrites its stub tests into real assertions (red), then implements, then green.

## Tasks
> Implementation checklist

- [x] T1: Implement `IngredientService` (create / get_by_id / find_by_name / update / delete / list) → files: src/services/ingredient_service.py, tests/unit/test_ingredient_service.py → verify: `pytest tests/unit/test_ingredient_service.py -v` (17 pass)
- [ ] T2: Implement `RecipeService` (create compound/opaque, calculate_macros, update replaces items, delete cascades, list type filter) → files: src/services/recipe_service.py, tests/unit/test_recipe_service.py → verify: `pytest tests/unit/test_recipe_service.py -v` (6 pass)
- [ ] T3: Implement `GoalService` (set_goal upsert, set_default, get_goal fallback chain) → files: src/services/goal_service.py, tests/unit/test_goal_service.py → verify: `pytest tests/unit/test_goal_service.py -v` (6 pass)
- [ ] T4: Implement `MealService` (register with provisional, get_day_entries, get_day_summary, update, delete) → files: src/services/meal_service.py, tests/unit/test_meal_service.py → verify: `pytest tests/unit/test_meal_service.py -v` (7 pass)
- [ ] T5: Full suite green + fix stale `YYYY-MM-DD` comments in dataclasses → files: src/models/meal_entry.py (and any other stale comments) → verify: `pytest tests -q`

## Verification
> Spec contrast (filled at close)

## Close
> Close (filled at close)
