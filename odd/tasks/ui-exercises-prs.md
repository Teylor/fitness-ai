# ui-exercises-prs

> Feature: ui-exercises-prs

## Spec
> WHAT and WHY (no technology)

### Context
- The application currently catalogs exercises and logs workout sessions with sets (reps, weight, duration, distance).
- The Web UI has tabs for Comidas, Recetas, Ingredientes, Entrenamientos, and Resumen, but lacks a dedicated view to browse exercises and view their strength metrics.
- Users want a dedicated "Ejercicios" section in the UI showing all exercises (e.g., Press banca, Press militar, etc.) with two distinct and essential performance records:
  1. **Estimated 1RM PR**: The highest estimated 1RM achieved for that exercise (using the Epley formula `weight * (1 + reps / 30)`, or exact weight when reps = 1).
  2. **Max Weight Set (Peso más alto)**: The heaviest weight ever lifted in any set, accompanied by its repetitions. For example, if during workouts a user completed sets of `20 kg x 10 reps`, `22 kg x 6 reps`, and `18 kg x 12 reps`, the highest weight is `22 kg` and the UI must display `22 kg x 6 reps`.
- If an exercise has no logged sets (or is a non-weight exercise like Plank or Run), these fields display `-`.

### Objective
Provide a dedicated "Ejercicios" view in the UI showing the catalog of exercises with their muscle group, exercise type, estimated 1RM PR, and heaviest weight lifted with its repetitions, backed by backend services and MCP/API query capabilities.

### Acceptance criteria

- [x] C1: `WorkoutService.get_exercise_stats(exercise_id: Optional[int] = None)` aggregates performance statistics across all sets in historical workout sessions:
  - `estimated_1rm`: Maximum estimated 1RM (rounded to 1 decimal place).
  - `estimated_1rm_date`: Date (DD-MM-YYYY) of the highest 1RM set.
  - `max_weight`: Highest weight lifted (float).
  - `max_weight_reps`: Repetitions achieved at `max_weight`. If multiple sets share the same highest weight, the set with the most reps is chosen.
  - `max_weight_date`: Date (DD-MM-YYYY) of the max weight set.
  - Returns `None` for exercises without logged weight sets.
- [x] C2: `list_exercises` tool in `src/mcp/tools/exercise_tools.py` supports `include_prs: bool = False` (or string query param `'true'`). When enabled, each returned exercise dictionary includes `pr`: `{ "estimated_1rm", "estimated_1rm_date", "max_weight", "max_weight_reps", "max_weight_date" }` or `None`.
- [x] C3: Web UI (`src/ui/html_generator.py`):
  - Adds a new navigation tab `💪 Ejercicios` (`active_tab == 'exercise'`).
  - Section `#tab-exercise` includes:
    - Search input to filter exercises by name.
    - Muscle group selector to filter by muscle group.
    - An "Añadir Ejercicio" form/section to easily catalog new exercises (`name`, `muscle_group`, `type`).
    - A responsive table/list displaying: Exercise name, Muscle group, Type, Estimated 1RM (`{e1rm} kg` or `-`), and Heaviest set (`{max_weight} kg × {max_weight_reps} reps` or `-`).
    - Dynamic data loading via `/api/list_exercises?include_prs=true`.
- [x] C4: Unit tests in `tests/unit/test_workout_service.py` and integration tests in `tests/integration/test_mcp_exercise_tools.py` and `tests/integration/test_ui_web_routes.py` verifying PR and max-weight set extraction, API responses, and UI generation.
- [x] C5: OpenSpec updated in `docs/specs/openspec/` (`requirements.md`, `api-spec.md`).

## Clarify
> Ambiguities and resolutions

- **Q1: What if a user performed multiple sets at the same max weight?**
  - **A**: The set with the greatest number of repetitions is selected (e.g., `22 kg x 6` beats `22 kg x 4`). If both weight and reps are tied, the most recent date is chosen.
- **Q2: Does Estimated 1RM always correspond to the heaviest weight set?**
  - **A**: No, and this is why both metrics are displayed. A set with `20 kg x 10 reps` yields an estimated 1RM of `26.7 kg`, while `22 kg x 6 reps` yields an estimated 1RM of `26.4 kg`. The user explicitly wants to see both: the estimated 1RM PR (`26.7 kg`) and the heaviest weight lifted with its repetitions (`22 kg x 6 reps`).
- **Q3: What should be displayed for `time` or `distance` exercises, or exercises with no logged sets?**
  - **A**: The UI displays `-` for both 1RM and Heaviest Set.
- **Q4: Can exercises be added from this new tab?**
  - **A**: Yes. Just like the Ingredients tab has an inline registration form, the Exercises tab includes an "Añadir Ejercicio" form so users can register exercises without having to go through workout logs.

## Plan
> Implementation plan

- **T1 — WorkoutService Exercise Stats Calculation**:
  - Implement `WorkoutService.get_exercise_stats(exercise_id: Optional[int] = None) -> Dict[int, dict]`.
  - Add unit tests verifying calculation of `estimated_1rm` and `max_weight` / `max_weight_reps` across sets.
- **T2 — MCP Tool & API Integration**:
  - Update `list_exercises` in `src/mcp/tools/exercise_tools.py` to support `include_prs: bool = False`.
  - Add integration tests verifying `list_exercises(include_prs=True)`.
- **T3 — Web UI Exercises Tab**:
  - Update `VALID_FORM_TYPES` in `src/ui/html_generator.py` to include `"exercise"`.
  - Add tab button `💪 Ejercicios` and tab section `#tab-exercise`.
  - Implement exercise creation form and exercises table with PR & Max Weight badges.
  - Implement `fetchExercisesList()` JavaScript function and filtering.
- **T4 — Integration & E2E Verification**:
  - Add test in `tests/integration/test_ui_web_routes.py` for `/ui/exercise` and `/api/list_exercises?include_prs=true`.
  - Run full test suite (`pytest`).
- **T5 — OpenSpec & Backlog Closure**:
  - Update `docs/specs/openspec/requirements.md` and `api-spec.md`.
  - Update `odd/BACKLOG.md` and create PR to `main`.

## Tasks

- [x] T1: Implement `WorkoutService.get_exercise_stats` and unit tests
- [x] T2: Update `list_exercises` tool with `include_prs` and integration tests
- [x] T3: Add Exercises tab and table in `src/ui/html_generator.py`
- [x] T4: Verify with full test suite
- [x] T5: Update OpenSpec and finalize backlog item

## Verification
- Unit tests: `tests/unit/test_workout_service.py` (24/24 passing, including max weight vs 1RM separation and tie breaking)
- Integration tests: `tests/integration/test_mcp_exercise_tools.py` (6/6 passing), `tests/integration/test_mcp_ui_tools.py` (3/3 passing), `tests/integration/test_ui_web_routes.py` (6/6 passing)
- Full suite: 181/181 passing (`pytest`)
- Live server: tested `/ui/exercise` (HTTP 200) and `/api/list_exercises?include_prs=true` (HTTP 200) on port 9700.
