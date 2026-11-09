# specs-completion

> Feature: specs-completion

## Spec
> WHAT and WHY (no technology)

### Context

- `docs/specs/openspec/` is the global specification (OpenSpec style) and is incomplete:
  - `requirements.md` — only Context + Stack (goals, functional and non-functional requirements missing).
  - `api-spec.md` — cut off at line 21 (conventions + first tool sentence); 0 of 18 tools documented.
  - `data-model.md` — nearly complete but carries stale details vs the code: `exercises.muscle_group` default documented as `'desconocido'` (code/migration: `'unknown'`) and `workout_sessions.date` storage format undocumented (Peewee `DateTimeField` = full datetime, while the public API exposes `DD-MM-YYYY[ HH:MM[:SS]]`).
- The implementation is complete and green on this branch: 6 services + 18 registered MCP tools (12 nutrition/goal + 6 training), 135 tests passing.
- Known doc/code inconsistencies to fix in CLARIFY: the `api-spec.md` convention line says datetimes use a `T` separator (`DD-MM-YYYYTHH:MM:SS`) while the implementation parses/formats `DD-MM-YYYY HH:MM[:SS]` (space-separated).
- The three docs must describe the **final system state** (18 tools), consistent with each other and with the code, per the backlog note: "Fill `requirements.md`, `api-spec.md` (cut off at line 21), `data-model.md` (empty)".

### Objective

Complete the OpenSpec documentation so the three files in `docs/specs/openspec/` are a full, accurate, mutually consistent reference of the system: `requirements.md` (what the system must do and why), `api-spec.md` (the complete 18-tool MCP contract: signatures, defaults, envelopes, error codes), and `data-model.md` (SQLite schema aligned with the committed migration and Peewee models). Docs only — no code changes.

### Acceptance criteria

- [ ] C1: `requirements.md` is complete: context, stack, goals/non-goals, actors, functional requirements per domain (nutrition catalog, meal logging, daily goals, training catalog, workout logging, personal records) and non-functional requirements (local-only, idempotent creation, fuzzy resolution, typed errors, language). No placeholders.
- [ ] C2: `api-spec.md` documents all 18 tools (4 ingredient + 4 recipe + 2 meal + 2 goal + 4 workout + 2 exercise) with: signature, argument table (name/type/required/default/description), success response shape, and the error codes each tool can return. Conventions fixed to match the code (dates `DD-MM-YYYY`, workout datetimes `DD-MM-YYYY HH:MM[:SS]`).
- [ ] C3: `data-model.md` aligned with `src/db/migrations/001_initial.sql` and `src/db/models.py` on this branch: `exercises.muscle_group` default `'unknown'`; `workout_sessions.date` documented as a stored datetime (Peewee `DateTimeField`) distinct from the `DD-MM-YYYY` user dates; all tables/indexes/constraints match the migration.
- [ ] C4: Cross-consistency: tool count (18) and error-code vocabulary identical across the three docs and the code; no Spanish residuals in the three files; full test suite still green (docs-only change).

## Clarify
> Ambiguities and resolutions (filled interactively with the user)

- **Q1. Which system state do the docs describe — `main` today (12 tools) or this branch (18 tools)?** A: this branch / final state (18 tools). The spec is the reference of the system, and `specs-completion` runs in parallel with the `services-training` merge.
- **Q2. `api-spec.md` convention line says `DD-MM-YYYYTHH:MM:SS` (T separator); the code parses `DD-MM-YYYY HH:MM[:SS]`.** A: code wins — the convention line is corrected to `DD-MM-YYYY` (dates) and `DD-MM-YYYY HH:MM[:SS]` (optional-time workout datetimes).
- **Q3. `data-model.md` documents `muscle_group` default `'desconocido'` but migration + Peewee say `'unknown'` on this branch.** A: align the doc to `'unknown'` (already fixed in the code by `services-training` T5).
- **Q4. How deep does `api-spec.md` go — MCP protocol internals or tool contracts?** A: tool contracts only (names, args, envelopes, errors). Transport/protocol details stay in the conventions block (local MCP, streamable-http).
- **Q5. Language of the docs?** A: English (per `translate-to-english`).

## Plan
> Implementation plan (filled after clarify)

- **Mode:** fast — docs-only, per-task verification by cross-checking against the code (signatures from `src/mcp/tools/*.py`, schema from `001_initial.sql` / `src/db/models.py`), full test suite + residual scan before each commit.
- **T1 — `requirements.md`:** keep header/context/stack; add Goals, Non-goals, Actors, Functional requirements (FR1 nutrition catalog, FR2 meal logging, FR3 daily goals + fallback chain, FR4 training catalog, FR5 workout registration, FR6 personal records with Epley/reps=1 rule), Non-functional requirements (local-only, idempotent, fuzzy threshold 0.6, typed error codes, English).
- **T2 — `api-spec.md`:** fix conventions (date formats, envelope, error-code table, pagination, units); tool index (18); one section per domain per tool: args table + success shape + applicable error codes, all taken from `src/mcp/tools/*.py` and the services.
- **T3 — `data-model.md`:** fix `muscle_group` default; document `workout_sessions.date` storage (datetime vs `DD-MM-YYYY` user dates) in Conventions + table; re-verify every table/index/constraint against the migration.
- **T4 — Consistency pass:** script/grep cross-check (18 tool names vs `server.py`; error codes vs `errors.py`; no `desconocido`/Spanish residuals); run `pytest`; close the task file.

## Tasks
> Check the box as each task is completed.

- [x] T1: Complete `docs/specs/openspec/requirements.md` (goals, actors, FR1–FR6, NFRs)
- [x] T2: Complete `docs/specs/openspec/api-spec.md` (conventions + 18 tools)
- [x] T3: Align `docs/specs/openspec/data-model.md` with migration + Peewee models
- [x] T4: Cross-consistency verification (tools/errors/format vs code) + full test suite

## Verification
> Spec contrast (filled at close)

- C1 `requirements.md`: goals, non-goals, actors, FR1–FR6 (nutrition, meals, goals + fallback, training, workouts, PRs with Epley/reps=1 rule), NFR1–NFR6. Behavior claims re-verified in code: recipe macros × quantity (`meal_service.py`), goal fallback chain + default-clear (`goal_service.py`), strict-greater PR update (`workout_service.py`). ✔
- C2 `api-spec.md`: 18 documented tools == 18 registered tools (`server.py`, checked programmatically); every signature/arg/default matches `inspect.signature` of `src/mcp/tools/*.py` (checked programmatically); error codes match `src/utils/errors.py` (`not_found`, `duplicate`, `invalid_input`, `conflict`, `internal`); date convention fixed to `DD-MM-YYYY[ HH:MM[:SS]]`. ✔
- C3 `data-model.md`: `muscle_group` default `'unknown'`; `workout_sessions.date` documented as stored datetime exception; every table/index/constraint matches `001_initial.sql`. ✔
- C4: No Spanish residuals in the three files (accent/word scan clean); full test suite green: **135 passed**.

## Close
> Close (filled at close)

- **Date:** 2026-11
- **Commits:** `552dce2` (T1) · `6a285ec` (T2) · `1cc012f` (T3)
- **Next:** PR to `main`; no code was changed, so merge order vs `feat/services-training` is irrelevant for code (this branch already contains the training code, so it merges cleanly on top).
