# Skill: classify

> Decide the size of the change: trivial, small, substantial, or requires SDD.

## When it activates
After `explore`, before `track-feature`.

## Criteria

| Size | Criteria | Action |
|--------|-----------|--------|
| **Trivial** | 1 file, typo, rename, config, comment | → `track-feature` (minimal) → `implement-task` → `close` |
| **Small** | 1-2 files, 1 module, no public API, no migration | → `track-feature` → `implement-task` → `close` |
| **Substantial** | Several modules, new entity, new MCP tool, new table | → `track-feature` (with inline spec) → `implement-task` → `close` |
| **Requires SDD** | Changes public contract/API, data migration, security, hard to revert, multiple agents in parallel, ambiguous requirements | → `sdd-specify` → `sdd-clarify` → `sdd-plan` → `sdd-tasks` → `track-feature` → `implement-task` → `close` |

## Escalation criteria to SDD (any of these):
- Changes a public contract or API (MCP tool)
- Touches several modules at the same time
- The requirements are ambiguous or admit multiple interpretations
- Affects security or data migration
- Hard to revert
- Multiple agents will work in parallel

## Output
- Decision documented in `odd/tasks/<feature>.md` (section "Plan" → "Classification").
- If it escalates to SDD → invoke `sdd-specify`.

## Rules
- When in doubt, escalate a level.
- If unexpected complexity appears during `implement-task` → reclassify and escalate.
- Record the reason for the classification.