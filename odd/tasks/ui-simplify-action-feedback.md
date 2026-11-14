# ui-simplify-action-feedback

> Feature: ui-simplify-action-feedback

## Spec

### Context

`executeAction()` in `src/ui/html_generator.py` ("Universal Dispatch & Result Display",
lines ~912-955) is the single client-side dispatch for every UI write action. Its success
branch (lines 929-934) renders the generic label `✅ Operación completada con éxito` and
then dumps the **entire** raw response: `<div>${JSON.stringify(data, null, 2)}</div>`.

The success `data` shape varies per endpoint (verified against `src/mcp/tools/`):
- create/update exercise → `{status, exercise}`
- create/update ingredient → `{status, ingredient}`
- create/update recipe → `{status, recipe}`
- register meal → `{status, entry_id, meal_type, macros, price, day_summary, google_health_synced}`
- register workout → `{status, ...session}`
- goal update → `{status, goal, profiles}`

So the box always shows a full pretty-printed entity/session dump (often the whole
`day_summary`), which is noisy for a success confirmation.

### Objective

Replace the bare full-JSON dump in the `executeAction()` success branch with a concise,
human-readable one-line summary derived from the response entity, while keeping the full
raw response accessible (collapsed) so no debugging info is lost, and preserving the
`return data` contract that callers rely on.

### Acceptance Criteria

- [ ] C1: The success branch shows a concise one-line summary (e.g. `Ejercicio «name» guardado`,
      `Ingrediente «name» guardado`, `Comida registrada`) instead of a bare full-JSON dump as the
      primary message.
- [ ] C2: The full raw JSON response remains available, collapsed in a `<details>` element
      (default closed) — no information lost.
- [ ] C3: `executeAction` still `return data` (callers that read the returned object keep working).
- [ ] C4: The error / fallback path (Hermes prompt copy mode) is unchanged.
- [ ] C5: Full suite green (`pytest tests -q`) and the new behavior is covered by an integration
      test asserting on the generated UI HTML/JS.

## Clarify

- Q1: Which actions go through `executeAction` and what is each success `data` shape?
  A1: All UI write actions. Entity keys present on success: `exercise` / `ingredient` /
      `recipe` / `goal` / `entry_id` (meal) / `...session` (workout). A summary helper that
      branches on which entity key is present covers all of them (evidence: `src/mcp/tools/
      {exercise,ingredient,recipe,meal,workout,goal}_tools.py`).
- Q2: How should the raw JSON stay accessible?
  A2: Wrap it in a collapsed `<details><summary>Ver respuesta completa</summary><pre>…</pre></details>`.
      Concise by default, full payload one click away (satisfies C2).
- Q3: Is the generated HTML a Python f-string (brace escaping)?
  A3: Yes. The whole page is one f-string template. Literal JS braces must be doubled
      (`{{` / `}}`), and JS `${...}` interpolations must be written `${{...}}` to survive
      f-string rendering — see the existing `${{JSON.stringify(data, null, 2)}}` on line 932.
      Forgetting this corrupts the emitted JS.
- Q4: UI-only or does it touch server logic?
  A4: UI-only (client-side JS in generated HTML). No API/service change. Verification is
      `pytest tests -q` + HTML string assertions (the repo suite has no headless browser).

## Plan

- Mode: fast (one pre-commit report at the end of the feature).
- TDD: T1 = failing integration test (RED), T2 = implementation to GREEN.
- Decisions:
  - D1: Add a `summarizeSuccess(data, payload)` helper next to `executeAction`; branch on the
    present entity key (`exercise` / `ingredient` / `recipe` / `goal` / `entry_id` / `session`),
    fallback `Operación completada con éxito`.
  - D2: Wrap the raw JSON in a collapsed `<details>` (keeps current debuggability, satisfies C2).
  - D3: Keep `return data` unchanged (C3); leave the error/fallback branch untouched (C4).
- Files: `src/ui/html_generator.py` (JS only), `tests/integration/test_ui_web_routes.py` (one test).

## Tasks

- [ ] T1: Add `test_ui_execute_action_summary(db)` to `tests/integration/test_ui_web_routes.py`:
      GET a `/ui/...` page and assert the generated JS defines `summarizeSuccess`, the success
      branch uses it, the raw JSON is wrapped in `<details>` (not a bare `<div>` dump), and
      `return data` is still present. → files: tests/integration/test_ui_web_routes.py → verify:
      `pytest tests/integration/test_ui_web_routes.py -q` RED on the new assertions vs current code.
- [ ] T2: Rewrite the `executeAction()` success branch in `src/ui/html_generator.py`: add the
      `summarizeSuccess` helper (f-string doubled braces), render `✅ ${summary}` + collapsed
      `<details>` raw JSON, keep `return data`. → files: src/ui/html_generator.py → verify: T1 test
      GREEN, then full `pytest tests -q` green.

## Verification

> (filled at close)

## Close

> (filled at close)
