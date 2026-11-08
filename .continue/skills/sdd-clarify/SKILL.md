"# Skill: sdd-clarify

> List the ambiguities and resolve them before moving on.

## When it activates
After `sdd-specify`, before `sdd-plan`.

## Steps

1. **Read** `specs/<feature>/spec.md`.
2. **List** all the ambiguities, unspoken assumptions, unanswered questions:
   - What happens if...?
   - What if the user...?
   - What exactly does ... mean?
   - Is there any undocumented limit or constraint?
3. **Present** to the user in Q/A format:
   ```
   Q1: ...? → A: (pending)
   Q2: ...? → A: (pending)
   ```
4. **Resolve** each one with the user.
5. **Update** the `## Clarify` section of `odd/tasks/<feature>.md` with the answers.
6. **If an answer changes the spec** → update `spec.md` first.

## Rules
- Do not move to `sdd-plan` with unresolved ambiguities.
- If the user says "I don't know" → propose an option and record it as an assumption.
- At most 2 clarify rounds. If there are more than 5 questions → the spec is poorly written, go back to `sdd-specify`.
"