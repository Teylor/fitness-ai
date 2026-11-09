# SDD + ODD Workflow

> Mandatory process for any change in the project. The agent enforces this order.

## Principle

> **No implementation without a spec.** Before touching code, specs are reviewed and updated.
> Once approved by the user, implementation begins.

---

## Phase 0 — BACKLOG (Entry Gate)

> Before SPECIFY, the work must exist as an item in `odd/BACKLOG.md` (📥 Proposed → ✅ Approved).
> When starting a feature, the item moves to ➡️ In Progress. When closing it, to 🏁 Done.
> The backlog is the single work queue: nothing starts without being approved there.

---

## Complete Lifecycle

```
User Request
       │
       ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 1. SPECIFY                                                          │
│    Describe the feature: WHAT and WHY (technology-agnostic).        │
│    Clear acceptance criteria.                                       │
│    → odd/tasks/<feature>.md ("Spec" section)                        │
└───────────────────────────────┬─────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. CLARIFY                                                          │
│    The agent lists ambiguities, assumptions, and questions.         │
│    Resolve ALL of them before continuing.                           │
│    → odd/tasks/<feature>.md ("Clarify" section)                     │
└───────────────────────────────┬─────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 3. PLAN                                                             │
│    Technical decisions aligned with the constitution (ADRs).        │
│    Architecture, dependencies, risks.                               │
│    → odd/tasks/<feature>.md ("Plan" section)                        │
│    → docs/architecture/ssd-decisions.md (if a new ADR is required)  │
└───────────────────────────────┬─────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 4. TASKS                                                            │
│    List of small tasks, each with:                                  │
│      - Description                                                  │
│      - Verification (test, command, or manual inspection)           │
│      - Status: [ ] → [~] → [x]                                      │
│    → odd/tasks/<feature>.md ("Tasks" section)                       │
└───────────────────────────────┬─────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 5. IMPLEMENT                                                        │
│    One task at a time. TDD if configured.                           │
│    Pre-commit report; user commit per task.                         │
│    → src/ (code)                                                    │
│    → odd/tasks/<feature>.md (mark [x] + evidence)                   │
└───────────────────────────────┬─────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 6. REVIEW / VERIFY                                                  │
│    Check outcome against spec (not against "it seems to work").     │
│    Every acceptance criterion → verified.                           │
│    → odd/tasks/<feature>.md ("Verification" section)                │
└───────────────────────────────┬─────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 7. CLOSE                                                            │
│    Close acceptance criteria & update docs.                         │
│    Final commit & push branch to origin.                            │
│    Create Pull Request to main directly.                            │
│    → odd/tasks/<feature>.md ("Close" section)                       │
│    → Pull Request: feat/<name> → main                               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Escalation to SDD (Full Branch)

Not every feature requires the full lifecycle. `classify` decides:

| Size | Criteria | Path |
|------|----------|------|
| **Trivial** | 1 file, typo fix, rename, config | Direct implementation (no spec) |
| **Small** | 1-2 files, 1 module, no public API | Minimal spec + tasks + implementation |
| **Substantial** | Multiple modules, new entity, new MCP tool | Full spec + clarify + plan + tasks + implement + verify |
| **Requires SDD** | Changes public contract/API, data migration, security, hard to roll back, multiple parallel agents | Full SDD (separate `spec.md` + `plan.md`) |

### SDD Escalation Criteria (Any of the following):
- Changes a public contract or API (MCP tool)
- Touches multiple modules simultaneously
- Requirements are ambiguous or have multiple interpretations
- Affects security or data migration
- Is hard to roll back
- Multiple agents will work in parallel

---

## File Structure per Feature

```
odd/
├── BACKLOG.md                     # Single work queue (Proposed → Approved → In Progress → Done)
└── tasks/
    └── <feature-name>.md          # Single checklist (source of truth)

specs/
└── <feature-name>/
    ├── spec.md                   # (SDD only) What and why
    └── plan.md                   # (SDD only) Technical decisions
