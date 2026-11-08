"# Skill: track-feature

> Create or update `odd/tasks/<feature>.md` before the first code write.

## When it activates
After `classify` (or `sdd-tasks` if it escalated to SDD), before `implement-task`.

## Steps

1. **Create file** `odd/tasks/<feature-name>.md` if it does not exist.
2. **Fill in the sections**:
   - `## Spec` → What and why (acceptance criteria)
   - `## Clarify` → Resolved ambiguities (Q/A)
   - `## Plan` → Technical decisions + classification
   - `## Tasks` → Checklist with per-task verification
   - `## Verification` → (empty, filled in at close)
   - `## Close` → (empty, filled in at close)
3. **Link** to `specs/<feature>/spec.md` and `plan.md` if they exist (SDD branch).
4. **Confirm** with the user: "Checklist created. Approved to implement?"

## Template

```markdown
# Feature: <name>

## Spec
> What and why (no technology)

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2

## Clarify
> Resolved ambiguities

- Q: ...? → A: ...

## Plan
> Technical decisions + classification

- Classification: <trivial|small|substantial|SDD>
- D1: ...
- D2: ...

## Tasks
> Implementation checklist

- [ ] T1: <description> → verify: <test/command>
- [ ] T2: <description> → verify: <test/command>

## Verification
> Comparison against the spec (filled in at close)

## Close
> Close (filled in at close)
```

## Rules
- **Single source of progress.** The checklist lives ONLY here.
- The spec never stores state (if it exists as a separate file).
- Do not start `implement-task` without this file.
- If the feature already exists → update it, do not create a new one.
"