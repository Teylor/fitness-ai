# Feature: ui-exercises-pr-set

> Feature: ui-exercises-pr-set

## Spec
> What and why (no technology)

- The Exercises tab table displays the three PR columns in this order:
  1. `1RM Estimado` — highest estimated 1RM value (`{e1rm} kg`) with its date (previously `1RM (PR)`).
  2. `Peso 1RM` — the set (`weight × reps`) that produced the highest estimated 1RM, with its date. E.g. `20 × 10` when that set yields a higher estimated 1RM than the heaviest set.
  3. `Peso Máx` — the heaviest weight ever lifted with its repetitions, with its date (previously `Récord`). E.g. `22 × 6`.
- Both records are shown side by side so the user sees them even when they come from different sets (e.g. `75 × 5` heaviest vs `70 × 12` best estimated 1RM).
- For exercises without logged weight sets (time/distance exercises), all three columns display `-`.

## Clarify
> Ambiguities and resolutions

- Q: What exactly does the new `Peso 1RM` column show?
  - A: The weight × reps of the set that produced the maximum estimated 1RM, i.e. the `estimated_1rm_weight` × `estimated_1rm_reps` already returned by `get_exercise_stats` / `list_exercises(include_prs=true)`.
- Q: Does the backend or API change?
  - A: No. `pr` already contains `estimated_1rm_weight`, `estimated_1rm_reps` and `estimated_1rm_date`. UI-only change.
- Q: Column order and naming?
  - A: User decision: `1RM Estimado` → `Peso 1RM` → `Peso Máx` (renames the old `1RM (PR)` and `Récord` headers).
- Q: Do the PR columns keep their dates?
  - A: Yes, each column shows its own date below the badge, consistent with the current behavior.

## Plan
> Technical decisions + classification

- Classification: **small** — 1 source file (UI generator) + 1 integration test + 1 spec line; no public API change, no migration. The backend already computes and exposes the set behind the max estimated 1RM.
- D1: `src/ui/html_generator.py` — table header: replace `1RM (PR)` / `Récord` with `1RM Estimado` / `Peso 1RM` / `Peso Máx` (new `<th>` in the middle).
- D2: `src/ui/html_generator.py` — `renderExercisesTable`: new `prSetHtml` rendered from `ex.pr.estimated_1rm_weight` / `estimated_1rm_reps` / `estimated_1rm_date` (badge `⚡ {w}×{r}` + date line, `-` fallback); insert the new `<td>` between the 1RM and max-weight cells.
- D3: `tests/integration/test_ui_web_routes.py` — update `test_ui_exercises_tab_and_prs_integration` header assertions to the three new column names.
- D4: `docs/specs/openspec/requirements.md` — update FR8.5 to list the three PR columns.

## Tasks
> Implementation checklist

- [ ] T1: Add `Peso 1RM` column and rename headers in `src/ui/html_generator.py` → verify: `pytest tests/integration/test_ui_web_routes.py`
- [ ] T2: Update FR8.5 in `docs/specs/openspec/requirements.md` → verify: grep FR8.5
- [ ] T3: Run full test suite → verify: `pytest`

## Verification
> Comparison against the spec (filled in at close)

## Close
> Close (filled in at close)
