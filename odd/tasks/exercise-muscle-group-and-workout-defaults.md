# exercise-muscle-group-and-workout-defaults

> Feature: exercise-muscle-group-and-workout-defaults

## Spec

### Context
The exercise catalog (FR4.1) stores a free-text `muscle_group` per exercise. The workout logger form
pre-fills a hardcoded default exercise, the Exercises tab filter is a hardcoded list of 8 groups while
the create form accepts any free-text group, and there is no path to edit the `muscle_group` (or
`type`) of an existing exercise: `ExerciseService` exposes only create/get/find/list, `server.py`
registers only `list_exercises`/`create_exercise`, and the Exercises tab has a create form but no
edit control.

### Objective
1. Remove the hardcoded default exercise ("Press de Banca") from the workout form: start with one
   clean empty exercise block (same pattern as recipe rows).
2. Allow assigning/editing the muscle group (and type) of existing exercises: service method +
   `update_exercise` MCP tool (auto-exposed at `/api/update_exercise`) + inline row editor in the
   Exercises tab.
3. Make the muscle group filter accurate: options built dynamically from the groups actually present
   in the catalog (including custom free-text groups), case-insensitive exact match.

### Acceptance criteria
- [ ] C1: The workout form starts with exactly one exercise block with an empty name; the generated
      UI HTML contains no "Press de Banca" string.
- [ ] C2: `ExerciseService.update(exercise_id, muscle_group=None, type=None)` partially updates an
      existing exercise; unknown id, invalid type, or blank muscle_group raise ValidationError;
      omitted fields stay unchanged. Unit tests cover all paths.
- [ ] C3: `update_exercise` MCP tool is registered and reachable at `/api/update_exercise`; it
      returns the updated exercise dict; integration tests cover ok + error paths.
- [ ] C4: The Exercises tab table has a per-row muscle group editor (datalist of existing groups +
      free text) and a type select, saving via POST `/api/update_exercise` and refreshing the row.
- [ ] C5: The muscle group filter options are derived from catalog groups (unique, alphabetical,
      custom groups included, unknown shown as "Otros"); filtering is case-insensitive exact match;
      the current selection survives list refreshes.
- [ ] C6: `docs/specs/openspec/` updated: `update_exercise` endpoint in api-spec.md and the
      Exercises section requirement (FR8.5) mentions inline editing + dynamic filter.

## Clarify
- Q1: Is there an existing path to edit a muscle group?
- A1: No. `src/services/exercise_service.py` (L16-90) exposes only create/get_by_id/find_exact/
  find_by_name/list; `src/mcp/server.py` L77-79 registers only `list_exercises` and
  `create_exercise`; the Exercises tab has a create form but no edit control.
- Q2: Where does the "Press de Banca" default come from?
- A2: `src/ui/html_generator.py` L844 (`addExerciseBlock(name = 'Press de Banca')` default
  parameter) and L901 (initial call). The recipe form already uses the "start with 1 clean empty
  row instead of hardcoded ..." pattern (L839-840) - reuse it.
- Q3: Why is the filter not accurate today?
- A3: The filter select hardcodes 8 groups (L608-618) while the create form accepts any free-text
  group (L635, non-restrictive datalist), so custom groups are never filterable. `matchGroup`
  (L1404) compares the stored value case-insensitively and exactly.
- Q4: What is editable?
- A4: `muscle_group` and `type` only. Renaming an exercise is out of scope (backlog item wording:
  "assigning/editing muscle group on exercises").

## Plan
- Mode: fast (one pass, single pre-commit report at the end).
- TDD: T2 and T3 are RED-GREEN (tests first, then implementation). T1/T4/T5 are UI changes
  verified by the full pytest suite (integration HTML-generation tests) plus generated-HTML
  evidence. T6 is docs.
- D1: `ExerciseService.update(exercise_id, muscle_group=None, type=None)` - partial update;
  ValidationError (code `invalid_input`) for unknown id, invalid type, or blank muscle_group;
  `None` means "leave unchanged".
- D2: New MCP tool `update_exercise(exercise_id: int, muscle_group: str = None, type: str = None)`;
  the generic `/api/{tool_name}` dispatcher (server.py L128) exposes it automatically - no new
  route needed.
- D3: Edit UI is inline in the table row (group input with datalist + type select + save button),
  no separate edit panel.
- D4: Filter options are computed from `allExercises` on every list fetch (unique groups,
  alphabetical, unknown rendered as "Otros"); the current selection is preserved by value.
- D5: The workout form keeps exactly one initial block via `addExerciseBlock()` with `name = ''`.

## Tasks
- [ ] T1: Remove the hardcoded "Press de Banca" default: `addExerciseBlock(name = '')` and the
  initial `addExerciseBlock('')` call (one clean empty block). → files: src/ui/html_generator.py →
  verify: generated workout HTML contains no "Press de Banca"; full `pytest tests -q` green.
- [ ] T2: Add `ExerciseService.update(exercise_id, muscle_group=None, type=None)` with validation,
  plus unit tests (update muscle_group, update type, both, unknown id raises, invalid type
  raises, blank muscle_group raises, None fields unchanged). → files:
  src/services/exercise_service.py, tests/unit/test_exercise_service.py → verify:
  `pytest tests/unit/test_exercise_service.py -v` green with the new tests.
- [ ] T3: Add `update_exercise` MCP tool and register it in `server.py`; integration tests for ok,
  unknown id, and invalid type paths. → files: src/mcp/tools/exercise_tools.py, src/mcp/server.py,
  tests/integration/test_mcp_exercise_tools.py → verify:
  `pytest tests/integration/test_mcp_exercise_tools.py -v` green.
- [ ] T4: Inline muscle group editor in the Exercises tab table: per-row group input (datalist of
  existing groups + free text) and type select with a save button posting
  `/api/update_exercise`, re-fetching the list on success. → files: src/ui/html_generator.py →
  verify: full `pytest tests -q` green; generated exercise HTML contains the row editor and the
  `update_exercise` handler.
- [ ] T5: Dynamic muscle group filter: build the filter options from catalog groups (unique,
  alphabetical, unknown as "Otros"), keep the selected value across refreshes; remove the
  hardcoded option list. → files: src/ui/html_generator.py → verify: full `pytest tests -q` green;
  filter options derive from the catalog (no hardcoded group list in the generated HTML).
- [ ] T6: Update openspec: add the `update_exercise` endpoint to api-spec.md and mention inline
  muscle group editing + dynamic filter in requirements.md (FR8.5). → files:
  docs/specs/openspec/api-spec.md, docs/specs/openspec/requirements.md → verify: both docs mention
  `update_exercise` / dynamic filter; no residual hardcoded-group references.

## Verification
> (filled at close)

## Close
> (filled at close)
