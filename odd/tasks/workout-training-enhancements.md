# Feature: workout-training-enhancements

> Pack of 3 training features:
> 1. Estimated 1RM in daily workout summary (per set and best per exercise).
> 2. Set count at max weight in Exercises tab `Peso Máx` column (`75×10 (2)`, omitting `(1)`).
> 3. Cardio time logging (in minutes) in the Workout Registration form (`#tab-workout`) and display in Daily Summary.

## Spec
> What and why (no technology)

### Context
- In the Daily Summary (`#tab-summary`), workout sessions list sets in a table with a `1RM Est.` column, but `WorkoutService.get_by_day` (`_session_to_dict`) does not include `estimated_1rm` on returned sets, causing the UI to display `-` for every set and offering no per-exercise 1RM summary badge.
- In the Exercises tab (`#tab-exercise`), the `Peso Máx` column shows the heaviest weight lifted and the highest repetitions achieved at that weight (`{max_weight}×{max_weight_reps}`), but does not indicate how many sets were performed with that weight in that session (e.g. doing 2 sets at 75 kg of 10 and 9 reps should show `75×10 (2)`, or 3 sets at 66 kg of 15, 13, 13 reps should show `66×15 (3)`, omitting `(1)` if only 1 set was done).
- In the Workout Registration tab (`#tab-workout`), the backend (`WorkoutService.register_session`) already supports `time` exercises (`duration` in seconds), but the UI form only renders `Reps` and `Peso (kg)` inputs and cannot log time-based cardio exercises.

### Acceptance Criteria
- [x] C1: **Estimated 1RM in Daily Workout Summary**:
  - `WorkoutService.get_by_day` (`_session_to_dict`) computes `estimated_1rm` (rounded to 1 decimal place; exact weight when `reps == 1`; `None` for non-weight sets) for each set in the session.
  - In `#tab-summary` (`renderSummaryWorkouts`), each weight/reps set row displays its `estimated_1rm` (`{e1rm} kg`), and each session card renders per-exercise badges showing the best estimated 1RM achieved for each strength exercise in that session.
- [x] C2: **Max Weight Set Count in Exercises Tab (`Peso Máx`)**:
  - `WorkoutService.get_exercise_stats` computes `max_weight_sets` (int): the number of sets performed at `max_weight` within the session where the best `(max_weight, max_weight_reps)` set was achieved (on a tie of weight and max reps across sessions, the session with more sets at that weight wins; defaults to `1` when derived solely from `PersonalRecordModel`).
  - In `#tab-exercise` (`renderExercisesTable`), the `Peso Máx` badge renders `💪 {max_weight}×{max_weight_reps} ({max_weight_sets})` when `max_weight_sets > 1`, and `💪 {max_weight}×{max_weight_reps}` when `max_weight_sets <= 1`.
- [x] C3: **Cardio (Time) Logging in Workout Registration & Summary**:
  - In `#tab-workout`, users can add or switch exercise blocks to Cardio / Time mode (`type = "time"`), either via a dedicated `⏱️ + Añadir Cardio (Tiempo)` button, a per-exercise mode selector (`Peso y Reps` vs `Cardio / Tiempo (min)`), or automatically when selecting a catalog exercise whose `type === 'time'`.
  - Time exercise rows accept duration in **minutes** (supporting decimals, e.g. `20` or `15.5` min) and `submitWorkout` converts minutes to seconds (`Math.max(1, Math.round(minutes * 60))`) in the `duration` field sent to `register_workout`.
  - In `#tab-summary` (`renderSummaryWorkouts`), sets with `duration` display the formatted time in minutes (e.g. `20 min`) instead of `undefined kg`.
- [x] C4: **Automated Tests & Documentation**:
  - Unit tests in `tests/unit/test_workout_service.py` and integration tests in `tests/integration/test_mcp_exercise_tools.py`, `tests/integration/test_mcp_workout_tools.py`, and `tests/integration/test_ui_web_routes.py` cover all 3 features.
  - OpenSpec documentation (`docs/specs/openspec/requirements.md` and `docs/specs/openspec/api-spec.md`) updated.