```

### Template: `odd/tasks/<feature>.md`

```markdown
# Feature: <name>

## Spec
> What and why (technology-agnostic)

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2

## Clarify
> Resolved ambiguities

- Q: ...? → A: ...

## Plan
> Technical decisions

- D1: ...
- D2: ...

## Tasks
> Implementation checklist

- [ ] T1: <description> → verify: <test/command>
- [ ] T2: <description> → verify: <test/command>

## Verification
> Spec compliance verification

- [x] Criterion 1: ✅ <evidence>
- [x] Criterion 2: ✅ <evidence>

## Close
> Closure

- Date: ...
- Next step: ...
```

---

## Integration Rules

1. **Single source of truth for progress.** The checklist lives exclusively in `odd/tasks/<feature>.md`. The spec never tracks state.
2. **Escalation criteria.** If `classify` yields "requires SDD" → separate `specs/<feature>/spec.md` and `plan.md` files are created.
3. **Modifications to an existing spec.** Edit `spec.md` first, regenerate `plan.md`, and reopen affected tasks in the ODD document with a stated reason.
4. **Mid-flight escalation.** If unexpected complexity emerges during `implement-task`, stop, reclassify, and switch to the SDD path without discarding completed work.
5. **Implementation-only changes.** Do not modify the spec.
6. **User approval.** The user must approve spec + plan + tasks before `implement`.
7. **Backlog as single queue.** The agent checks `odd/BACKLOG.md` before starting, updates the item's status at kickoff (➡️ In Progress), and marks it complete on finish (🏁 Done). No feature starts without an approved item.
8. **Branching and Pull Requests.** Each feature is developed on its own branch `feat/<feature-name>`, created when the feature starts. A fix to a feature is made on a `fix/<feature-name>` branch. When a feature closes (all tasks verified, final commit made), the branch is pushed to origin and a Pull Request to `main` is created directly.
9. **Pre-commit gate.** Before every commit (task, closure, or archival), the agent presents the pre-commit report (changes made, relevant tests, suggested message) and stops: the user commits, requests changes, or instructs to continue. The agent never runs `git commit` autonomously.
10. **Language (ADR-002).** All generated project text is written in English: docs, specs, ODD, ADRs, READMEs, code comments/docstrings, test docstrings/assertion messages, SQL/script comments, and commit messages. Spanish is used only in the conversation with the user. Accented normalization fixtures (`Ñandú`, `Café`) are the documented exception.
11. **Execution modes (fast/slow).** Every feature runs in one of two modes, decided after `classify` (default: fast). **Fast**: feature by feature, not task by task — run all tasks in the feature in a single pass (each task is still verified: tests pass, marked `[x]` with evidence), then present ONE pre-commit report covering the entire feature and propose a single commit. **Slow**: task by task within the feature — the pre-commit gate (rule 9) applies per task. Simple features use fast, complex features use slow; when complexity is ambiguous, ask the user which mode to use before implementing.

---

## Core ODD Skills (Always Active)

| Skill | Description |
|-------|-------------|
| `odd-protocol` | Orchestrator. Enforces the execution order: consult BACKLOG, authorize, explore, resolve uncertainty, classify, track, implement, close. |
| `explore` | Inspects live code, tests, and relevant ADRs before proposing any plan. |
| `classify` | Determines the size: trivial, small, substantial, or requires spec. |
| `track-feature` | Creates or updates `odd/tasks/<feature>.md` prior to the first write operation. |
| `implement-task` | One task at a time, using TDD if configured, generating a pre-commit report before each commit, and recording progress and evidence. |
| `close-feature` | Closes acceptance criteria, updates the task doc, sets the next step, produces the final pre-commit report, marks 🏁 Done in `odd/BACKLOG.md`, pushes the branch, and creates the Pull Request to `main`. |

## SDD Branch Skills (Only Active when Escalated by Classify)

| Skill | Description |
|-------|-------------|
| `sdd-specify` | Writes `specs/<feature>/spec.md`: what and why, technology-agnostic. |
| `sdd-clarify` | Identifies ambiguities and resolves them before proceeding. |
| `sdd-plan` | Writes `plan.md`: architecture, design decisions, and risks, aligned with project constraints. |
| `sdd-tasks` | Translates the plan into a checklist directly inside the ODD document, rather than an isolated tasks.md. |
| `sdd-verify` | Compares code against spec. Optional diagnostic step; does not block closure. |
| `sdd-archive` | Upon closing, marks the spec as implemented and archives it to historical records. |

---

## Workflow Connection

```
Request → odd-protocol (check BACKLOG) → explore → classify
                                 │
                                 ├─ trivial/small ────────────→ track-feature → implement-task → close
                                 │
                                 └─ requires spec → sdd-specify → sdd-clarify → sdd-plan → sdd-tasks
                                                                                 │
                                                                                 ▼
                                                               track-feature (links spec & plan)
                                                                                 │
                                                                                 ▼
                                                               implement-task → close
                                                                                 │
                                                                                 ▼
                                                               sdd-verify (optional) → sdd-archive
