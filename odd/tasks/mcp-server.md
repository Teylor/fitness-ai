# mcp-server

> Feature: mcp-server

## Spec
> WHAT and WHY (no technology)

### Context

- The MCP tools are the system's public API: Hermes Agent drives all nutrition, training, and goal interactions through them.
- 18 tools are designed (SSD) and stubbed in `src/mcp/tools/` with signatures, but every body is `...`.
- `src/mcp/server.py` is a placeholder: it imports `mcp.server.Server` (does not exist in the installed mcp 2.x) and imports the 18 stubs without registering any of them.
- The installed SDK is `mcp` 2.x: `FastMCP` was renamed to `MCPServer` (`mcp.server.mcpserver`), and `server.run(transport=...)` selects `stdio` / `sse` / `streamable-http`.
- The 6 services exist and are unit-tested (91 tests) but raise bare `ValueError` — no machine-readable error codes for the api-spec error format.

### Objective

Implement the 18 MCP tools as thin wrappers over the existing services, wire them into an mcp 2.x `MCPServer` started by `python -m src.main` (streamable-http on `settings.mcp_host:mcp_port`), and return JSON with the api-spec error format, so Hermes can drive the whole system.

### Acceptance criteria

- [ ] C1: `create_server()` returns an mcp 2.x `MCPServer` with exactly 18 tools registered; `list_tools()` returns the 18 documented names.
- [ ] C2: Every tool calls the corresponding service (no SQL in the tool layer) and returns a JSON-friendly dict with `status: "ok"` plus payload.
- [ ] C3: Errors are returned as `{"status": "error", "code": ..., "message": ...}` using codes from the typed exceptions; unexpected exceptions → `code: "internal"`.
- [ ] C4: Idempotent creation: create tools do not crash on exact/fuzzy duplicates (service behavior) and return the existing entity.
- [ ] C5: `python -m src.main` starts the server on `localhost:9700` (streamable-http) and an MCP client can list the 18 tools over HTTP.
- [ ] C6: All 24 integration test stubs (6 files) are implemented and green.
- [ ] C7: Full suite green; no Spanish residual in `src/mcp/**` and `tests/integration/test_mcp_*.py`.

## Clarify
> Ambiguities and resolutions

- Q1: BACKLOG note says "19 tools" but the SSD and stubs enumerate 18 → A: 18 is canonical (ssd-components.md; 6 stub modules: meal 2, ingredient 4, recipe 4, goal 2, workout 4, exercise 2). The BACKLOG note is corrected to 18 in this kickoff.
- Q2: Transport? api-spec says "Local MCP (localhost)", start/stop.bat manage port 9700, and `src/config.py` already defines `mcp_host`/`mcp_port` → A: `streamable-http` on `settings.mcp_host:mcp_port` (127.0.0.1:9700 by default), per mcp 2.x `run()`.
- Q3: Error codes are not enumerated (api-spec is cut off after line 20) → A: define the code set in `src/utils/errors.py`: `not_found`, `duplicate`, `invalid_input`, `conflict`, `internal`. To be reconciled when `specs-completion` fills the api-spec.
- Q4: Success envelope is unspecified (api-spec cut off) → A: `{"status": "ok", ...payload}`, consistent with the stub docstrings.
- Q5: `set_daily_goal` stub has no way to persist the *default* goal, but `GoalService` has `set_default` + fallback chain → A: add optional `default: bool = False`; `default=True` upserts the default goal.
- Q6: Mode? → A: fast — TDD per task (RED first), full suite + residual scan before each commit. (User can upgrade to slow.)

## Plan
> Implementation plan

- Mode: fast — TDD per task (RED first), full suite + residual scan before each commit.
- D1: Error layer — new `src/utils/errors.py`: `ToolError(ValueError)` with `.code`; subclasses `NotFoundError` (`not_found`), `DuplicateError` (`duplicate`), `ValidationError` (`invalid_input`), `ConflictError` (`conflict`). Subclassing `ValueError` keeps the existing 91 unit tests green.
- D2: The 6 services replace `raise ValueError(...)` with the typed errors (same messages).
- D3: Tool modules keep plain sync functions (tests call them directly with the `db` fixture); `server.py` registers each with explicit `name=` on `MCPServer`.
- D4: Each wrapper validates input (unit/date/item_type) → calls the service → returns `{"status": "ok", ...}`; catches `ToolError` → error envelope; catches `Exception` → `code: "internal"`.
- D5: `main.py`: `create_server().run(transport="streamable-http", host=settings.mcp_host, port=settings.mcp_port)`.
- D6: No SDD escalation — Substantial (~25 files) but no new public API (tools already designed in SSD) and no migration.

## Tasks
> Check the box as each task is completed.

- [x] T1: Typed error hierarchy (`ToolError` + 4 subclasses) + unit tests → files: src/utils/errors.py, tests/unit/test_errors.py → verify: pytest tests/unit/test_errors.py -v → PASSED (5 tests)
- [x] T2: Services raise typed errors (same messages; still `ValueError`) → files: src/services/*.py (6) → verify: pytest tests/unit -v → PASSED (77 tests, 101 total)
- [x] T3: Ingredient tools (4) → files: src/mcp/tools/ingredient_tools.py, tests/integration/test_mcp_ingredient_tools.py → verify: pytest tests/integration/test_mcp_ingredient_tools.py -v → PASSED (5 tests)
- [ ] T4: Recipe tools (4) → files: src/mcp/tools/recipe_tools.py, tests/integration/test_mcp_recipe_tools.py → verify: 5 stub tests green
- [ ] T5: Meal tools (2, incl. provisional item flow) → files: src/mcp/tools/meal_tools.py, tests/integration/test_mcp_meal_tools.py → verify: 3 stub tests green
- [ ] T6: Goal tools (2, incl. `default` flag) → files: src/mcp/tools/goal_tools.py, tests/integration/test_mcp_goal_tools.py → verify: 3 stub tests green
- [ ] T7: Workout tools (4) → files: src/mcp/tools/workout_tools.py, tests/integration/test_mcp_workout_tools.py → verify: 5 stub tests green
- [ ] T8: Exercise tools (2) → files: src/mcp/tools/exercise_tools.py, tests/integration/test_mcp_exercise_tools.py → verify: 3 stub tests green
- [ ] T9: Server wiring — `create_server()` (mcp 2.x `MCPServer`), 18 registrations, `main.py` transport → files: src/mcp/server.py, src/main.py, tests/integration/test_mcp_server.py → verify: `list_tools()` == 18 names; HTTP smoke (ephemeral port, list over HTTP)
- [ ] T10: Full suite green + residual scan (no Spanish in `src/mcp/**`, `tests/integration/test_mcp_*.py`) → files: (fixes only) → verify: `pytest tests -q` (91 + 24 + new)

## Verification
> Spec contrast (filled at close)

## Close
> Close (filled at close)
