---
name: close-feature
description: >-
  Close out acceptance criteria, update documentation and odd/tasks/<feature>.md,
  and prepare the final pre-commit report. Use when all tasks in the checklist are [x].
---

# Skill: close-feature

> Close out the acceptance criteria, update the document, and leave the next step.

## When it activates
When all tasks in the checklist are `[x]`.

## Steps

1. **Verify** that all tasks are `[x]` in `odd/tasks/<feature>.md`.
2. **Fill in the Verification section**:
   - For each acceptance criterion in the spec → evidence that it is met.
   - Run the full test suite: `pytest tests/ -v`
3. **Update docs** if needed:
   - `docs/design/odd-models.md` (if an entity was added)
   - `docs/specs/openspec/api-spec.md` (if an MCP tool was added)
   - `docs/specs/openspec/data-model.md` (if a table was added)
   - `docs/architecture/ssd-decisions.md` (if there is a new ADR)
4. **Fill in the Close section**:
   - Close date.
   - Summary of what was implemented.
   - "Next step" if there is pending follow-up.
5. **Final pre-commit report**: summary of what was implemented, result of `pytest tests/ -v`, and the suggested message `feat(<module>): close <feature> [all tasks done]`. The user runs the commit (or the agent if explicitly asked).

## Rules
- Do not close without verifying ALL acceptance criteria.
- If something is missing → do not close, add a task to the checklist.
- If there is follow-up → document it in "Next step", do not block the close.
