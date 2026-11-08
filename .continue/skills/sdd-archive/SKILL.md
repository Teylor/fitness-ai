"# Skill: sdd-archive

> At close, mark the spec as implemented and move it to its archive.

## When it activates
After `close-feature` (and optionally `sdd-verify`), SDD branch only.

## Steps

1. **Mark** in `specs/<feature>/spec.md`:
   ```markdown
   > **Status**: ✅ Implemented (<date>)
   > **Feature doc**: [odd/tasks/<feature>.md](../../odd/tasks/<feature>.md)
   ```
2. **Move** to the archive:
   ```
   specs/<feature>/  →  specs/_archive/<feature>/
   ```
3. **Update** the `## Close` section of `odd/tasks/<feature>.md`:
   - "Spec archived in `specs/_archive/<feature>/`"
4. **Pre-commit report**: what was moved/marked (spec → `specs/_archive/<feature>/`) and the suggested message `chore: archive spec <feature>`. The user runs the commit (or the agent if explicitly asked).

## Rules
- Only archive if `close-feature` is complete.
- An archived spec is immutable (no further edits).
- If it needs to be reopened → create a new feature (do not reopen the archived one).
- The file `odd/tasks/<feature>.md` is NOT moved (it is the progress history).
"