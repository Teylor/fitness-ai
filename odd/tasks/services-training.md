# services-training

> Feature: services-training

## Spec
> WHAT and WHY (no technology)

### Context

- The training domain is the last unimplemented vertical: nutrition + goals were delivered by `services-nutrition` and `mcp-server` (12 of the 18 SSD tools registered).
- The DB layer already ships the complete training schema: `exercises`, `workout_sessions`, `exercise_sets`, `personal_records` (migration `001_initial.sql` + Peewee models in `src/db/models.py`). No new migration is expected.
- Building blocks already exist and are tested: `src/utils/errors.py` (typed error hierarchy: `not_found`, `duplicate`, `invalid_input`, `conflict`, `internal`), `src/utils/fuzzy.py` (normalize + `fuzzy_match`), `src/utils/macros.py::estimate_1rm` (Epley: `weight × (1 + reps/30)`).
- Service stubs with fixed signatures: `ExerciseService` (`create`, `get_by_id`, `find_by_name`, `list`) and `WorkoutService` (`register_session`, `get_last_workout`, `get_personal_record`, `get_by_day`, `_check_and_update_pr`).
- Tool stubs with fixed signatures: 4 workout tools (`register_workout`, `get_last_workout`, `get_personal_record`, `get_workouts_by_day`) + 2 exercise tools (`list_exercises`, `create_exercise`); `server.py` currently registers 12 tools.
- Known inconsistencies to resolve in CLARIFY: session date format (dataclass ISO string vs Peewee `DateTimeField` vs the `DD-MM-YYYY` user-date convention used by nutrition); PR semantics for `time` / `distance` exercises (the PR table only carries weight/reps/1RM fields); Spanish residuals in `src/models/*.py` docstrings, `src/utils/macros.py`, `src/utils/fuzzy.py`, and the `exercises.muscle_group` migration default `'desconocido'` vs Peewee default `'unknown'`.

### Objective

Implement `ExerciseService` and `WorkoutService` as the training domain layer over the existing Peewee models (no schema changes), register the remaining 6 training MCP tools (4 workout + 2 exercise) to complete the 18-tool public API, and return JSON with the established envelopes (`status: "ok"` / `status: "error"` + typed codes). Keep the thin-wrapper pattern (no SQL in the tool layer). PRs are auto-computed on registration using the Epley estimated 1RM, with at most one PR row per exercise.

### Acceptance criteria

- [ ] C1: `ExerciseService` implemented: `create` (idempotent — exact/normalized-name duplicates return the existing exercise, no crash), `get_by_id`, `find_by_name` (fuzzy, reusing `utils/fuzzy`), `list` (search + muscle_group filter, limit/offset). Typed errors only (`not_found`, `invalid_input`, `duplicate`).
- [ ] C2: `WorkoutService.register_session` creates the session + all sets in a single transaction, resolves exercise names (auto-creating missing ones per CLARIFY), computes per-set estimated 1RM (Epley) for `weight_reps` sets, and upserts the exercise PR only when the new estimated 1RM is strictly greater than the stored one. Returns the session + the list of created/updated PRs.
- [ ] C3: `WorkoutService` read operations implemented: `get_last_workout(exercise_name)` (most recent session + its sets for the exercise), `get_personal_record(exercise_name)` (PR or `not_found`), `get_by_day(date)` (all sessions of the day with their sets).
- [ ] C4: The 6 training tools are implemented as thin wrappers over the services (no SQL in the tool layer) and registered in `server.py` → `list_tools()` returns the full 18-tool set.
- [ ] C5: Tool envelopes consistent with the nutrition tools: `{"status": "ok", ...payload}` on success, `{"status": "error", "code": ..., "message": ...}` on typed errors, unexpected exceptions → `code: "internal"`.
- [ ] C6: Unit tests for both services + integration tests for the 6 tools (following the patterns of `tests/unit/test_*service*.py` and `tests/integration/test_mcp_*_tools.py`); full test suite green.
- [ ] C7: No Spanish residuals in the training files this feature touches (`src/services/exercise_service.py`, `src/services/workout_service.py`, `src/models/exercise.py`, `src/models/workout_session.py`, `src/models/exercise_set.py`, `src/models/personal_record.py`, `src/mcp/tools/workout_tools.py`, `src/mcp/tools/exercise_tools.py`, `src/utils/macros.py`, `src/utils/fuzzy.py`, and their tests); the `exercises.muscle_group` default is aligned between migration and Peewee model (value decided in CLARIFY).

## Clarify
> Ambiguities and resolutions (filled interactively with the user)

