# ui-design-changes

> Feature: ui-design-changes

## Spec

### Context
`src/ui/html_generator.py` generates the entire web UI (single generated HTML with embedded CSS/JS) served via `/ui` with hot-reload. The current look is functional but generic. The user wants to explore several visual styles (color palette, typography, layout, component shapes, light/dark theme) before committing to a direction.

### Objective
Iterate locally on distinct UI style variants, show each one to the user, and keep the locally approved direction — without any commit or push until the user explicitly approves.

### Acceptance Criteria
- [ ] C1: Each style variant is a self-contained, easily reversible change to the presentation layer only (CSS/theme tokens in `src/ui/`; no changes to data logic, endpoints, or generated-HTML structure/ids used by the JS).
- [ ] C2: Every variant is tested with the app running and reviewed by the user before the next variant starts.
- [ ] C3: **No `git commit` and no `git push` of any design change until the user explicitly approves.** All experimentation stays uncommitted in the working tree.
- [ ] C4: Once a direction is approved, only that approved variant is committed/pushed on a `feat/ui-design-changes` branch, per backlog rule 8.

## Clarify
- "Variant" = a coherent complete look (palette + typography + spacing/shapes + theme), not isolated tweaks.
- Prefer changing CSS custom properties/theme tokens so switching between variants is fast and the final diff stays small.
- Reversible by design: each variant is a separate logical step in the working tree; if a variant is rejected it is discarded, not kept in history.

## Plan
- **T1**: Baseline snapshot of current UI (screenshot/notes) + identify theme-token seams in `src/ui/html_generator.py`.
- **T2..**: Apply variant N → user reviews → approve next variant or direction (repeat).
- **Tn**: On approval: finalize approved style, run `pytest tests -q`, then (and only then) commit + push on `feat/ui-design-changes`.

## Tasks
- [ ] T1: Baseline + locate theme-token seams
- [ ] T2: Variant 1 — review
- [ ] T3: Variant 2 — review
- [ ] Tn: Approved direction — finalize (commit/push only after approval)

## Verification
- (to be filled)

## Close
- (to be filled)
