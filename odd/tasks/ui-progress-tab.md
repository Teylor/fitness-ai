# Feature: ui-progress-tab

> Add the `📈 Progreso` navigation tab and "Coming Soon" placeholder section before the `📊 Resumen` tab in the Web UI, queuing full body measurement tracking in the backlog.

## Spec
> What and why (no technology)

- [x] C1: Add `progress` to `VALID_FORM_TYPES` and render the `📈 Progreso` tab button immediately before `📊 Resumen` in `src/ui/html_generator.py`.
- [x] C2: Render `#tab-progress` with a "Coming Soon" placeholder card describing upcoming body progress tracking (weight, waist, leg, etc.).
- [x] C3: Add `ui-body-progress-tracking` to `odd/BACKLOG.md` under `📥 Proposed` for future implementation.

## Clarify
> Resolved ambiguities

- Q: Where should the `Progreso` tab appear and what should it show initially?
  - A: Right before the `Resumen` tab, showing a "Coming Soon" placeholder for weight and body circumference measurements (waist, leg, etc.).

## Plan
> Technical decisions + classification

- Classification: **Small** — UI tab + placeholder section in `src/ui/html_generator.py` and test update in `tests/integration/test_mcp_ui_tools.py`.

## Tasks
> Implementation checklist

- [x] T1: Add `progress` tab button and `#tab-progress` "Coming Soon" section in `src/ui/html_generator.py` and update `tests/integration/test_mcp_ui_tools.py` → verify: `pytest tests/integration/test_mcp_ui_tools.py tests/integration/test_ui_web_routes.py -v` → PASSED

## Verification
> Comparison against the spec (filled in at close)

- **C1-C3**: Verified by `pytest tests/integration/test_mcp_ui_tools.py tests/integration/test_ui_web_routes.py -v` (19 passed).

## Close
> Close (filled in at close)

- **Date**: 2026-11-20
- **Implemented**: `📈 Progreso` tab ("Coming Soon") placed before `📊 Resumen`.
