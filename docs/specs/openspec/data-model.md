# Data Model

> SQLite schema for the nutrition, finance, and workout tracking system.
> Source of truth: `src/db/migrations/001_initial.sql` and the Peewee models in `src/db/models.py`.

## Conventions

- **Engine**: SQLite, single file `data/fitness.db`.
- **ORM**: Peewee — one class per table, sharing a global `SqliteDatabase` instance (re-pointed to `:memory:` in tests).
- **Primary keys**: `INTEGER PRIMARY KEY AUTOINCREMENT`, aliased `id`.
- **Timestamps**: `created_at` / `updated_at` stored as `TEXT` via `datetime('now')` (UTC).
- **User dates**: stored as `TEXT` in `DD-MM-YYYY` form.
- **`workout_sessions.date` exception**: stored as a full datetime (Peewee `DateTimeField`; SQLite renders it as `YYYY-MM-DD HH:MM:SS.SSS` text). The public API accepts/exposes it as `DD-MM-YYYY` or `DD-MM-YYYY HH:MM[:SS]`.
- **Units**: `gr` | `ml` | `u`.
- **Macros**: `kcal` (energy), `protein`, `carbs`, `fat` (grams).
- **Booleans**: stored as `INTEGER` (0/1).
- **`provisional`**: flag marking rows whose macro/price data is not yet confirmed.
- **PRAGMAs & Concurrency**:
  - `PRAGMA foreign_keys = ON;` — enforced on all connections to validate referential integrity and execute cascade/restrict behaviors.
  - `PRAGMA journal_mode = WAL;` — Write-Ahead Logging enables concurrent readers without blocking writes, avoiding database locks during 24/7 background operation.
  - `PRAGMA busy_timeout = 5000;` — waits up to 5000 ms on transient locks before raising errors.
  - `PRAGMA synchronous = NORMAL;` — recommended durability and write performance mode for WAL.
  - **Transaction Management**: `get_db()` context manager provides atomic transactions with automatic rollback on error and nested savepoint support.

## Relationships

```
ingredients 1 ──── * recipe_items * ──── 1 recipes
                                          │
meal_entries * ─── item_type='recipe'  ──┤   (polymorphic — no FK constraint)
meal_entries * ─── item_type='ingredient' ─── 1 ingredients

exercises 1 ──── * exercise_sets * ──── 1 workout_sessions
exercises 1 ──── 1 personal_records
workout_sessions 1 ──── 0..1 personal_records  (ON DELETE SET NULL)
```

- `recipe_items` is the join table between `recipes` and `ingredients`, carrying `quantity` + `unit`.
- `meal_entries` is **polymorphic**: `item_type` + `item_id` point to either an `ingredients` row or a `recipes` row. There is no foreign-key constraint — the application enforces referential integrity.
- `exercise_sets` belong to one `workout_sessions` row and reference one `exercises` row.
- `personal_records` holds at most one row per exercise (unique `exercise_id`) and optionally links back to the `workout_sessions` row that produced it.

## Tables

### `ingredients`

A food item with macros and price, expressed per base unit.

| Field | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PK AUTOINCREMENT | |
| name | TEXT | NOT NULL | |
| unit | TEXT | NOT NULL, `CHECK (unit IN ('gr','ml','u'))` | Base unit of the macros/price below |
| kcal | REAL | NOT NULL DEFAULT 0 | Energy per base unit |
| protein | REAL | NOT NULL DEFAULT 0 | Grams per base unit |
| carbs | REAL | NOT NULL DEFAULT 0 | Grams per base unit |
| fat | REAL | NOT NULL DEFAULT 0 | Grams per base unit |
| price | REAL | NOT NULL DEFAULT 0 | Cost per base unit |
| provisional | INTEGER | NOT NULL DEFAULT 0 | Data not yet confirmed |
| created_at | TEXT | NOT NULL DEFAULT `datetime('now')` | |
| updated_at | TEXT | NOT NULL DEFAULT `datetime('now')` | |

- **Unique**: `(name, unit)`
- **Indexes**: `idx_ingredients_name` (`name`); partial `idx_ingredients_provisional` (`WHERE provisional = 1`)

### `recipes`

A named recipe. Two shapes: **compound** (built from `recipe_items`, macros/price computed) or **opaque** (direct `price` and, optionally, direct macros).

