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
- [x] T1: Baseline + locate theme-token seams
  - Baseline: working tree was clean at `main` `0cfbbd1`; snapshot of live `/ui` saved outside repo (`/tmp/tmp.k81ETbMkSA/ui-baseline.html`).
  - Seam: all typography now controlled by CSS tokens in `:root` (`--font-body`, `--fs-xs..--fs-2xl`, `--leading-body`) in `src/ui/html_generator.py`; every `font-size` in CSS and inline styles references those tokens (70 usages). Switching variants = editing the token block only.
- [x] T2: Variant 1 — review — **applied, committed `b4893b4` (header) + pushed**
  - Focus (user request): text/font readability only.
  - Changes: type scale floor raised (nothing below 12.5px; was 10.4px), scale 12.5/13/14/15/16/18/22px; body 16px + line-height 1.5 (was browser default ~1.2); tables 15px + line-height 1.4; `tabular-nums` on tables and macro values (aligned digits); font-smoothing + text-rendering; system font stack kept (offline PWA, no web fonts).
- [ ] T3: Variant 2 (readability, v2) — review — **applied, uncommitted, awaiting user review**
  - Focus (user request, 2026-11-16): "la fuente, letra pequeña y difícil de ver" — push the type scale up another step and improve body rhythm.
  - Changes (presentation-only, tokens in `:root` of `src/ui/html_generator.py`):
    - Floor 12.5px → **13px** (`--fs-xs`); nothing renders below 13px.
    - Scale: 13 / 14 / 15 / 17 / 17 / 20 / 24px (`--fs-xs`→`--fs-2xl`).
    - `--fs-lg` (tables, tabs, list items) 15px → **17px** — the most-read content jumps a step.
    - `--fs-base` (inputs, buttons, body) 16px → **17px**.
    - Headings 18/22 → **20/24px**.
    - `--leading-body` 1.5 → **1.6** (more breathing room between lines).
    - Added `-moz-osx-font-smoothing: grayscale` + `font-feature-settings: "kern" 1` on body.
  - System font stack kept (offline PWA, no web fonts). Reversible: tokens only.
- [ ] Tn: Approved direction — finalize (commit/push only after approval)

## Verification
- (to be filled)

## Close
- (to be filled)
