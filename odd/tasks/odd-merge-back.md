# Feature: odd-merge-back

> Reflux all met acceptance criteria, tools, and schema improvements from task deltas back into global OpenSpec documentation.

## Spec
> What and why (no technology)

### Context
- Through successive features (`html-artifacts`, `google-health-api`, `ui-catalog-and-edit`, `ui-new-features`, `ui-full-daily-summary`, `ui-delete-actions`, `google-health-food-sync`, `db-robustness`), the codebase evolved significantly.
- Currently, the global specification in `docs/specs/openspec/` only documents the initial 18 tools and 10 tables, missing:
  - Google Health API v4 integration and automatic OAuth 2.0 token renewal.
  - Interactive Generative UI tools (`get_ui_form`, `/ui`, `/api/` bridge).
  - Deletion tools (`delete_meal`, `delete_ingredient`, `delete_recipe`).
  - Activity & Health metrics (`log_steps`, `get_health_metrics`, and table `step_logs`).
  - Database reliability conventions (WAL journal mode, foreign keys, busy timeout, atomic context manager).
- The global specification must serve as the single source of truth for Hermes Agent, developers, and future coding agents.

### Objective
- Synchronize `docs/specs/openspec/requirements.md`, `docs/specs/openspec/api-spec.md`, and `docs/specs/openspec/data-model.md` to fully reflect the 26 MCP tools, 12 Peewee database tables, and updated requirements.
- Formalize Rule 6 in `odd/BACKLOG.md` so that future features reflux specification updates before closing.

### Acceptance Criteria
- [x] C1: **Requirements Reflux**: `requirements.md` includes FR7 (Google Health & Activity Tracking), FR8 (Interactive UI Artifacts & Dashboards), FR9 (Catalog and Meal Deletion), and NFR7 (Storage Robustness & Concurrency).
- [x] C2: **API Specification Reflux**: `api-spec.md` lists and documents all 26 MCP tools (including `delete_meal`, `log_steps`, `get_health_metrics`), their parameters, responses, error codes, and HTTP bridge endpoints.
- [x] C3: **Data Model Reflux**: `data-model.md` includes `step_logs` (12 models total) and documents SQLite PRAGMAs (`foreign_keys`, `journal_mode = wal`, `busy_timeout = 5000`, `synchronous = normal`).
- [x] C4: **Rule Permanence**: `odd/BACKLOG.md` Rule 6 explicitly mandates updating `docs/specs/openspec/` as part of closing any feature that impacts specifications.

## Clarify
> Ambiguities resolved

- **Q1. Does this feature introduce code changes?**
  - A: No, it is a docs-and-specification synchronization feature. The code and test suite are already complete and green (168 tests passing).
- **Q2. How many tools are active?**
  - A: Exactly 26 MCP tools registered in `src/mcp/server.py`: Ingredients (4), Recipes (4), Meals (3), Goals (2), Workouts (4), Exercises (2), UI (1), Health & Activity (6).

## Plan
> Technical decisions + classification

- **Classification**: Normal (documentation synchronization).
- **T1**: Update `docs/specs/openspec/requirements.md` with FR7–FR9 and NFR7.
- **T2**: Update `docs/specs/openspec/api-spec.md` with complete 26-tool index, schemas for `delete_meal`, `log_steps`, `get_health_metrics`, and HTTP routes.
- **T3**: Update `docs/specs/openspec/data-model.md` with `step_logs` table schema and SQLite PRAGMA configuration.
- **T4**: Verify tests and consistency, update task file, commit and open Pull Request.

## Tasks
> Implementation checklist

- [x] T1: Reflux requirements into `docs/specs/openspec/requirements.md`.
- [x] T2: Reflux API tool definitions into `docs/specs/openspec/api-spec.md`.
- [x] T3: Reflux schema and pragmas into `docs/specs/openspec/data-model.md`.
- [x] T4: Run test suite and check consistency.

## Verification
> Spec contrast (filled at close)

- **C1 (Requirements Reflux)**: `requirements.md` was augmented with FR7 (Google Health & Activity Tracking), FR8 (Interactive UI Artifacts & Dashboards), FR9 (Catalog and Meal Deletion), and NFR7 (Storage Robustness & Concurrency).
- **C2 (API Specification Reflux)**: `api-spec.md` tool index updated to 26 tools. Added schemas, argument tables, response models, and error codes for `delete_meal`, `log_steps`, and `get_health_metrics`, plus the interactive web routes (`/ui`, `/ui/{form_type}`, `/api/{tool_name}`).
- **C3 (Data Model Reflux)**: `data-model.md` updated with `step_logs` table schema and documentation for SQLite production PRAGMAs (`foreign_keys=ON`, `journal_mode=WAL`, `busy_timeout=5000`, `synchronous=NORMAL`) and Peewee transaction management.
- **C4 (Rule Permanence)**: `odd/BACKLOG.md` Rule 6 formalized to mandate updating `docs/specs/openspec/` before closing any task that alters the domain specification.

## Close
> Close (filled at close)

- **Date**: 2026-11-10
- **Status**: Closed. 4/4 tasks ✅, 4/4 spec criteria ✅.
- **Artifacts**:
  - `odd/BACKLOG.md`
  - `odd/tasks/odd-merge-back.md`
  - `docs/specs/openspec/requirements.md`
  - `docs/specs/openspec/api-spec.md`
  - `docs/specs/openspec/data-model.md`
