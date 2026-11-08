"# Skill: sdd-plan

> Write `specs/<feature>/plan.md`: architecture, decisions, and risks, aligned with the constitution.

## When it activates
After `sdd-clarify` (all ambiguities resolved).

## Steps

1. **Create** `specs/<feature>/plan.md`.
2. **Write**:
   - **Architecture**: Affected components, new ones, interactions.
   - **Technical decisions**: Which libraries, patterns, structure.
   - **New ADRs**: If there are decisions that affect the whole project → record them in `docs/architecture/ssd-decisions.md`.
   - **Risks**: What can go wrong and the mitigation.
   - **Dependencies**: What must exist first, what blocks what.
   - **Migrations**: If there are DB changes → SQL script / Peewee migration.
3. **Align** with existing ADRs (do not contradict without justification).
4. **Confirm** with the user: "Plan written. Approved?"

## Template

```markdown
# Plan: <feature name>

## Architecture
> Affected and new components

## Technical decisions
- D1: ...
- D2: ...

## New ADRs
- ADR-XXX: ... (or "None")

## Risks
| Risk | Impact | Mitigation |
|--------|---------|-----------|
| ... | ... | ... |

## Dependencies
- Must exist first: ...
- Blocks: ...

## Migrations
- [ ] 00X_<name>.sql
- [ ] peewee-migrate create <name>

## Alignment with existing ADRs
- ADR-001: ✅ Compatible
- ADR-003: ⚠️ Affected (explain)
```

## Rules
- Do not contradict existing ADRs without creating a new ADR that supersedes them.
- If the plan requires changing an existing MCP tool → notify (it changes the public contract).
- The plan is immutable once approved (changes → edit → re-plan affected tasks).
"