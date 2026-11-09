# hermes-e2e

> Feature: hermes-e2e

## Spec
> WHAT and WHY (no technology)

### Context

- The fitness AI system exposes 18 MCP tools via an MCP Server (`streamable-http` transport on port 9700 and `/mcp` endpoint).
- The primary actor is the Hermes Agent (an AI assistant on user mobile devices that translates voice/text into structured MCP tool calls).
- Unit and integration tests verify individual services and tools in isolation. However, there is no end-to-end verification proving that a real MCP client (`mcp.ClientSession` over the actual transport) can discover all 18 tools, maintain sessions, execute realistic multi-step user workflows (from client requests across protocol streams to database persistence and back), and interpret JSON responses.
- The backlog item #6 (`hermes-e2e`) calls for: "End-to-end verification with a real MCP client (Hermes)."

### Objective

Build a comprehensive end-to-end test suite (`tests/e2e/test_hermes_e2e.py`) simulating real Hermes Agent workflows through a real MCP `ClientSession` over ASGI/streamable-http transport against a test database. Verify that full user journeys (nutrition, goals, recipes, workouts, PRs, provisional entries, and error handling) work seamlessly across the protocol.

### Acceptance criteria

- [x] C1: An E2E test harness/fixture provides a real `ClientSession` connected via `streamable_http_client` to the MCP Server with clean database isolation.
- [x] C2: Protocol & Discovery: The client initializes, establishes protocol handshake, discovers all 18 tools with full schemas, parameter definitions, and descriptions matching `api-spec.md`.
- [x] C3: Nutrition & Goals E2E Workflow: Complete user journey: create ingredients -> set daily goal -> compose recipe -> register meals (direct & recipe) -> query daily summary, verifying exact macro calculations and progress against goals.
- [x] C4: Training & PR E2E Workflow: Complete user journey: catalog exercises -> register multi-set workouts across different dates -> verify automatic PR calculation (Epley formula and direct 1-rep attempts) -> query last workout, daily sessions, and personal records.
- [x] C5: Adaptive Flows (Fuzzy & Provisional): Hermes registers a meal with provisional ingredient/recipe -> resolves later; registers workouts with unknown exercise (auto-created) -> verifies responses and fuzzy search resolution.
- [x] C6: Error Resilience & Envelopes: Client triggers error conditions (invalid date format, missing required parameters, duplicate records, non-existent reads) and receives expected `{"status": "error", "code": ..., "message": ...}` with standard typed codes.
- [x] C7: Reliability & Speed: E2E test suite executes cleanly under `pytest` with zero leaks or timeouts, and full test suite remains green.

## Clarify
> Ambiguities and resolutions (filled interactively with the user)

- **Q1. Transport mechanism for E2E tests?** A: In-process ASGI transport via `httpx2.ASGITransport` + `mcp.client.streamable_http.streamable_http_client`. This tests the full protocol serialization, JSON-RPC, Starlette ASGI routes, session management, and SSE/HTTP streams without binding to a physical network port (preventing port collisions in CI/local runs).
- **Q2. Database isolation strategy?** A: Dedicated temporary SQLite file fixture per test module/session with migrations applied, ensuring thread-safe access between the async MCP server worker threads and test runners.
- **Q3. Test directory structure?** A: New `tests/e2e/` folder containing `conftest.py` (or shared client fixture) and `test_hermes_e2e.py`.
- **Q4. Real Hermes LLM calls or simulated Hermes tool invocation sequences?** A: Deterministic E2E simulation of Hermes tool invocation sequences. The test acts as the Hermes client issuing JSON-RPC tool calls, asserting protocol payloads and database state transitions.

## Plan
> Implementation plan (filled after clarify)

- **Mode:** fast — TDD per scenario, clean fixtures, full test suite pass.
- **T1 — E2E Harness & Client Fixture:** Setup `tests/e2e/conftest.py` with temporary database fixture, ASGI streamable-http app runner, and `ClientSession` client helper. Test discovery of 18 tools.
- **T2 — Nutrition & Daily Goals Flow:** Implement full multi-step journey (ingredients -> goal -> recipe -> meal -> summary) in `test_hermes_e2e.py`.
- **T3 — Training & PR Flow:** Implement workout logging, multi-set progression, Epley 1RM upserts, last workout queries, and PR tracking.
- **T4 — Provisional, Fuzzy & Error Resilience:** Test auto-creation of unknown exercises/provisional ingredients, fuzzy queries, and error envelopes.
- **T5 — Suite verification & Polish:** Full test suite run (`pytest`), ensure no leftovers or deprecations, verify criteria C1–C7.

## Tasks
> Check the box as each task is completed.

- [x] T1: E2E harness and client fixture (`tests/e2e/conftest.py` + discovery test)
- [x] T2: Nutrition & Daily Goals multi-step E2E flow
- [x] T3: Training & PR multi-step E2E flow
- [x] T4: Provisional, fuzzy matching & error handling E2E tests
- [x] T5: Polish, verification against spec, and full suite pass

## Verification
> Spec contrast (filled at close)

- [x] C1: `tests/e2e/conftest.py` implements `HermesTestClient` and `hermes_client` fixture connecting over `httpx2.ASGITransport` + `mcp.client.streamable_http.streamable_http_client` with an isolated temporary database file per test session.
- [x] C2: `test_hermes_protocol_handshake_and_tool_discovery` asserts discovery of all 18 tools, descriptions, and input schemas over protocol.
- [x] C3: `test_hermes_nutrition_and_goals_workflow` completes multi-step journey (ingredients, goals, recipes, meals, day summary with remaining macros).
- [x] C4: `test_hermes_training_and_pr_workflow` registers multi-set workouts, computes Epley estimated 1RM, exercises 1-rep attempts, verifies strict PR updates, queries last workout and daily sessions.
- [x] C5: `test_hermes_provisional_and_fuzzy_adaptive_flows` tests auto-creation of provisional ingredients and unknown exercises, finalized updates, and fuzzy queries.
- [x] C6: `test_hermes_error_resilience_and_typed_envelopes` tests invalid dates, units, duplicate sets, empty names, and non-existent queries, validating typed `invalid_input` and `not_found` error codes.
- [x] C7: Full test suite green (140 passed in 1.35s). Zero leaks, zero Spanish residuals.

## Close
> Close (filled at close)

- Date: 2026-11
- Next step: Review Proposed backlog items (#11 `html-artifacts`, #7 `db-robustness`, #9 `odd-merge-back`, #10 `google-health-api`).

