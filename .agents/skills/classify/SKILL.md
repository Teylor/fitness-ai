---
name: classify
description: >-
  Decide the size of the change: trivial, small, or substantial.
  Use after explore and before track-feature.
---

# Skill: classify

> Decide the size of the change: trivial, small, or substantial.

## When it activates
After `explore`, before `track-feature`.

## Criteria

| Size | Criteria | Action |
|--------|-----------|--------|
| **Trivial** | 1 file, typo, rename, config, comment | → `track-feature` (minimal) → `implement-task` → `close-feature` |
| **Small** | 1-2 files, 1 module, no public API, no migration | → `track-feature` → `implement-task` → `close-feature` |
| **Substantial** | Several modules, new entity, new MCP tool, new table, public contract/API change, data migration, security, or ambiguous requirements | → `track-feature` (with full inline Spec, Clarify, and Plan) → `implement-task` → `close-feature` |

## Output
- Decision documented in `odd/tasks/<feature>.md` (section "Plan" → "Classification").

## Rules
- When in doubt, escalate a level.
- If unexpected complexity appears during `implement-task` → reclassify and update the inline spec and plan in `odd/tasks/<feature>.md`.
- Record the reason for the classification.
