"# Skill: implement-task

> One task at a time, with TDD if configured, marking progress and evidence.

## When it activates
After `track-feature` (checklist approved by the user).

## Execution modes (rule 11, odd-workflow)

- **Slow (task-by-task):** the steps below apply as written — one task at a time, pre-commit report and proposed commit per task.
- **Fast (feature-by-feature, default):** run every task of the feature in one pass without per-task stops. Each task is still verified (tests pass) and marked `[x]` with evidence. When the feature is done, present ONE pre-commit report covering all its changes and propose a single commit.

## Steps

1. **Select** the first `[ ]` task in the checklist in `odd/tasks/<feature>.md`.
2. **TDD** (if configured):
   a. Write the test first (red).
   b. Run it → it must fail.
3. **Implement** the task.
4. **Verify**:
   - Run the test → it must pass (green).
   - Run the verification command specified in the task.
5. **Pre-commit report** (mandatory, before any commit):
   a. **Changes made**: affected files and what was modified in each, with the why.
   b. **Tests (if applicable)**: which tests cover the changes (new and existing) and their result. If there are no applicable tests → state that explicitly.
   c. **Suggested commit message**: `feat(<module>): <description> [T#]`
6. **Wait for the user's decision** (do not advance on your own):
   - The user commits (or asks the agent to do so with the agreed message) → **Mark** in `odd/tasks/<feature>.md`:
     - `[x] T#: <description> → verify: <evidence: pytest output, command, etc.>`
   - The user asks for changes → leave the task as `[~]`, apply them, re-verify the tests, and repeat the report.
   - The user says "continue to the next task" → **Mark** `[x]` with evidence (the commit is at the user's discretion).
7. **Repeat** with the next task (only after the user's decision; slow mode).

## Rules
- **One task at a time.** Do not group (slow mode; see Execution modes).
- If a task requires more than expected → stop, reclassify (→ `classify`).
- If a test fails → do not move on to the next until it is fixed.
- If unexpected complexity appears → escalate to SDD (→ `sdd-specify`).
- Evidence is mandatory: without evidence, the task is not done.
- Commit per task (no grouped commits) in slow mode; one proposed commit per feature in fast mode. The user runs the commit after the pre-commit report.
- The agent does not run `git commit` on its own.
- Do not advance to the next task without the user's decision after the report (slow mode; in fast mode advance after verifying the task).
- All new code text (docstrings, comments, test descriptions/assertion messages) is written in English (ADR-002).

## Evidence format

```
- [x] T3: Implement calc_recipe_macros → verify: pytest tests/unit/test_macros_utils.py::test_calc_recipe -v → PASSED (3 tests)
```
"