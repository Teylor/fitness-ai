# Skill: odd-protocol

> Orchestrator for the ODD cycle. Enforces the order: authorize, explore, resolve uncertainty, classify, track, implement, close.

## When it activates
Always. It is the first skill invoked for any change request.

## Steps

1. **Authorize**: Confirm with the user that work will proceed on the feature.
2. **Explore** (→ `explore`): Read the actual code, tests, and relevant ADRs.
3. **Resolve uncertainty**: Ask the user about anything unclear.
4. **Classify** (→ `classify`): Decide the size (trivial/small/substantial/SDD).
5. **Track** (→ `track-feature`): Create `odd/tasks/<feature>.md`.
6. **Implement** (→ `implement-task`): Per execution mode (rule 11): fast (default) — run the whole feature in one pass, TDD, ONE pre-commit report at the end; slow — one task at a time, pre-commit report before each commit. (the user runs the commit)
7. **Close** (→ `close-feature`): Verify the criteria, update the docs, leave the next step.

## Rules
- Do not skip steps.
- Do not implement without `track-feature`.
- Do not close without verifying all acceptance criteria.
- No commit without a pre-commit report (changes, tests where applicable, suggested message) and the user's decision.
- The agent does not run `git commit` on its own.
- If `classify` escalates to SDD → invoke the SDD branch before `implement-task`.
- Execution mode (rule 11): default fast; complex features use slow; when complexity is unclear, ask the user which mode to use before implementing.
- All generated project text (docs, ODD, comments, docstrings, tests, commit messages) is written in English (ADR-002). Spanish only in the conversation with the user.
