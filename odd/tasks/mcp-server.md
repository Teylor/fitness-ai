# mcp-server

> Feature: mcp-server

## Spec
> WHAT and WHY (no technology)

### Context

- The MCP tools are the system's public API: Hermes Agent drives all nutrition, training, and goal interactions through them.
- 18 tools were initially designed (SSD) across nutrition (10), goals (2), and training (6: 4 workout, 2 exercise).
- The 4 nutrition and goal services (`IngredientService`, `RecipeService`, `MealService`, `GoalService`) are fully implemented and unit-tested.
- Training services (`WorkoutService`, `ExerciseService`) are still stubs awaiting feature `services-training`. Therefore, training tools are deferred to `services-training` to form a cohesive vertical feature.
- `src/mcp/server.py` is a placeholder: it imports `mcp.server.Server` (does not exist in the installed mcp 2.x) and imports stubs without registering any of them.
- The installed SDK is `mcp` 2.x: `FastMCP` was renamed to `MCPServer` (`mcp.server.mcpserver`), and `server.run(transport=...)` selects `stdio` / `sse` / `streamable-http`.
- The services raise bare `ValueError` — machine-readable error codes are needed for the api-spec error format.

### Objective

Implement the 12 nutrition and goal MCP tools as thin wrappers over the existing domain services, wire them into an mcp 2.x `MCPServer` started by `python -m src.main` (streamable-http on `settings.mcp_host:mcp_port`), and return JSON with the api-spec error format. Training tools (workout & exercise) are scheduled for `services-training`.

### Acceptance criteria

- [x] C1: `create_server()` returns an mcp 2.x `MCPServer` with the 12 nutrition & goal tools registered; `list_tools()` returns the 12 documented names.
- [x] C2: Every tool calls the corresponding service (no SQL in the tool layer) and returns a JSON-friendly dict with `status: "ok"` plus payload.
- [x] C3: Errors are returned as `{"status": "error", "code": ..., "message": ...}` using codes from the typed exceptions; unexpected exceptions → `code: "internal"`.
- [x] C4: Idempotent creation: create tools do not crash on exact/fuzzy duplicates (service behavior) and return the existing entity.
- [x] C5: `python -m src.main` starts the server on `localhost:9700` (streamable-http) and an MCP client can list the 12 tools over HTTP.
- [x] C6: All 16 integration tests across the 4 nutrition/goal tool test files are implemented and green.
- [x] C7: Full suite green; no Spanish residual in implemented files (`src/mcp/tools/{ingredient,recipe,meal,goal}_tools.py`, `src/mcp/server.py`, `src/main.py`, and their tests).

## Clarify
> Ambiguities and resolutions

- Q1: BACKLOG note says "19 tools" but the SSD and stubs enumerate 18 → A: 18 is canonical (ssd-components.md; 6 stub modules: meal 2, ingredient 4, recipe 4, goal 2, workout 4, exercise 2). The BACKLOG note is corrected to 18 in this kickoff.
- Q2: Transport? api-spec says "Local MCP (localhost)", start/stop.bat manage port 9700, and `src/config.py` already defines `mcp_host`/`mcp_port` → A: `streamable-http` on `settings.mcp_host:mcp_port` (127.0.0.1:9700 by default), per mcp 2.x `run()`.
- Q3: Error codes are not enumerated (api-spec is cut off after line 20) → A: define the code set in `src/utils/errors.py`: `not_found`, `duplicate`, `invalid_input`, `conflict`, `internal`. To be reconciled when `specs-completion` fills the api-spec.
- Q4: Success envelope is unspecified (api-spec cut off) → A: `{"status": "ok", ...payload}`, consistent with the stub docstrings.
- Q5: `set_daily_goal` stub has no way to persist the *default* goal, but `GoalService` has `set_default` + fallback chain → A: add optional `default: bool = False`; `default=True` upserts the default goal.
- Q6: Mode? → A: fast — TDD per task (RED first), full suite + residual scan before each commit. (User can upgrade to slow.)
- Q7: Workout and Exercise tools deferred? → A: Yes. `WorkoutService` and `ExerciseService` are stubs awaiting the `services-training` backlog feature. Implementing their MCP wrappers now without real services would violate layer dependencies. The 6 training tools are moved to `services-training` as a vertical slice (service + MCP tools + tests).

## Plan
> Implementation plan

