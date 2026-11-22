# Feature: workout-form-ux-and-daily-overwrite

> Improve the Training (`#tab-workout`) input ergonomics and daily workout persistence: place Weight (`Peso (kg)`) on the left and Reps (`Reps`) on the right in both Training and Daily Summary tables, prevent `Enter` from submitting the workout form while making `Enter` inside any set row append and focus a new set row, and overwrite any existing workout session for the same calendar day (with atomic Personal Record recalculation).

## Spec
> What and why (no technology)

- [ ] C1: **Weight-before-Reps Column Order**:
  - In `#tab-workout`, the strength exercise sets table displays **Peso (kg)** on the left and **Reps** on the right (both header columns and row inputs) while keeping live `1RM Est.` computation and submission payload unchanged.
  - In `#tab-summary`, the daily workout table displays **Peso / Duración** on the left and **Reps** on the right (keeping cardio/distance rows aligned cleanly with the updated column order).
- [ ] C2: **Prevent `Enter` Form Submission in `#form-workout`**:
  - Pressing `Enter` inside any `<input>` or `<select>` within `#form-workout` never submits the workout form.
  - Autocomplete selection via `Enter` on `.ex-name` when a suggestion is highlighted (`activeIdx >= 0`) continues to pick the highlighted exercise cleanly, and explicit activation of the submit button (`Registrar Sesión`) continues to submit normally.
- [ ] C3: **Create & Focus Next Set Row on `Enter`**:
  - Pressing `Enter` inside any set row input (`.set-weight`, `.set-reps`, or `.set-duration-min`, whether on the last row or an earlier row) creates a new set row for that exercise block and moves focus to the first input of the newly created row (`.set-weight` in `weight_reps` mode, `.set-duration-min` in `time` mode).
- [ ] C4: **Daily Workout Overwrite & Atomic PR Recalculation**:
  - Registering a workout for a calendar day (`DD-MM-YYYY`, ignoring time of day) that already has one or more workout sessions atomically replaces the existing session(s) for that day with the new session across both Web UI and MCP (`register_workout`).
  - If validation fails on the new workout payload, the transaction rolls back completely and existing workout data for that day remains intact.
  - Personal Records (`PersonalRecord`) for exercises affected by replaced session(s) are recalculated atomically from remaining + new `ExerciseSet` records (removing the PR row if no valid `weight_reps` sets remain for that exercise).
  - The response includes `"overwritten": bool` (and `"replaced_sessions": int`) so the Web UI displays `"Entrenamiento sobrescrito"` when overwriting vs `"Entrenamiento registrado"` for a new day.
- [ ] C5: **Tests & Documentation**:
  - Unit tests (`tests/unit/test_workout_service.py`), MCP integration tests (`tests/integration/test_mcp_workout_tools.py`), UI/HTTP integration tests (`tests/integration/test_ui_web_routes.py`), JS syntax check (`node --check`), and full test suite pass.
  - OpenSpec documentation (`docs/specs/openspec/requirements.md`, `docs/specs/openspec/api-spec.md`) updated.

## Clarify
> Resolved ambiguities

- **Q1: Should daily overwrite apply to both Web UI and MCP `register_workout`, or UI-only?**
  - **A:** Both — enforce max 1 workout session per calendar day inside `WorkoutService.register_session()`, consistent with 1-per-day upsert semantics used in `BodyProgressService`.
- **Q2: Should overwriting a day's workout ask for confirmation in the UI or overwrite directly?**
  - **A:** Overwrite directly when clicking `Registrar Sesión`, showing clear status feedback (`"Entrenamiento sobrescrito"` vs `"Entrenamiento registrado"`).
- **Q3: Should Personal Records (`PersonalRecord`) be recalculated when a previous session on that day is replaced?**
  - **A:** Yes — atomically recalculate PRs for all exercises present in replaced session(s) (and new session) so corrected typos or removed exercises never leave stale/ghost PRs.
- **Q4: What should happen when `Enter` is pressed on a non-last set row, or in Cardio (`time`) rows, and where should focus move?**
  - **A:** Pressing `Enter` in any set row input (`.set-weight`, `.set-reps`, `.set-duration-min`, last row or not) always creates a new set row for that exercise and focuses the new row's first input (`.set-weight` for strength, `.set-duration-min` for cardio/time).
- **Q5: Should the Weight/Reps column swap also apply to the Daily Summary workout table (`#tab-summary`)?**
  - **A:** Yes — swap Weight/Duration before Reps in both `#tab-workout` and `#tab-summary` for visual consistency.

## Plan
> Technical decisions + classification