| Field | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PK AUTOINCREMENT | |
| name | TEXT | NOT NULL, UNIQUE | |
| price | REAL | NULL | Direct price (opaque recipes) |
| kcal | REAL | NULL | Set when the recipe carries its own macros |
| protein | REAL | NULL | |
| carbs | REAL | NULL | |
| fat | REAL | NULL | |
| provisional | INTEGER | NOT NULL DEFAULT 0 | Data not yet confirmed |
| created_at | TEXT | NOT NULL DEFAULT `datetime('now')` | |
| updated_at | TEXT | NOT NULL DEFAULT `datetime('now')` | |

- **Indexes**: `idx_recipes_name` (`name`); partial `idx_recipes_provisional` (`WHERE provisional = 1`)

### `recipe_items`

An ingredient within a recipe, with a quantity.

| Field | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PK AUTOINCREMENT | |
| recipe_id | INTEGER | NOT NULL, `REFERENCES recipes(id) ON DELETE CASCADE` | |
| ingredient_id | INTEGER | NOT NULL, `REFERENCES ingredients(id) ON DELETE RESTRICT` | |
| quantity | REAL | NOT NULL | |
| unit | TEXT | NOT NULL, `CHECK (unit IN ('gr','ml','u'))` | |

- **Indexes**: `idx_recipe_items_recipe` (`recipe_id`); `idx_recipe_items_ingredient` (`ingredient_id`)
- Deleting a recipe cascades to its items; deleting an ingredient is blocked while it is used in any recipe (`RESTRICT`).

### `meal_entries`

A logged intake (polymorphic — an ingredient or a recipe), with a date.

| Field | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PK AUTOINCREMENT | |
| date | TEXT | NOT NULL | `DD-MM-YYYY` |
| item_type | TEXT | NOT NULL, `CHECK (item_type IN ('ingredient','recipe'))` | |
| item_id | INTEGER | NOT NULL | Polymorphic pointer — no FK constraint |
| quantity | REAL | NOT NULL | |
| unit | TEXT | NOT NULL, `CHECK (unit IN ('gr','ml','u'))` | |
| created_at | TEXT | NOT NULL DEFAULT `datetime('now')` | |

- **Indexes**: `idx_meal_entries_date` (`date`); `idx_meal_entries_item` (`item_type`, `item_id`); `idx_meal_entries_date_item` (`date`, `item_type`, `item_id`)

### `daily_goals`

Daily macro targets. One row per date; `is_default` marks the standing goal.

| Field | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PK AUTOINCREMENT | |
| date | TEXT | NOT NULL, UNIQUE | `DD-MM-YYYY` |
| kcal | REAL | NOT NULL | |
| protein | REAL | NOT NULL | |
| carbs | REAL | NOT NULL | |
| fat | REAL | NOT NULL | |
| is_default | INTEGER | NOT NULL DEFAULT 0 | Standing goal flag |
| created_at | TEXT | NOT NULL DEFAULT `datetime('now')` | |

### `exercises`

Catalog of exercises.

| Field | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PK AUTOINCREMENT | |
| name | TEXT | NOT NULL, UNIQUE | |
| muscle_group | TEXT | NOT NULL DEFAULT `'unknown'` | Free text |
| type | TEXT | NOT NULL DEFAULT `'weight_reps'`, `CHECK (type IN ('weight_reps','time','distance'))` | Drives which `exercise_sets` columns apply |
| created_at | TEXT | NOT NULL DEFAULT `datetime('now')` | |

- **Indexes**: `idx_exercises_name` (`name`); `idx_exercises_muscle` (`muscle_group`)

### `workout_sessions`

A training session.

| Field | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PK AUTOINCREMENT | |
| date | TEXT | NOT NULL | Stored datetime (see Conventions — the only non-`DD-MM-YYYY` user date) |
| notes | TEXT | NULL | |
| created_at | TEXT | NOT NULL DEFAULT `datetime('now')` | |

- **Indexes**: `idx_sessions_date` (`date`)

### `exercise_sets`

A single set within a session.

| Field | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PK AUTOINCREMENT | |
| session_id | INTEGER | NOT NULL, `REFERENCES workout_sessions(id) ON DELETE CASCADE` | |
| exercise_id | INTEGER | NOT NULL, `REFERENCES exercises(id) ON DELETE RESTRICT` | |
| set_number | INTEGER | NOT NULL | |
| reps | INTEGER | NULL | Applies to `weight_reps` |
| weight | REAL | NULL | Applies to `weight_reps` |
| duration | REAL | NULL | Seconds — applies to `time` |
| distance | REAL | NULL | Meters — applies to `distance` |

