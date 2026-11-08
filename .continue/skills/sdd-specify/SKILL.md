"# Skill: sdd-specify

> Write `specs/<feature>/spec.md`: what and why, no technologies.

## When it activates
When `classify` escalates to SDD.

## Steps

1. **Create** `specs/<feature-name>/spec.md`.
2. **Write**:
   - **Problem**: What problem does it solve?
   - **Context**: Why now? What limits the current solution?
   - **Acceptance criteria**: Checkable list (no technology).
   - **Non-requirements**: What will NOT be done (to avoid scope creep).
   - **Assumptions**: What is taken for granted.
3. **Do not include**: technologies, frameworks, file structure, specific APIs.
4. **Confirm** with the user: "Spec written. Approved?"

## Template

```markdown
# Spec: <feature name>

## Problem
> What problem it solves (no technology)

## Context
> Why now, what limits the current solution

## Acceptance criteria
- [ ] CA1: ...
- [ ] CA2: ...

## Non-requirements
- X will not be done
- Y will not be done

## Assumptions
- A1: ...
- A2: ...
```

## Rules
- No technology. If you mention "SQLite" or "Peewee" → wrong.
- The spec is immutable once approved (changes → edit the spec → regenerate the plan).
- The spec NEVER stores progress state.
"