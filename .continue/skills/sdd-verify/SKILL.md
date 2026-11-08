"# Skill: sdd-verify

> Compare code against the spec. Optional, diagnostic, does not block the close.

## When it activates
Optional, after `close-feature`. Useful when an extra verification is wanted before archiving.

## Steps

1. **Read** `specs/<feature>/spec.md` (acceptance criteria).
2. **For each criterion**:
   - Find the corresponding implementation in the code.
   - Run the associated test.
   - Verify that the actual behavior matches the spec.
3. **Report**:
   ```
   | Criterion | Status | Evidence |
   |----------|--------|-----------|
   | CA1 | ✅ | test_x.py::test_y PASSED |
   | CA2 | ✅ | Comando: `python -m src.main` → OK |
   | CA3 | ⚠️ | Partial: edge case Z missing |
   ```
4. **If there are discrepancies**:
   - Do not block the close.
   - Document it in the `## Verification` section of `odd/tasks/<feature>.md`.
   - Create a new feature for the fix if necessary.

## Rules
- **Does not block.** It is diagnostic, not a gate.
- If the code does not match the spec → document it, do not fix it here.
- If the spec is wrong (it describes something that was not wanted) → edit the spec, not the code.
- The result is stored in the ODD document, not in the spec.
"