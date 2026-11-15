# Requirements

> Requirements specification for the nutrition, finance, and workout tracking system.
> Primary interaction: voice → Hermes Agent (MCP) → System.

## Context

The system runs 24/7 on a local PC (server mode). An AI agent (Hermes Agent) connects via a local MCP server to execute actions: logging meals, querying macros, recording workouts, checking PRs, etc. The user interacts with Hermes via phone.

"Finance" scope is limited to food cost tracking: every ingredient/recipe carries a price per base unit, and the daily summary reports total spend against the day.

## Stack

| Component | Technology |
|---|---|
| Language | Python |
| Database | SQLite |
| AI Integration | MCP Server (local) |

## Goals

- Log meals with minimal friction from a voice interaction: one agent tool call registers an intake and returns the macros, the price, and the day's remaining budget.
- Track daily macro goals and the remaining budget (consumed vs goal) including food spend.
- Log workouts (session → exercises → sets) and automatically track personal records (estimated 1RM).
- Be safe to use from a voice interface: creation is idempotent, unknown items are auto-created as provisional instead of failing, and name resolution is fuzzy (case/accent-insensitive).
- Run fully local: one process, one SQLite file, no external services.

## Non-goals

- No user-facing UI beyond the agent (no web/mobile app, no auth, single local user).
- No barcode lookup or remote nutrition databases; the catalog is user-managed.
- No analytics beyond per-day summaries and per-exercise PRs.
- No multi-device sync or multi-user support.

## Actors

| Actor | Description |
|---|---|
| User | Owns the data. Interacts by voice via phone. |
| Hermes Agent | AI agent. Converts user intent into MCP tool calls and interprets the JSON responses. |
| fitness-ai server | The system under specification. Local MCP server exposing the tool contract (see `api-spec.md`). |

## Functional requirements

### FR1 — Nutrition catalog

- **FR1.1** The system manages ingredients with macros and price expressed **per base unit** (`gr` | `ml` | `u`).
- **FR1.2** Ingredient macro/price data can be flagged `provisional` (not yet confirmed) and filtered on.
- **FR1.3** The system manages recipes in two shapes:
  - **compound**: built from ingredient items; macros and price are **computed** from the items × ingredient data;
  - **opaque**: carry direct `price` / macro values.
- **FR1.4** Duplicate creation is prevented by normalized name (case- and accent-insensitive): ingredients unique by `(name, unit)`, recipes by `name`. Creation tools are **idempotent** — a duplicate returns the existing item as success, not an error.
- **FR1.5** An ingredient in use by a recipe cannot be deleted (conflict).
- **FR1.6** Ingredients support a boolean flag `is_supplement` (default `false`) to distinguish supplements (e.g., Creatine, Omega 3) from culinary ingredients.

### FR2 — Meal logging

- **FR2.1** An intake is registered by item name, quantity, and unit. The item type (`ingredient` | `recipe`) may be omitted: resolution order is exact/normalized/fuzzy ingredient → fuzzy recipe → **auto-created provisional ingredient**.
- **FR2.2** Unknown items never fail a registration: they are auto-created as `provisional` and used.
- **FR2.3** Intakes carry a date (`DD-MM-YYYY`); default = today.
- **FR2.4** The day summary reports: consumed macros, total spend, the applicable goal, remaining macros (goal − consumed), the per-meal breakdown with each meal's computed macros, and grouped subtotals by `meal_type`.
- **FR2.5** Macros of a compound recipe are applied as `stored_value × quantity` (recipe values act as a per-unit multiplier); ingredient macros scale per the unit convention (see `api-spec.md`).
- **FR2.6** Meals support a category `meal_type` (`desayuno`, `comida`, `merienda`, `cena`, `tentempie`, defaulting to `tentempie`). Both MCP registration and the Web UI allow selecting the meal type.
- **FR2.7** Every day includes a fixed daily water intake of **3L at 1.25€** (`water_and_supplements.water`), added to the daily `spend`. Supplements (`is_supplement = true`) and the 3L daily water are grouped into a dedicated **"Agua y Suplementos"** section in both the Ingredients Catalog and the Daily Summary.
- **FR2.8** Daily creatine (`water_and_supplements.creatine`) is enabled by default for every day (1 unit / 5g at 0.30€, or resolved from the `"Creatina"` catalog ingredient when present), toggleable per date via `toggle_daily_creatine` (`POST /api/toggle_daily_creatine`) without duplicating manually logged creatine entries.

### FR3 — Daily goals

- **FR3.1** The system manages daily macro goals, one per date, plus a single global **default** goal.
- **FR3.2** Goal resolution for a date follows the fallback chain: explicit goal for that date → closest **previous** dated goal → default goal. If none exists, the lookup fails with `not_found`.
- **FR3.3** Setting a new default goal clears the default flag on all other goals.

### FR4 — Training catalog

- **FR4.1** The system manages an exercise catalog: name (unique, normalized), free-text `muscle_group`, and `type` ∈ `weight_reps` | `time` | `distance`.
- **FR4.2** Exercise creation is idempotent by normalized name (a duplicate returns the existing exercise, no error); fuzzy matches do not block creation.

### FR5 — Workout logging