- **Indexes**: `idx_sets_session` (`session_id`); `idx_sets_exercise` (`exercise_id`); `idx_sets_exercise_session` (`exercise_id`, `session_id`)
- Deleting a session cascades to its sets; deleting an exercise is blocked while sets reference it (`RESTRICT`).

### `personal_records`

A personal record (PR) per exercise — at most one row per exercise.

| Field | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PK AUTOINCREMENT | |
| exercise_id | INTEGER | NOT NULL, UNIQUE, `REFERENCES exercises(id) ON DELETE CASCADE` | |
| max_weight | REAL | NOT NULL | |
| max_reps | INTEGER | NOT NULL | |
| estimated_1rm | REAL | NOT NULL | |
| date | TEXT | NOT NULL | `DD-MM-YYYY` |
| session_id | INTEGER | NULL, `REFERENCES workout_sessions(id) ON DELETE SET NULL` | Session that produced the PR |

- **Indexes**: `idx_pr_exercise` (`exercise_id`)
- Deleting an exercise removes its PR; deleting the linked session nulls `session_id`.

### `sleep_logs`

Inbound sleep sessions from Google Health.

| Field | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PK AUTOINCREMENT | |
| date | TEXT | NOT NULL | `DD-MM-YYYY` |
| start_time | TEXT | NOT NULL | ISO start timestamp |
| end_time | TEXT | NOT NULL | ISO end timestamp |
| duration_minutes | REAL | NOT NULL | Sleep duration in minutes |
| deep_sleep_minutes | REAL | NOT NULL DEFAULT 0 | Deep sleep in minutes |
| rem_sleep_minutes | REAL | NOT NULL DEFAULT 0 | REM sleep in minutes |
| light_sleep_minutes | REAL | NOT NULL DEFAULT 0 | Light sleep in minutes |
| source | TEXT | NOT NULL DEFAULT `'google_health'` | Data source |
| created_at | TEXT | NOT NULL DEFAULT `datetime('now')` | |

- **Indexes**: `idx_sleep_logs_date` (`date`); `UNIQUE (date, start_time)`

### `weight_logs`

Inbound body weight measurements from Google Health.

| Field | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PK AUTOINCREMENT | |
| date | TEXT | NOT NULL | `DD-MM-YYYY` |
| weight_kg | REAL | NOT NULL | Body weight in kilograms |
| bmi | REAL | NULL | Body Mass Index |
| body_fat_pct | REAL | NULL | Body fat percentage |
| source | TEXT | NOT NULL DEFAULT `'google_health'` | Data source |
| created_at | TEXT | NOT NULL DEFAULT `datetime('now')` | |

- **Indexes**: `idx_weight_logs_date` (`date`); `UNIQUE (date, created_at)`

### `step_logs`

Daily physical step counts and estimated walking/running distance.

| Field | Type | Constraints | Description |
|---|---|---|---|
| id | INTEGER | PK AUTOINCREMENT | |
| date | TEXT | NOT NULL | `DD-MM-YYYY` |
| steps | INTEGER | NOT NULL DEFAULT 0 | Daily step count |
| distance_km | REAL | NULL | Estimated distance in km |
| source | TEXT | NOT NULL DEFAULT `'manual'` | Data source (`'manual'` \| `'google_health'`) |
| created_at | TEXT | NOT NULL DEFAULT `datetime('now')` | |
| updated_at | TEXT | NOT NULL DEFAULT `datetime('now')` | |

- **Indexes**: `idx_step_logs_date` (`date`); `UNIQUE (date)`

## Enumerations

| Field | Allowed values |
|---|---|
| `ingredients.unit`, `recipes`-related `unit`, `meal_entries.unit`, `recipe_items.unit` | `gr`, `ml`, `u` |
| `meal_entries.item_type` | `ingredient`, `recipe` |
| `exercises.type` | `weight_reps`, `time`, `distance` |

## Migration Notes

- The schema is applied by `src/db/migrate.py` over ordered files in `src/db/migrations/` (`001_initial.sql` is the initial, full schema).
- All `CREATE TABLE` / `CREATE INDEX` statements are idempotent (`IF NOT EXISTS`).
- `ALL_MODELS` in `src/db/models.py` lists every Peewee model for `create_tables` / test setup and must stay in sync with the migrations.
