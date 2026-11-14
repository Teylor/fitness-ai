# accent-insensitive-search

> Feature: accent-insensitive-search

## Spec

### Context
Backend name searches (`IngredientService.list`, `RecipeService.list`, `ExerciseService.list(search=...)`, and `find_by_name`/`find_exact`) already strip accents via `src/utils/fuzzy.py:normalize()`. However:
1. Client-side filters in `src/ui/html_generator.py` (`filterIngredients`, `filterRecipes`, `filterExercises`) and ingredient-unit auto-fill (`onMealItemInput`, `onRecipeItemInput`) and muscle group key comparisons use plain `.toLowerCase()`, so searching `"atun"` or `"biceps"` does not match `"Atún"` or `"Bíceps"`.
2. `ExerciseService.list(muscle_group=...)` compares `.lower()` instead of `normalize()`.

### Objective
Make all UI search filters, name auto-matchers, and muscle-group comparisons accent-insensitive via a shared JS `normalizeText()` helper, and update `ExerciseService.list(muscle_group=...)` to use `normalize()`.

### Acceptance Criteria
- [x] C1: `src/ui/html_generator.py` defines `normalizeText(str)` using NFKD decomposition + diacritic stripping + lowercase + trim.
- [x] C2: `filterIngredients`, `filterRecipes`, `filterExercises`, `onMealItemInput`, `onRecipeItemInput`, and muscle group key comparisons use `normalizeText()`.
- [x] C3: `ExerciseService.list(muscle_group=...)` uses `normalize()` so accent differences (e.g. `Biceps` vs `Bíceps`) match.
- [x] C4: Unit + integration tests cover both backend and UI JS output; full `pytest tests -q` green.

## Clarify
- Backend `IngredientService`, `RecipeService`, and `ExerciseService.list(search=...)` already use `normalize()` from `src/utils/fuzzy.py`.
- In JS, `String(str || '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim()` mirrors Python's `normalize()`. Note f-string brace doubling (`{{` / `}}`) in `html_generator.py`.

## Plan
- Mode: fast.
- TDD:
  - T1: Add unit test for `ExerciseService.list(muscle_group=...)` accent-insensitivity and integration test asserting `normalizeText` usage in generated UI HTML.
  - T2: Add `normalizeText()` in `src/ui/html_generator.py` and update `ExerciseService.list(muscle_group=...)` in `src/services/exercise_service.py`.

## Tasks
- [x] T1: Add tests in `tests/unit/test_exercise_service.py` and `tests/integration/test_ui_web_routes.py` (RED).
- [x] T2: Implement `normalizeText()` in `src/ui/html_generator.py` and `normalize()` for `muscle_group` in `src/services/exercise_service.py` (GREEN).

## Verification
- **Tests**: Full pytest suite passing (`205 passed in 2.92s`), including `test_list_exercises_accent_insensitive_search_and_muscle_group` and `test_ui_accent_insensitive_search_helpers`.
- **Backend**: `ExerciseService.list(muscle_group=...)` now normalizes with `src/utils/fuzzy.py:normalize()` (matching `IngredientService`, `RecipeService`, and `ExerciseService.list(search=...)`).
- **UI**: `normalizeText()` added in `src/ui/html_generator.py` and wired into `filterIngredients`, `filterRecipes`, `filterExercises`, `onMealItemInput`, `onRecipeItemInput`, and muscle group key comparisons.

## Close
- Closed 2026-11: T1–T2 ✅ and Verification filled.
- Backlog item moved to Done; branch `feat/accent-insensitive-search` committed and pushed.
