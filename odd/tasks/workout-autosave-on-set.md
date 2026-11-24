# Feature: workout-autosave-on-set

> Automatically save the daily workout in the Training (`#tab-workout`) tab every time a complete set (`weight` + `reps` for strength, or `duration` in minutes for cardio/time) is entered or edited, leveraging daily overwrite semantics (`register_workout`) and auto-hydrating any existing session for the selected date so progress is never lost if the user closes the app without clicking "Registrar Sesión".

## Spec
> What and why (no technology)

- [ ] C1: **Filtered Payload Builder & Safe Serialized Auto-Save**:
  - Auto-save constructs a clean workout payload that skips incomplete set rows (e.g., blank trailing rows added by `Enter`) and exercise blocks with blank names, supports `0 kg` bodyweight strength sets (`weight >= 0` and integer `reps >= 1`) and positive cardio durations (`duration > 0` min), merges duplicate exercise blocks sharing the same trimmed name (case-insensitive) with sequential `set_number` (`1..N`), and never sends an empty `exercises: []` payload.
  - Concurrent edits are serialized with a single-flight save queue and payload fingerprint deduplication so out-of-order HTTP responses can never overwrite newer edits, without clearing the form, stealing focus, or modifying the manual `#workout-result` banner.
  - A subtle inline status indicator next to `Registrar Sesión` reports auto-save progress and outcome (`Guardando...`, `✓ Guardado automáticamente HH:MM`, or `⚠️ Error al autoguardar`).
  - Clicking `Registrar Sesión` continues to work as an explicit manual save, cancelling pending debounce timers and syncing auto-save state on success.
- [ ] C2: **Non-Intrusive Set & Edit Auto-Save Triggers**:
  - Strength set inputs (`.set-weight`, `.set-reps`) and cardio duration inputs (`.set-duration-min`) trigger debounced auto-save on `input` (`700ms`) and immediate auto-save on `change`.
  - Pressing `Enter` inside a set row triggers an immediate auto-save of the completed set while appending and focusing the next empty set row (preserving existing `Enter` UX).
  - Removing a set row or removing an exercise block triggers immediate auto-save (no-op when 0 valid sets remain).
  - Editing `#workout-notes` (`change`) or finalizing an exercise name (`.ex-name` `change` or autocomplete `pick`) triggers immediate auto-save if at least one valid set exists, while raw keystrokes in `.ex-name` NEVER trigger auto-save so half-typed exercise names are never auto-created in the catalog.
- [ ] C3: **Auto-Hydrate Existing Daily Workout on Open & Date Change**:
  - Opening the app or changing `#workout-date` to a different calendar day (`DD-MM-YYYY`) loads any existing session for that day via `GET /api/get_workouts_by_day?date=...` into `#tab-workout` (notes, exercise blocks, strength/cardio modes, set values, 1RM estimates, and max-weight reference badges) while suppressing auto-save during hydration.
  - Switching tabs back and forth for the same already-hydrated date does not wipe in-progress edits.
  - Selecting a calendar day with no saved workout resets the form to a clean single empty exercise block.
- [ ] C4: **Tests, OpenSpec & Verification**:
  - UI/HTTP integration tests in `tests/integration/test_ui_web_routes.py` verify auto-save markup/handlers, daily hydration wiring, and progressive set-by-set daily overwrite round-trips (including `0 kg` bodyweight and cardio sets).
  - OpenSpec requirements (`docs/specs/openspec/requirements.md`) document set-level workout auto-save and daily hydration.
  - `node --check` on extracted inline JS and the full `pytest tests/ -v` suite pass cleanly.

## Clarify
> Resolved ambiguities

- **Q1: Should `#tab-workout` auto-load the existing workout for the selected date on page load and date change?**
  - **A:** Yes — approved by user. Hydrating the selected day's saved workout prevents reopening the app mid-workout from starting with a blank form and accidentally overwriting earlier exercises via daily overwrite.
- **Q2: How should incomplete rows and half-typed exercise names be handled during auto-save?**
  - **A:** Skip incomplete set rows and blank exercise names; never auto-save on raw `.ex-name` keystrokes (only on `change` / autocomplete pick) and never POST an empty `exercises: []` payload.
- **Q3: How should auto-save communicate status without disrupting data entry?**
  - **A:** Show a subtle inline status element (`#workout-autosave-status`) next to `Registrar Sesión` without clearing inputs, touching `#workout-result`, or moving focus; keep `Registrar Sesión` for explicit manual save.

## Plan
> Technical decisions + classification

- **Classification**: **Small** — changes are confined to `src/ui/html_generator.py` (Web UI HTML/JS) and `tests/integration/test_ui_web_routes.py` (plus OpenSpec/ODD docs), with zero backend API, service, or database schema changes (`POST /api/register_workout` daily overwrite and `GET /api/get_workouts_by_day` already exist).
- **D1 (Filtered Payload Builder & Single-Flight Queue)**:
  - Introduce `buildWorkoutPayload({ skipIncomplete })` shared between auto-save (`skipIncomplete: true`) and manual submit.
  - Implement `scheduleWorkoutAutoSave({ immediate = false })` and `flushWorkoutAutoSave()` using `workoutAutosaveTimer`, `workoutAutosaveInFlight`, `workoutAutosavePending`, `lastSavedWorkoutFingerprint`, and `isHydratingWorkout`.
  - Add `#workout-autosave-status` inline next to the submit button and update it via `setWorkoutAutoSaveStatus(text, tone)`.
- **D2 (Event Wiring)**:
  - Attach debounced/immediate triggers to `.set-weight`, `.set-reps`, `.set-duration-min`, `handleWorkoutFormKeydown` (`Enter`), `removeSetRow()`, `removeExerciseBlock()`, `.ex-name` `change` + autocomplete `onPick`, and `#workout-notes` `change`.
- **D3 (Daily Hydration)**:
  - Implement `loadWorkoutForSelectedDate({ force = false })` using `GET /api/get_workouts_by_day?date=DD-MM-YYYY` and `lastHydratedWorkoutDate`, invoked on initial page load and `#workout-date` `change` events (preserving existing `switchTab('workout')` line verbatim for test compatibility).

## Tasks
> Implementation checklist

- [x] T1: Add filtered workout payload builder, single-flight debounced/immediate auto-save queue, and subtle `#workout-autosave-status` indicator in `src/ui/html_generator.py` → verify: `node --check` (`JS_SYNTAX_OK`) + `pytest tests/integration/test_ui_web_routes.py -v` → PASSED (19 passed in 1.18s)
- [x] T2: Wire auto-save triggers on complete set `input`/`change`/`Enter`, set/block deletion, `.ex-name` `change`/autocomplete pick, and `#workout-notes` `change` in `src/ui/html_generator.py` → verify: `node --check` (`JS_SYNTAX_OK`) + `pytest tests/integration/test_ui_web_routes.py -v` → PASSED (19 passed in 0.87s)
- [x] T3: Add `loadWorkoutForSelectedDate()` hydration via `GET /api/get_workouts_by_day` on initial load and `#workout-date` calendar-day change in `src/ui/html_generator.py` → verify: `node --check` (`JS_SYNTAX_OK`) + `pytest tests/integration/test_ui_web_routes.py -v` → PASSED (19 passed in 0.89s)
- [ ] T4: Add UI/HTTP integration tests in `tests/integration/test_ui_web_routes.py` and update `docs/specs/openspec/requirements.md`, then run full `node --check` + `pytest tests/ -v` → verify: `node --check` + `pytest tests/ -v`

## Verification
> Comparison against the spec (filled in at close)

## Close
> Close (filled in at close)