## Clarify
> Resolved ambiguities

- **Q1: Does the `(N)` set count in `Peso Máx` count sets at that weight in the same session or across all history?**
  - **A**: In the same workout session where that `Peso Máx` was achieved (e.g. 2 sets with 75 kg of 10 and 9 reps in a session → `75×10 (2)`; 3 sets with 66 kg of 15, 13, 13 reps → `66×15 (3)`). If only 1 set was done at that weight in the session, `(1)` is omitted (`75×10`).
- **Q2: What unit should the user enter and view for cardio time?**
  - **A**: Minutes in the UI (e.g. `20 min`), converted to seconds (`duration = minutes * 60`) for storage in the database (matching FR5.4), and displayed in minutes in the Daily Summary.
- **Q3: How should Estimated 1RM be shown in the Daily Workout Summary?**
  - **A**: Both in the `1RM Est.` column of each set row in the session table and as a per-exercise best-1RM summary badge in the session header/card.

## Plan
> Technical decisions + classification

- **Classification**: **Substantial** — touches `WorkoutService` (`get_exercise_stats`, `_session_to_dict`), Web UI (`#tab-workout`, `#tab-exercise`, `#tab-summary` in `src/ui/html_generator.py`), unit/integration tests, and OpenSpec docs.
- **Execution Mode**: Fast (default) — implement all tasks with TDD (red → green), verify with full test suite, and produce a single pre-commit report at the end.
- **D1 (`_session_to_dict` 1RM enrichment)**: In `WorkoutService._session_to_dict`, compute `estimated_1rm` for each set when `weight > 0` and `reps > 0` (`float(weight)` if `reps == 1` else `round(estimate_1rm(float(weight), int(reps)), 1)`), else `None`.
- **D2 (`get_exercise_stats` session-level max weight set counting)**: Group sets by `(exercise_id, session_id, weight)` so that for each exercise's `max_weight`, we know for each session: the max reps achieved at `max_weight`, the number of sets performed at `max_weight` in that session, and the session date. Pick the session that maximizes `(weight, max_reps_at_weight, sets_count_at_weight)` and expose `max_weight_sets: int` in the stats dict.
- **D3 (`#tab-exercise` `Peso Máx` badge)**: In `renderExercisesTable`, format the `Peso Máx` badge as `💪 ${ex.pr.max_weight}×${ex.pr.max_weight_reps || 1}${ex.pr.max_weight_sets > 1 ? ' (' + ex.pr.max_weight_sets + ')' : ''}`.
- **D4 (`#tab-workout` Cardio / Time support)**:
  - Add a mode selector (`weight_reps` vs `time`) on each exercise block in `#tab-workout` AND a `⏱️ + Añadir Cardio (Tiempo)` button next to `+ Añadir Ejercicio`.
  - When an exercise from `allExercises` is selected via autocomplete or typed, auto-switch the block's mode if `ex.type === 'time'`.
  - In `time` mode, the table header shows `Set | Duración (minutos) |` and each row renders `<input type="number" class="set-duration-min" ... placeholder="Minutos (ej: 20)">`.
  - In `submitWorkout`, if a block is in `time` mode (or row has `.set-duration-min`), build `{ set_number: i + 1, duration: Math.max(1, Math.round(parseFloat(durMin) * 60)) }`.
- **D5 (`#tab-summary` workout 1RM badges & cardio duration rendering)**:
  - In `renderSummaryWorkouts`, compute `e1rm` from `set.estimated_1rm` (with JS fallback for weight/reps sets), collect the highest 1RM per exercise in the session, and render a row of exercise 1RM badges (`🏆 {exercise}: 1RM Est. {best1rm} kg`) above the sets table.
  - For time sets (`set.duration > 0` and no weight/reps), format the Reps/Peso columns cleanly (`⏱️ Tiempo` / `${Math.round((set.duration / 60) * 10) / 10} min` and `-` for `1RM Est.`).

## Tasks
> Implementation checklist

