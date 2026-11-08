# Feature: translate-to-english

> Migrate all project text to English (docs, ODD, code comments/docstrings, tests, SQL and scripts). No behavior change.

## Spec
> What and why (no technology)

- [ ] C1: All Markdown docs are in English (root README, `docs/**`, `specs/`, `config/`, `odd/**`).
- [ ] C2: All Python docstrings and comments in `src/**` are in English.
- [ ] C3: All SQL comments are in English.
- [ ] C4: All test docstrings, comments, and assertion messages are in English; sample test data is English except the accent/normalization fixtures.
- [ ] C5: Shell script (`.bat`) comments and `echo` strings are in English.
- [ ] C6: The decision "project language is English" is recorded in `docs/architecture/ssd-decisions.md` (ADR-002).
- [ ] C7: A final sweep finds no residual Spanish (except the documented accent fixtures) and the full test suite passes.

## Clarify
> Ambiguities resolved

- Q: Does "everything in English" include code identifiers? → A: No. Identifiers, imports, syntax, and technical terms already follow Python/SQL conventions and stay. Only human-readable text (docstrings, comments, assertion messages, docs, test descriptions) is translated.
- Q: What about sample test data values (e.g. `"Pan"` = bread)? → A: Translate sample data names to English for consistency.
- Q: What about the accent fixtures in `tests/unit/test_fuzzy_utils.py` (`normalize("Ñandú")`, `normalize("Café")`)? → A: Preserve those input strings — they are the point of the tests (proving accent-stripping). They are the documented exception to C4.
- Q: Word-for-word or meaning-preserving? → A: Meaning-preserving, natural English. Preserve markdown structure, headings, tables, code blocks, links, and ODD conventions (rule numbers, states, ADR format).
- Q: Are the ODD files (`odd/BACKLOG.md`, `odd/tasks/*`) in scope? → A: Yes, they are project text.
- Q: Is the new ADR written in Spanish or English? → A: English (forward-looking decision; the file is migrated in the same pass).

## Plan
> Technical decisions + classification

- **Classification**: Substantial (broad — every doc + all source/test comments; translation-only, so low risk).
- D1: Scope = human-readable text only. Identifiers, syntax, and technical terms untouched.
- D2: Preserve markdown/code structure exactly; translate prose only. Keep code blocks, imports, function names, and (non-sample) data values unchanged.
- D3: Exception list — preserve accented test fixtures that validate normalization: `normalize("Ñandú")` and `normalize("Café")` in `tests/unit/test_fuzzy_utils.py`.
- D4: Order (review-friendly, low → high risk): ODD → READMEs → architecture → design → specs → skills → source → SQL/scripts → tests → final sweep.
- D5: Verification — per task: residual-Spanish check in the touched area; at the end: repo-wide accent/Spanish sweep (expect only D3 fixtures) + full `pytest tests -q` (unit + integration) green.
- D6: Commits — markdown → `docs(<scope>): ...`; source/tests → `refactor(<scope>): translate to English`; SQL/scripts → `chore: translate <area> to English`. One commit per task.

## Tasks
> Implementation checklist

- [x] T1: Record ADR-002 (English) + create this feature file + move `translate-to-english` to En curso and update execution order → files: docs/architecture/ssd-decisions.md, odd/BACKLOG.md, odd/tasks/translate-to-english.md → verify: `git diff --stat` shows the 3 files; `ADR-002` present in `ssd-decisions.md`.
- [x] T2: Translate ODD files to English → files: odd/BACKLOG.md, odd/tasks/README.md, odd/tasks/db-layer.md, odd/tasks/utils-core.md → verify: residual-Spanish check on `odd/**` → 0 accented chars.
- [x] T3: Translate README group → files: README.md, config/README.md, specs/README.md, src/README.md, docs/architecture/README.md, docs/design/README.md, docs/specs/README.md → verify: residual-Spanish check on each → 0.
- [x] T4: Translate architecture docs → files: docs/architecture/ssd-overview.md, ssd-components.md, ssd-decisions.md → verify: residual-Spanish check → 0.
- [ ] T5: Translate design docs → files: docs/design/odd-workflow.md, odd-models.md, odd-interactions.md → verify: residual-Spanish check → 0.
- [ ] T6: Translate spec docs → files: docs/specs/openspec/api-spec.md, data-model.md, requirements.md → verify: residual-Spanish check → 0.
- [ ] T7: Translate `.continue/skills/*` (12 SKILL.md) → verify: residual-Spanish check on `.continue/skills/**` → 0.
- [ ] T8: Translate Python source docstrings & comments → files: src/**/*.py → verify: `pytest tests -q` green (no behavior change); residual-Spanish check on `src/**` → 0.
- [ ] T9: Translate SQL comment + `.bat` scripts (and fix `start.bat` "stopped" → "started") → files: src/db/migrations/001_initial.sql, start.bat, stop.bat → verify: residual-Spanish check → 0.
- [ ] T10: Translate tests (docstrings, comments, assertion messages, sample data; keep D3 fixtures) → files: tests/**/*.py → verify: `pytest tests -q` green; residual-Spanish check → only D3 fixtures.
- [ ] T11: Final sweep + close → repo-wide accent/Spanish sweep (expect only D3 fixtures); `pytest tests -q` green; fill Verification + Close; move to Finalizados.

## Verification
> Spec contrast (filled at close)

## Close
> Close (filled at close)