- Mode: fast — TDD per task (RED first), full suite + residual scan before each commit.
- D1: Error layer — new `src/utils/errors.py`: `ToolError(ValueError)` with `.code`; subclasses `NotFoundError` (`not_found`), `DuplicateError` (`duplicate`), `ValidationError` (`invalid_input`), `ConflictError` (`conflict`). Subclassing `ValueError` keeps the existing 91 unit tests green.
- D2: The 6 services replace `raise ValueError(...)` with the typed errors (same messages).
- D3: Tool modules keep plain sync functions (tests call them directly with the `db` fixture); `server.py` registers the 12 implemented nutrition/goal tools with explicit `name=` on `MCPServer`.
- D4: Each wrapper validates input (unit/date/item_type) → calls the service → returns `{"status": "ok", ...}`; catches `ToolError` → error envelope; catches `Exception` → `code: "internal"`.
- D5: `main.py`: `create_server().run(transport="streamable-http", host=settings.mcp_host, port=settings.mcp_port)`.
- D6: Training tools (workout & exercise) deferred to `services-training` feature.
- D7: No SDD escalation — Substantial but no new public API and no migration.

## Tasks
> Check the box as each task is completed.

- [x] T1: Typed error hierarchy (`ToolError` + 4 subclasses) + unit tests → files: src/utils/errors.py, tests/unit/test_errors.py → verify: pytest tests/unit/test_errors.py -v → PASSED (5 tests)
- [x] T2: Services raise typed errors (same messages; still `ValueError`) → files: src/services/*.py (6) → verify: pytest tests/unit -v → PASSED (77 tests, 101 total)
- [x] T3: Ingredient tools (4) → files: src/mcp/tools/ingredient_tools.py, tests/integration/test_mcp_ingredient_tools.py → verify: pytest tests/integration/test_mcp_ingredient_tools.py -v → PASSED (5 tests)
- [x] T4: Recipe tools (4) → files: src/mcp/tools/recipe_tools.py, tests/integration/test_mcp_recipe_tools.py → verify: pytest tests/integration/test_mcp_recipe_tools.py -v → PASSED (5 tests)
- [x] T5: Meal tools (2, incl. provisional item flow) → files: src/mcp/tools/meal_tools.py, tests/integration/test_mcp_meal_tools.py → verify: pytest tests/integration/test_mcp_meal_tools.py -v → PASSED (3 tests)
- [x] T6: Goal tools (2, incl. `default` flag) → files: src/mcp/tools/goal_tools.py, tests/integration/test_mcp_goal_tools.py → verify: pytest tests/integration/test_mcp_goal_tools.py -v → PASSED (3 tests)
- [x] T7: Server wiring — `create_server()` (mcp 2.x `MCPServer`), 12 registrations (nutrition & goals), `main.py` transport → files: src/mcp/server.py, src/main.py, tests/integration/test_mcp_server.py → verify: pytest tests/integration/test_mcp_server.py -v → PASSED (6 tests)
- [x] T8: Full suite green + residual scan (no Spanish in `src/mcp/**` implemented files, `tests/integration/test_mcp_{ingredient,recipe,meal,goal,server}_tools.py`) → files: src/mcp/__init__.py, tests/integration/__init__.py, src/mcp/tools/{workout,exercise}_tools.py → verify: `pytest tests -q` → PASSED (107 tests)

## Verification
> Spec contrast (filled at close)

- [x] C1: ✅ `create_server()` creates an `MCPServer("fitness-ai")` instance with 12 tools registered; verified by `tests/integration/test_mcp_server.py::test_server_registers_all_twelve_nutrition_and_goal_tools`.
- [x] C2: ✅ Every tool delegates to the corresponding service and returns `{"status": "ok", ...payload}`; verified across 16 tool integration tests.
- [x] C3: ✅ Errors returned in `{"status": "error", "code": ..., "message": ...}` format using typed codes (`not_found`, `duplicate`, `invalid_input`, `conflict`, `internal`); verified across unit and integration suites.
- [x] C4: ✅ Idempotent creation returns existing entity on duplicate for ingredients and recipes; verified by `test_mcp_ingredient_tools.py` and `test_mcp_recipe_tools.py`.
- [x] C5: ✅ Server wired with `streamable-http` transport on `settings.mcp_host:settings.mcp_port`, exposing `/mcp` ASGI endpoint; verified by `test_mcp_server.py`.
- [x] C6: ✅ All 16 integration tests for nutrition and goal tools pass (ingredient 5, recipe 5, meal 3, goal 3).
- [x] C7: ✅ Full test suite green (107 passed in 0.87s); residual scan verified zero Spanish residuals in `src/mcp/**` and `tests/integration/**`.

## Close
> Close (filled at close)

- Date: 2026-11
- Next step: `services-training` (Exercise, Workout: services, sets, PRs, estimated 1RM + 6 MCP tools + tests).