- [x] T1: Enrich `WorkoutService._session_to_dict` with `estimated_1rm` per set and add `max_weight_sets` calculation in `WorkoutService.get_exercise_stats` (TDD: unit & integration tests first) → verify: `pytest tests/unit/test_workout_service.py tests/integration/test_mcp_workout_tools.py tests/integration/test_mcp_exercise_tools.py -v` → PASSED (43 tests)
- [x] T2: Update `#tab-exercise` (`renderExercisesTable`) in `src/ui/html_generator.py` to show `({max_weight_sets})` in `Peso Máx` when `> 1` → verify: `pytest tests/integration/test_ui_web_routes.py -v` → PASSED (16 tests)
- [x] T3: Update `#tab-summary` (`renderSummaryWorkouts`) in `src/ui/html_generator.py` to display per-set `1RM Est.`, per-exercise best 1RM badges, and formatted minutes for cardio (`duration`) sets → verify: `pytest tests/integration/test_ui_web_routes.py -v` → PASSED (16 tests)
- [x] T4: Update `#tab-workout` in `src/ui/html_generator.py` to support adding cardio exercises in minutes (`⏱️ + Añadir Cardio (Tiempo)` + mode toggle + auto-detect `type === 'time'` from catalog + seconds conversion on submit) → verify: `pytest tests/integration/test_ui_web_routes.py -v` → PASSED (16 tests)
- [x] T5: Update OpenSpec (`docs/specs/openspec/requirements.md` and `docs/specs/openspec/api-spec.md`) and run full test suite → verify: `pytest tests/ -v` → PASSED (221 tests)
- [x] T6: Prevent price column line wrapping in Ingredients & Supplements tables (`white-space: nowrap;`) → verify: `pytest tests/integration/test_ui_web_routes.py -v` → PASSED (16 tests)

## Verification
> Comparison against the spec (filled in at close)

- **C1 (Estimated 1RM in Daily Workout Summary)**: `WorkoutService._session_to_dict` returns `estimated_1rm` for every set; `renderSummaryWorkouts` displays each set's 1RM in the table and renders `.summary-exercise-1rm-badges` with the best estimated 1RM per exercise in the session. Verified by `test_get_by_day_returns_sessions`, `test_get_workouts_by_day_tool`, and `test_ui_workout_training_enhancements_pack`.
- **C2 (Max Weight Set Count in Exercises Tab)**: `WorkoutService.get_exercise_stats` computes `max_weight_sets` per session at `max_weight` (tested with `75x10 (2)`, `66x15 (3)`, and single-set `22x6` without `(1)`). `renderExercisesTable` appends `(${ex.pr.max_weight_sets})` only when `> 1`. Verified by `test_get_exercise_stats_counts_sets_at_max_weight_in_session`, `test_list_exercises_with_prs`, and `test_ui_workout_training_enhancements_pack`.
- **C3 (Cardio Time Logging in Workout Registration & Summary)**: `#tab-workout` includes `⏱️ + Añadir Cardio (Tiempo)`, per-exercise mode selector (`weight_reps` vs `time`), automatic mode switching when selecting a `time` exercise from the catalog, minute inputs (`.set-duration-min`) converted to seconds on submit, and formatted minute display in `#tab-summary`. Verified by `test_ui_workout_training_enhancements_pack`.
- **C4 (Automated Tests & Documentation)**: Full test suite `pytest tests/ -v` passes (**221 passed in 3.56s**); OpenSpec `requirements.md` (FR6.5, FR8.2, FR8.5) and `api-spec.md` (`get_workouts_by_day`, `list_exercises`) updated.

## Close
> Close (filled in at close)

- **Date**: 2026-11-16
- **Implemented**: Estimated 1RM per set and per exercise in the daily workout summary, session set count `(N)` in the Exercises tab `Peso Máx` column when `> 1`, and cardio time logging in minutes in the Workout Registration form and Daily Summary.
- **Next step**: Commit on `feat/workout-training-enhancements`, push branch, and open PR to `main`.