- **Q1. Public date format for workouts.** A: `DD-MM-YYYY` (consistent with meals); optional time part (`DD-MM-YYYY HH:MM[:SS]`); default = now. Stored internally as ISO datetime (Peewee `DateTimeField`). `register_workout` and `get_workouts_by_day` accept `DD-MM-YYYY` with optional time.
- **Q2. PRs for `time`/`distance` exercises.** A: only `weight_reps` exercises get PRs; `get_personal_record` returns `not_found` for the other types.
- **Q3. Unknown exercise in `register_workout`.** A: auto-create it with `muscle_group="unknown"` and continue in the same call; auto-created exercises are reported in the response.
- **Q4. PR update rule.** A: the PR triple (`max_weight`, `max_reps`, `estimated_1rm`) comes from the set with the highest estimated 1RM. Estimated 1RM: a set with `reps = 1` uses the **exact weight** as the 1RM (direct attempt); any other set uses Epley (`weight × (1 + reps/30)`). The PR row is created/updated only when the new estimated 1RM is strictly greater than the stored one.
- **Q5. `set_number`.** A: client-provided, must be unique per (session, exercise), `1..n` (e.g. set 1: 100 kg x 8, set 2: 105 kg x 5 — weight may vary between sets). Duplicates or invalid numbers -> `invalid_input`.
- **Q6. `create_exercise` idempotency.** A: do not create duplicates — exact match after normalization (case/accents) returns the existing row (`existing: true`); fuzzy matches do NOT block creation.
- **Q7. `muscle_group` default.** A: `unknown` everywhere (Peewee model, `001_initial.sql`, dataclass).

## Plan
> Implementation plan (filled after clarify)

- **Mode:** fast — per-task TDD (RED first), full test suite + residual scan before each commit.
- **T1 — `ExerciseService`:** Peewee-backed. `create` idempotent (exact/normalized-name duplicate returns the existing row, `type` validated against `weight_reps|time|distance`, empty name -> `invalid_input`); `get_by_id` -> `Optional`; `find_by_name` = exact -> normalized exact -> fuzzy (`utils/fuzzy`, threshold 0.6); `list` (name search, `muscle_group` filter, `limit`/`offset`). Tests: `tests/unit/test_exercise_service.py` (mirror `test_ingredient_service.py` patterns).
- **T2 — `WorkoutService.register_session`:** single transaction: create session (date `DD-MM-YYYY[ HH:MM[:SS]]`, default now) + sets; resolve exercise names via `ExerciseService.find_by_name`, auto-creating missing ones (`muscle_group="unknown"`); validate `set_number` unique per (session, exercise) and per-type set fields (`weight_reps`: `reps`+`weight` · `time`: `duration` · `distance`: `distance`) -> `invalid_input`; PR upsert for `weight_reps` only: best set by estimated 1RM (reps=1 -> exact weight; else Epley), create/update only when strictly greater. Returns `{session, sets, new_prs, auto_created}`.
- **T3 — WorkoutService reads:** `get_last_workout(exercise_name)` (most recent session + sets), `get_personal_record(exercise_name)` (PR or none), `get_by_day(date)` (sessions + sets of the day). Extend `tests/unit/test_workout_service.py`.
- **T4 — 6 MCP tools:** thin wrappers (no SQL) with the established envelopes, registered in `server.py` -> 18 tools; update the tool-count assertion in `tests/integration/test_mcp_server.py` if present. Tests: `tests/integration/test_mcp_workout_tools.py`, `tests/integration/test_mcp_exercise_tools.py`.
- **T5 — Polish:** English docstrings for the training dataclasses (`src/models/{exercise,workout_session,exercise_set,personal_record}.py`) and `src/utils/{macros,fuzzy}.py`; `unknown` default in `001_initial.sql`; residual scan + full suite green.

## Tasks
> Check the box as each task is completed.

- [x] T1: Implement `ExerciseService` (idempotent create, get_by_id, fuzzy find_by_name, list) — `tests/unit/test_exercise_service.py`
- [x] T2: Implement `WorkoutService.register_session` (transactional, auto-create exercises, set validation, PR upsert)
- [x] T3: Implement WorkoutService reads (`get_last_workout`, `get_personal_record`, `get_by_day`)
- [ ] T4: Implement the 6 training MCP tools + register in `server.py` (18 tools)
- [ ] T5: English translation of training dataclasses/utils + `unknown` default in `001_initial.sql` + residual scan + full suite

## Verification
> Spec contrast (filled at close)

- (pending)

## Close
> Close (filled at close)

- (pending)
