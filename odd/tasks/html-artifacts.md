# html-artifacts

> Feature: html-artifacts

## Spec
> WHAT and WHY (no technology)

### Context

- The fitness AI system exposes 18 MCP tools powering Hermes Agent interactions.
- While voice and text commands are convenient for quick questions, entering complex, multi-field fitness data (such as a 3-exercise workout with 10 sets of varying weights and reps, or building a compound recipe with multiple ingredients and portions) can be tedious and error-prone in pure chat.
- The Hermes GUI can render interactive HTML artifacts directly inside the conversation pane or side-by-side view.
- Backlog item #11 specifies: "HTML artifacts rendered in the Hermes GUI to easily add ingredients, recipes, meals and workouts."

### Objective

Design and build interactive, self-contained HTML artifacts (responsive, zero-dependency, modern UI) tailored for the Hermes GUI. Users can interactively configure ingredients, compose recipes with live macro previews, record meals against daily goals, and log multi-set workouts. The artifacts will be accessible via MCP (e.g. MCP tools/resources) and/or a local web route, providing both direct API submission and fallback to agent prompt generation.

### Acceptance criteria

- [x] C1: Interactive HTML artifact for **Ingredient Management**: Form to input name, unit (`gr`, `ml`, `u`), calories, protein, carbs, fat, price per base unit, and provisional flag, with live validation.
- [x] C2: Interactive HTML artifact for **Recipe Builder**: Dynamic ingredient list builder with searchable catalog, quantity inputs, and instant live recalculation of total recipe macros (kcal, protein, carbs, fat) and cost.
- [x] C3: Interactive HTML artifact for **Meal Logger**: Date picker (default today), item selector (ingredient vs recipe), portion size, and real-time visual progress bars against daily goals.
- [x] C4: Interactive HTML artifact for **Workout Logger**: Date/time input, notes, dynamic table to add/remove exercises and sets (set number, reps, weight, duration), with live estimated 1RM computation (Epley formula).
- [x] C5: Unified Dashboard / Hub view: A cohesive single-page app or tabbed artifact allowing switching between all 4 entry types and viewing today's summary.
- [x] C6: Hermes & MCP Integration: Expose the artifacts through an MCP tool (e.g. `get_html_artifact` / `render_form`) and local HTTP routes (`/ui/...`) so Hermes can either embed the raw HTML or link to it.
- [x] C7: Mobile-friendly & standalone: Self-contained (clean embedded CSS, no build tool / npm requirement), responsive for mobile screens, supports dark mode, and handles data submission (direct fetch or copy-as-tool-call/prompt).

## Clarify
> Ambiguities and resolutions (filled interactively with the user)

- **Q1. How should Hermes deliver and render the artifacts?** A: Dual delivery: A dedicated MCP tool `get_ui_form(form_type: Optional[str] = "hub")` returning the raw HTML string to embed as an artifact directly in the Hermes chat UI, plus local HTTP routes `/ui` and `/ui/{form_type}` hosted directly on the Starlette server.
- **Q2. How should submitted data flow back into the system?** A: Hybrid submission: The HTML form performs a direct `fetch()` to the server's `/api/{tool_name}` endpoints for immediate submission and on-screen confirmation, with a "Copy prompt for Hermes" fallback button generating formatted text/JSON in case the webview is sandboxed.
- **Q3. Layout format?** A: Unified interactive Hub (`hub`) with tabs for Meals, Recipes, Ingredients, Workouts, and Summary, supporting focused single-purpose views (`meal`, `recipe`, `ingredient`, `workout`, `summary`).
- **Q4. Styling and technology stack?** A: Self-contained zero-dependency HTML5 with embedded CSS (responsive mobile-first layout, modern dark theme with emerald/cyan fitness accents) and vanilla JavaScript. No build step or external npm packages required.

## Plan
> Implementation plan (filled after clarify)

- **Mode:** fast — modular UI generator, clean Starlette routes, full unit, integration, and E2E test coverage.
- **T1 — Clarification & Design:** (Completed) User alignment on dual delivery, hybrid submission, and unified hub.
- **T2 — UI Generator Module (`src/ui/html_generator.py`):** Standalone HTML generator supporting all 5 views (`hub`, `ingredient`, `recipe`, `meal`, `workout`, `summary`) with embedded styles, live macro calculations, and Epley 1RM estimation.
- **T3 — MCP Tool (`src/mcp/tools/ui_tools.py`):** Implement `get_ui_form(form_type="hub")` and register in `src/mcp/server.py` (tool #19).
- **T4 — Starlette Web Routes & API Dispatch (`src/mcp/server.py`):** Mount `/ui` and `/ui/{form_type}` returning `HTMLResponse`, and mount `/api/{tool_name}` dispatching to MCP tool handlers.
- **T5 — Unit, Integration, & E2E Tests:** Test `get_ui_form` tool, verify Starlette HTTP routes `/ui` and `/api`, test client form generation, and ensure full test suite passes.

## Tasks
> Check the box as each task is completed.

- [x] T1: Clarify delivery mechanism, data submission, and layout with user
- [x] T2: Implement UI Generator module (`src/ui/html_generator.py`) with 5 views and dynamic JS
- [x] T3: Implement `get_ui_form` MCP tool (`src/mcp/tools/ui_tools.py`) and register on server
- [x] T4: Add `/ui` web routes and `/api/{tool_name}` dispatch to Starlette app in `server.py`
- [x] T5: Integration & E2E tests for UI artifacts and full test suite pass

## Verification
> Spec contrast (filled at close)

- [x] C1-C5: Implemented in `src/ui/html_generator.py` with modern dark fitness styling, dynamic ingredient rows, real-time Epley 1RM recalculations, meal logging, and daily summary dashboard.
- [x] C6: `get_ui_form` MCP tool implemented in `src/mcp/tools/ui_tools.py` and registered in `src/mcp/server.py` (total 19 tools); Starlette HTTP custom routes `/ui`, `/ui/{form_type}`, and `/api/{tool_name}` mounted and functioning.
- [x] C7: Self-contained zero-dependency HTML5 with embedded CSS and vanilla JS; supports hybrid submission (`fetch` to `/api/{tool_name}` with fallback "Copy for Hermes" prompt/JSON clipboard button).
- [x] Tests: Verified by `tests/integration/test_mcp_ui_tools.py`, `tests/integration/test_ui_web_routes.py`, `tests/integration/test_mcp_server.py`, and `tests/e2e/test_hermes_e2e.py::test_hermes_ui_artifact_flow`. Full suite passes: **145 tests in 1.40s**.

## Close
> Close (filled at close)

- Date: 2026-11
- Next step: Review remaining backlog items (#7 `db-robustness`, #9 `odd-merge-back`, #10 `google-health-api`, #8 `seed-data`).
