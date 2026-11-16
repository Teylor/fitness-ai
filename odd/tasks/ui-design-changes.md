# ui-design-changes

> Feature: ui-design-changes

## Spec

### Context
`src/ui/html_generator.py` generates the entire web UI (single generated HTML with embedded CSS/JS) served via `/ui` with hot-reload. The current look is functional but generic. The user wants to explore several visual styles (color palette, typography, layout, component shapes, light/dark theme) before committing to a direction.

### Objective
Iterate locally on distinct UI style variants, show each one to the user, and keep the locally approved direction — without any commit or push until the user explicitly approves.

### Acceptance Criteria
- [x] C1: Each style variant is a self-contained, easily reversible change to the presentation layer only (CSS/theme tokens in `src/ui/`; no changes to data logic, endpoints, or generated-HTML structure/ids used by the JS).
- [x] C2: Every variant is tested with the app running and reviewed by the user before the next variant starts.
- [x] C3: **No `git commit` and no `git push` of any design change until the user explicitly approves.** All experimentation stays uncommitted in the working tree.
- [x] C4: Once a direction is approved, only that approved variant is committed/pushed on a `feat/ui-design-changes` branch, per backlog rule 8. (Actual feature branch: `feat/ui-redisgn`.)

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
- [x] T3: Variant 2 (readability, v2) — review — **approved, committed `09da3be` + pushed**
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
- [x] Tn: Approved direction — finalized: test suite green, committed + pushed on `feat/ui-redisgn`

## Verification
- **C1 (presentation only):** diff of `b4893b4` + `09da3be` confined to `src/ui/html_generator.py` — `:root` theme tokens, body CSS, and a few presentation strings/grid classes in the generated HTML. No data logic, endpoints, or JS ids touched. Reversible: reverting the two commits restores the prior look.
- **C2 (tested + reviewed):** Variant 1 (header, `b4893b4`) and Variant 2 (type scale, `09da3be`) each shown on the live app and approved by the user before the next step.
- **C3 (no pre-approval commits):** no design commit/push existed until the user approved; both commits landed only after approval.
- **C4 (approved variant on feature branch):** approved look committed (`b4893b4`, `09da3be`) + pushed on feature branch `feat/ui-redisgn`.
- **Test suite:** `pytest tests/ -v` → **216 passed, 0 failed.** (4 UI smoke assertions updated to match the approved design text: `"Fitness AI Hub"` → `"Hermes Hub"`; `"1RM Estimado (PR)"` → `"1RM (PR)"`; `"Récord de Peso (Max Set)"` → `"Récord"`.)

## Close
- **Closed:** 2026-11-16
- **Delivered:** two readability variants, final direction approved. Final scale 13/14/15/17/17/20/24px (floor 13px), body 17px @ line-height 1.6, headings 20/24px, `rem` pinned to 16px, mobile `--fs-scale` 0.93 below 640px. Header/brand redesigned (`b4893b4`). All tokens live in `:root` of `src/ui/html_generator.py`.
- **Note:** commit `09da3be` also carried an `.agents/skills/impeccable/` skill install + `.gitignore`/`skills-lock.json` (incidental, already pushed — not part of the UI change itself).
- **Next step:** open PR `feat/ui-redisgn` → `main` when ready to merge (per backlog rule 8). No other pending follow-up.
