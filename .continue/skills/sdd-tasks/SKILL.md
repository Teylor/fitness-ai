"# Skill: sdd-tasks

> Turn the plan into a checklist inside the ODD document, not a separate tasks.md.

## When it activates
After `sdd-plan` (plan approved by the user).

## Steps

1. **Read** `specs/<feature>/plan.md` and `specs/<feature>/spec.md`.
2. **Break down** the plan into small tasks (each < 30 min of work).
3. **For each task** define:
   - Clear description (what to do).
   - Affected file(s).
   - Verification: specific test, command, or manual inspection.
   - Dependencies: which tasks must be done first.
4. **Write** in the `## Tasks` section of `odd/tasks/<feature>.md`:
   ```
   - [ ] T1: <description> → files: <paths> → verify: <test/command>
   - [ ] T2: <description> → files: <paths> → verify: <test/command>
   ```
5. **Link** in the ODD document:
   ```
   > Spec: [specs/<feature>/spec.md](../../specs/<feature>/spec.md)
   > Plan: [specs/<feature>/plan.md](../../specs/<feature>/plan.md)
   ```
6. **Confirm** with the user: "Checklist of N tasks created. Approved to implement?"

## Rules
- **Do not create a separate tasks.md.** The checklist lives in `odd/tasks/<feature>.md`.
- Each task must be independent (or declare an explicit dependency).
- Each task must have verification. No verification → not a valid task.
- Order tasks by dependency (what is used first goes first).
- If a task is > 30 min → break it down further.
- Include a final task: "Run the full test suite" → verify: `pytest tests/ -v`
"