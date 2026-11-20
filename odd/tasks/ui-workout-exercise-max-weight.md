# Feature: ui-workout-exercise-max-weight

> Display the recorded Max Weight (`Peso Máx`) reference inside the Workouts screen (`#tab-workout`) whenever the user enters or selects an exercise that already has previous weight records, helping them choose the right working weight.

## Spec
> What and why (no technology)

- [x] C1: When entering or selecting a weight-based exercise in the Workouts tab (`#tab-workout`) that already has recorded weight history (`pr.max_weight`), display a clear `Peso Máx` reference badge (weight in kg, reps, set count if > 1, and date if available) inside that exercise block.
- [x] C2: When the exercise has no previous weight records, is not yet in the catalog, the input is cleared, or the exercise is in `time` (cardio) mode, hide the `Peso Máx` reference.
- [x] C3: Keep the reference up to date when the exercise catalog finishes loading, when switching to the Workouts tab, and after registering a new workout session.
- [x] C4: Add integration tests covering the Workouts UI Max Weight reference rendering and PR data availability.

## Clarify
> Resolved ambiguities

- Q: Does this require a new backend endpoint or schema change?
  - A: No. `/api/list_exercises?include_prs=true` is already fetched on page load into `allExercises` and returns `pr.max_weight`, `pr.max_weight_reps`, `pr.max_weight_sets`, and `pr.max_weight_date` for every exercise with weight records.

## Plan
> Technical decisions + classification

- Classification: **Small** — UI-only enhancement in `src/ui/html_generator.py` and integration test coverage in `tests/integration/test_ui_web_routes.py`; no backend API or DB migration needed.
- D1: Add a `.ex-max-weight-ref` container to each dynamic exercise block in `addExerciseBlock()` and a helper `updateExerciseMaxWeightRef(exBlockId, matchedEx)` that formats `Peso Máx` consistently with `#tab-exercise` (`badge-warning`).
- D2: Also surface `Máx <weight> kg` in the exercise autocomplete dropdown subtitle (`sub`) for weight exercises that have a recorded `max_weight`.
- D3: Add `refreshAllWorkoutExerciseRefs()` invoked from `fetchExercisesList()`, call `fetchExercisesList()` when switching to `workout` tab, and refresh `fetchExercisesList()` after a successful `submitWorkout()`.

## Tasks
> Implementation checklist

- [x] T1: Add `.ex-max-weight-ref`, `updateExerciseMaxWeightRef()`, `refreshAllWorkoutExerciseRefs()`, autocomplete max-weight subtitle, and workout tab/submit refresh hooks in `src/ui/html_generator.py` → verify: `pytest tests/integration/test_ui_web_routes.py -v` → PASSED
- [x] T2: Add integration test `test_ui_workout_exercise_max_weight_reference` in `tests/integration/test_ui_web_routes.py` and run full test suite → verify: `pytest tests/ -v` → PASSED (225 passed)

## Verification
> Comparison against the spec (filled in at close)

- **C1**: `.ex-max-weight-ref` renders `Peso Máx:` + `badge-warning` (`💪 <weight> kg × <reps> (<sets>)`) + date when a matching weight exercise with `pr.max_weight` is entered/selected; autocomplete subtitle also shows `Máx <weight> kg`.
- **C2**: `updateExerciseMaxWeightRef()` hides and clears `.ex-max-weight-ref` when the input is empty, unmatched, lacks `pr.max_weight`, or when the block mode is `time`.
- **C3**: `fetchExercisesList()` calls `refreshAllWorkoutExerciseRefs()`, `switchTab('workout')` triggers `fetchExercisesList()`, and `submitWorkout()` awaits `register_workout` and refreshes `fetchExercisesList()`.
- **C4**: `pytest tests/ -v` → **225 passed** (including `test_ui_workout_exercise_max_weight_reference`).

## Close
> Close (filled in at close)

- **Date**: 2026-11-20
- **Implemented**: Max Weight (`Peso Máx`) reference badge in `#tab-workout` exercise blocks and autocomplete dropdown, automatically refreshed on catalog load, tab switch, and workout submission.
- **Next step**: Commit on `feat/ui-workout-exercise-max-weight`, push, and open a PR to `main`.