```

---

## Test Planning

| Version | Scope | Tooling |
|---------|-------|---------|
| **v0** | Unit tests per service (CRUDs, macro calculations, PR) + MCP integration tests (invoke tool → verify JSON) | `pytest` + `pytest-asyncio` |
| **v1** | E2E tests: simulate complete flow Hermes → MCP → DB → response | `pytest` + temporary DB fixture |

### Test Structure (v0)

```
tests/
├── __init__.py
├── conftest.py              # Fixtures: temporary DB, services, MCP client
├── unit/
│   ├── test_ingredient_service.py
│   ├── test_recipe_service.py
│   ├── test_meal_service.py
│   ├── test_goal_service.py
│   ├── test_exercise_service.py
│   ├── test_workout_service.py
│   ├── test_macros_utils.py
│   └── test_fuzzy_utils.py
└── integration/
    ├── test_mcp_meal_tools.py
    ├── test_mcp_ingredient_tools.py
    ├── test_mcp_recipe_tools.py
    ├── test_mcp_goal_tools.py
    ├── test_mcp_workout_tools.py
    └── test_mcp_exercise_tools.py
```

### TDD Rule in `implement-task`

1. **Before** implementing a task → write the test (red).
2. **Implement** the task (green).
3. **Refactor** if necessary.
4. **Pre-commit report** (mandatory before any commit):
   - **Changes made**: modified files and exact changes made to each.
   - **Tests (if applicable)**: tests covering the changes (new and existing) and their execution status; state explicitly if not applicable.
   - **Suggested commit message**: `feat(<module>): <task> [T#]`
5. **Await user decision** (see "Pre-commit report" below).
6. Mark `[x]` in `odd/tasks/<feature>.md` with test evidence: `pytest tests/unit/test_x.py::test_y -v` → PASSED.

### Pre-commit Report (Gate Before Each Commit)

> The agent does not execute `git commit` autonomously nor advance to the next task without user confirmation.

Report format:

1. **Changes made**: modified files and specific changes in each, along with the rationale.
2. **Tests (if applicable)**: tests verifying the changes (new and existing) and outcomes. If no tests apply, state explicitly.
3. **Suggested commit message**: `feat(<module>): <task> [T#]` (`docs(...)` / `refactor(...)` / `chore:` depending on change type).

After presenting the report, the agent pauses for the user's action:

| User Decision | Agent Action |
|---------------|--------------|
| Commit changes (directly or by instructing the agent) | Mark `[x]` with evidence → advance to next task. |
| Request revisions | Set task to `[~]`, apply changes, re-verify tests, and resubmit report. |
| "Continue to next task" | Mark `[x]` with evidence → advance to next task (committing deferred to user). |