- **Classification**: **Substantial** — spans `WorkoutService` (`src/services/workout_service.py`), Web UI (`src/ui/html_generator.py`), unit/integration tests, and OpenSpec documentation, and modifies the public behavior of `register_workout` to enforce single-session-per-day overwrite with PR recalculation.
- **D1 (Daily Overwrite & PR Recalculation in `WorkoutService.register_session`)**:
  - Compute the calendar day bounds `[start, end)` from `session_dt` (`datetime(y, m, d)` to `+1 day`), matching `get_by_day()`.
  - Inside `WorkoutSessionModel._meta.database.atomic()`, find all existing `WorkoutSessionModel` rows in `[start, end)`.
  - Collect affected `exercise_id`s from `ExerciseSetModel` rows belonging to those existing sessions, delete the existing sessions (cascading `ExerciseSetModel` rows and setting `PersonalRecordModel.session = NULL`), then create the new session and validate/insert all new sets (any `ValidationError` rolls back the deletion atomically).
  - Add a helper `_recalculate_pr(exercise_id)` that scans remaining `ExerciseSetModel` rows (joined with `WorkoutSessionModel`) for that `weight_reps` exercise and upserts or deletes `PersonalRecordModel` accordingly. Run it for every exercise affected by replaced sessions; then evaluate `new_prs` cleanly against the pre-new-session recalculated baseline (or compare against pre-overwrite PRs / newly established bests).
  - Return `"overwritten": replaced_count > 0` and `"replaced_sessions": replaced_count` in the `register_session()` dict (pass-through in `register_workout` tool).
- **D2 (Column Swap in `#tab-workout` and `#tab-summary`)**:
  - In `getSetsTableHeaderHtml(mode)` (`src/ui/html_generator.py`), change `weight_reps` header to `Set | Peso (kg) | Reps | 1RM Est. | (remove)`.
  - In `addSetRow()`, place `<input class="set-weight" ...>` in the left `<td>` and `<input class="set-reps" ...>` in the right `<td>`.
  - In `renderSummaryWorkouts()`, change the table header to `Ejercicio | Serie | Peso / Duración | Reps | 1RM Est.` and render the Weight/Duration cell before the Reps/Type badge cell for strength, cardio (`duration`), and distance sets.
- **D3 (`Enter` Key Handling & Feedback in `#form-workout`)**:
  - Attach a `keydown` listener on `#form-workout`:
    - If `e.key !== 'Enter'` return.
    - Allow native activation on `<button>` elements (e.g., `Registrar Sesión`) and `<textarea>`.
    - If the target is inside `.sets-table tbody tr` (`.set-weight`, `.set-reps`, `.set-duration-min`), call `e.preventDefault()`, identify the enclosing exercise block (`exBlockId`), call `addSetRow(exBlockId)` (returning the newly created `<tr>`), and focus its `.set-weight` or `.set-duration-min` input.
    - Otherwise, for any `<input>` or `<select>` in `#form-workout`, call `e.preventDefault()` so `Enter` never submits the form (while letting `.ex-name` autocomplete's own `keydown` handler pick highlighted suggestions first because it runs on the target before bubbling to `#form-workout`).
  - Update `summarizeSuccess(data, payload)` so `d.session` returns `'Entrenamiento sobrescrito'` when `d.overwritten` is truthy and `'Entrenamiento registrado'` otherwise.

## Tasks
> Implementation checklist

- [x] T1: Implement daily workout overwrite and atomic PR recalculation in `WorkoutService.register_session()` (TDD: unit tests in `tests/unit/test_workout_service.py` and MCP integration tests in `tests/integration/test_mcp_workout_tools.py`, covering same-day replacement regardless of time-of-day, rollback on validation error, PR downgrade/removal/retention, and `overwritten`/`replaced_sessions` fields) → verify: `pytest tests/unit/test_workout_service.py tests/integration/test_mcp_workout_tools.py -v` → PASSED (42 passed in 0.18s)
- [x] T2: Swap Weight (`Peso (kg)` / `Peso / Duración`, left) and Reps (`Reps`, right) columns in `#tab-workout` (`getSetsTableHeaderHtml`, `addSetRow`) and `#tab-summary` (`renderSummaryWorkouts`) in `src/ui/html_generator.py` → verify: `node --check` (`JS_SYNTAX_OK`) + `pytest tests/integration/test_ui_web_routes.py -v` → PASSED (18 passed in 1.24s)
- [x] T3: Add `#form-workout` `Enter` key handler (block form submission on inputs/selects while preserving `.ex-name` autocomplete selection, and append + focus next set row when pressing `Enter` in strength or cardio set inputs) and update `summarizeSuccess()` overwrite message in `src/ui/html_generator.py` → verify: `node --check` (`JS_SYNTAX_OK`) + `pytest tests/integration/test_ui_web_routes.py -v` → PASSED (18 passed in 0.87s)
- [x] T4: Add UI/HTTP integration tests in `tests/integration/test_ui_web_routes.py` covering Weight-left/Reps-right order in `#tab-workout` and `#tab-summary`, `Enter` key handling, and `/api/register_workout` daily overwrite flow, then run the full test suite → verify: `node --check` (`JS_SYNTAX_OK`) + `pytest tests/ -v` → PASSED (242 passed in 3.65s)
- [ ] T5: Update OpenSpec docs (`docs/specs/openspec/requirements.md`, `docs/specs/openspec/api-spec.md`) to document daily overwrite semantics, PR recalculation, and Training/Summary UI updates → verify: `pytest tests/ -v`

## Verification
> Comparison against the spec (filled in at close)

## Close
> Close (filled in at close)
