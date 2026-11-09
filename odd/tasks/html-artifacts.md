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

- [ ] C1: Interactive HTML artifact for **Ingredient Management**: Form to input name, unit (`gr`, `ml`, `u`), calories, protein, carbs, fat, price per base unit, and provisional flag, with live validation.
- [ ] C2: Interactive HTML artifact for **Recipe Builder**: Dynamic ingredient list builder with searchable catalog, quantity inputs, and instant live recalculation of total recipe macros (kcal, protein, carbs, fat) and cost.
- [ ] C3: Interactive HTML artifact for **Meal Logger**: Date picker (default today), item selector (ingredient vs recipe), portion size, and real-time visual progress bars against daily goals.
- [ ] C4: Interactive HTML artifact for **Workout Logger**: Date/time input, notes, dynamic table to add/remove exercises and sets (set number, reps, weight, duration), with live estimated 1RM computation (Epley formula).
- [ ] C5: Unified Dashboard / Hub view: A cohesive single-page app or tabbed artifact allowing switching between all 4 entry types and viewing today's summary.
- [ ] C6: Hermes & MCP Integration: Expose the artifacts through an MCP tool (e.g. `get_html_artifact` / `render_form`) and local HTTP routes (`/ui/...`) so Hermes can either embed the raw HTML or link to it.
- [ ] C7: Mobile-friendly & standalone: Self-contained (clean embedded CSS, no build tool / npm requirement), responsive for mobile screens, supports dark mode, and handles data submission (direct fetch or copy-as-tool-call/prompt).

## Clarify
> Ambiguities and resolutions (filled interactively with the user)

- **Q1. How should Hermes deliver and render the artifacts?**
- **Q2. How should submitted data flow back into the system?**
- **Q3. Layout format: Individual standalone artifacts per action, a unified tabbed dashboard, or both?**
- **Q4. Styling and technology stack?**

## Plan
> Implementation plan (filled after clarify)

- (pending clarification)

## Tasks
> Check the box as each task is completed.

- [ ] T1: Clarify delivery mechanism, data submission, and layout with user
- [ ] T2: Core artifact template & styling design system
- [ ] T3: Ingredient & Recipe builder artifacts
- [ ] T4: Meal & Workout logging artifacts
- [ ] T5: MCP tools / server endpoint integration
- [ ] T6: Tests, polish, and verification

## Verification
> Spec contrast (filled at close)

- (pending)

## Close
> Close (filled at close)

- (pending)