- **FR5.1** A session carries a date (`DD-MM-YYYY`, optional time part; default = now) and optional notes, and contains exercises, each with one or more sets.
- **FR5.2** Registration is **atomic**: the session and all its sets are created or none (full rollback on any validation error).
- **FR5.3** Unknown exercises in a session are auto-created (`muscle_group = "unknown"`, type inferred from the set payload: `reps`/`weight` → `weight_reps`, `duration` → `time`, `distance` → `distance`) and reported in the response.
- **FR5.4** Set validation per exercise type:
  - `weight_reps`: `reps` (≥ 1) and `weight` (≥ 0) required;
  - `time`: `duration` in seconds (> 0) required;
  - `distance`: `distance` in meters (> 0) required;
  - `set_number` is a positive integer, unique per exercise within the session.

### FR6 — Personal records (PRs)

- **FR6.1** At most one PR row per exercise; only `weight_reps` exercises get PRs.
- **FR6.2** The PR triple (`max_weight`, `max_reps`, `estimated_1rm`) comes from the set with the highest estimated 1RM. Estimated 1RM: a set with `reps = 1` uses the **exact weight** (direct attempt); any other set uses the Epley formula `weight × (1 + reps/30)`.
- **FR6.3** The PR row is created/updated only when the new estimated 1RM is **strictly greater** than the stored one.
- **FR6.4** A PR records the date and the session that produced it (session link is nullable; deleting the session nulls it, deleting the exercise removes the PR).
- **FR6.5** Exercise performance metrics queries (`WorkoutService.get_exercise_stats` / `list_exercises(include_prs=True)`) extract both the highest Estimated 1RM PR (`estimated_1rm`) and the Max Weight set (`max_weight` with `max_weight_reps` and session date) across all historical sets.

### FR7 — Health & Activity Tracking (Google Health)

- **FR7.1** The system integrates with Google Health API v4 for bidirectional synchronization.
- **FR7.2** Logged meals are uploaded to Google Health as `nutrition-log` data points with energy (`kcal`), total fat (`grams`), carbohydrates (`grams`), protein (`nutrients`), and categorized `mealType` (`BREAKFAST`, `LUNCH`, `BEFORE_DINNER`, `DINNER`, `SNACK`). Registration and deletion of meals automatically trigger background synchronization with Google Health when credentials are configured.
- **FR7.3** Sleep sessions and body weight measurements are pulled from Google Health and persisted in local `sleep_logs` and `weight_logs`.
- **FR7.4** Daily step counts are synchronized exclusively from Google Health (`fetch_google_health_steps`, `sync_google_health`) and stored in local `step_logs` with `source="google_health"`. Manual step entry via UI and tool is disabled (`manual_steps_disabled`).
- **FR7.5** OAuth 2.0 authentication supports transparent token renewal using a `refresh_token`; when expired (HTTP 401), tokens are refreshed from Google OAuth and persisted to `.env` without user disruption.

### FR8 — Generative UI Artifacts & Views

- **FR8.1** The MCP server generates standalone interactive HTML artifacts (`get_ui_form`, `generate_html`) for embedding in Antigravity or Hermes chat interfaces.
- **FR8.2** The UI provides tabbed navigation: Daily Summary (goal comparison, progress bars, macro breakdown), Meals (with live ingredient/recipe search and delete action), Training (exercises and sets), Steps, Sleep, Weight, and Catalog management (inline creation, edition, and deletion).
- **FR8.3** Direct HTTP endpoints (`/ui`, `/ui/{form_type}`, `/api/{tool_name}`) allow browser interaction and asynchronous tool execution directly from UI widgets.
- **FR8.4** The web UI header and Daily Summary views provide one-click "Sincronizar Google Health" actions to trigger full synchronization and refresh metrics.
- **FR8.5** A dedicated Exercises section (`/ui/exercise`) displays catalog exercises with muscle group, exercise type, estimated 1RM PR badge, heaviest weight set badge with repetitions, search and muscle group filter (options built dynamically from the groups actually present in the catalog, current selection preserved across refreshes), an inline per-row editor (muscle group input with datalist of existing groups plus free text, type select, saved via `POST /api/update_exercise` and row refresh), and an inline exercise creation form.

### FR9 — Catalog & Log Deletions

- **FR9.1** Individual meal entries can be deleted by ID (`delete_meal`).
- **FR9.2** Ingredients can be deleted by ID (`delete_ingredient`), provided they are not referenced by existing recipes (`RESTRICT`).
- **FR9.3** Recipes can be deleted by ID (`delete_recipe`), cascading deletion to associated `recipe_items`.

## Non-functional requirements

- **NFR1 — Local-only:** single process, single SQLite file, safe for 24/7 unattended operation with optional cloud sync to Google Health.
- **NFR2 — Idempotent creation:** all creation paths tolerate retries (voice/agent may repeat a call): normalized exact duplicates return the existing item.
- **NFR3 — Fuzzy resolution:** name lookups are normalized (lowercase, accents stripped, whitespace collapsed) with a fuzzy fallback (similarity threshold 0.6).
- **NFR4 — Typed errors:** every tool failure returns a machine-readable envelope `{"status": "error", "code": ..., "message": ...}` with codes from a fixed vocabulary (`not_found`, `duplicate`, `invalid_input`, `conflict`, `internal`).
- **NFR5 — Single user:** no multi-user partitioning or authentication overhead for local MCP calls.
- **NFR6 — Language:** code, docstrings, and documentation are in English.
- **NFR7 — Database Reliability:** SQLite runs with `foreign_keys = ON` to enforce constraints, `journal_mode = WAL` to allow concurrent readers/writers without locking, `busy_timeout = 5000` to prevent transient lock failures, and transactional contexts (`get_db`) with automatic rollback on error.

## Cross-references

- Tool contract (26 MCP tools): [`api-spec.md`](./api-spec.md)
- Schema (12 tables): [`data-model.md`](./data-model.md)
