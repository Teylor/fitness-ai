# API Specification (MCP Server)

> MCP tools exposed by the local Python server. The Hermes Agent calls them
> to interact with the system.

## Conventions

- **Transport:** local MCP (`streamable-http` on localhost)
- **Format:** JSON in / JSON out
- **Envelope:**
  - Success: `{"status": "ok", ...}`
  - Error: `{"status": "error", "code": "<code>", "message": "<human-readable>"}`
- **Error codes** (fixed vocabulary):

  | Code | Meaning |
  |---|---|
  | `not_found` | The requested entity (or data for the lookup) does not exist |
  | `duplicate` | A normalized-name collision on a mutating operation |
  | `invalid_input` | Missing/invalid argument (format, range, required field) |
  | `conflict` | A referential constraint blocks the operation |
  | `internal` | Unexpected server error |

- **Idempotent creation:** `create_*` tools resolve the name first (exact → normalized → fuzzy, threshold 0.6) and return the existing item as success instead of failing.
- **Dates:** user dates are `DD-MM-YYYY` (e.g. `09-11-2026`). Workout session dates optionally carry a time: `DD-MM-YYYY HH:MM[:SS]` (e.g. `09-11-2026 17:00`); default = now.
- **Units:** `gr` | `ml` | `u`. Macros are in grams, kcal in energy units, prices in currency **per unit** (per `gr`/`ml`/`u`).
- **Pagination:** list tools take `limit` (default `50`) and `offset` (default `0`).

## Tool index (26)

| Domain | Tools |
|---|---|
| Ingredients (4) | `create_ingredient`, `update_ingredient`, `delete_ingredient`, `list_ingredients` |
| Recipes (4) | `create_recipe`, `update_recipe`, `delete_recipe`, `list_recipes` |
| Meals (3) | `register_meal`, `get_day_summary`, `delete_meal` |
| Goals (2) | `set_daily_goal`, `get_daily_goal` |
| Workouts (4) | `register_workout`, `get_last_workout`, `get_personal_record`, `get_workouts_by_day` |
| Exercises (2) | `list_exercises`, `create_exercise` |
| UI Artifacts (1) | `get_ui_form` |
| Health & Activity (7) | `sync_meals_to_google_health`, `fetch_google_health_sleep`, `fetch_google_health_weight`, `fetch_google_health_steps`, `sync_google_health`, `log_steps`, `get_health_metrics` |

### Common shapes

- `ingredient`: `{id, name, unit, kcal, protein, carbs, fat, price, provisional, created_at, updated_at}`
- `recipe`: `{id, name, price, kcal, protein, carbs, fat, provisional, created_at, updated_at, items: [{id, recipe_id, ingredient_id, quantity, unit}]}`
- `meal_entry`: `{id, date, item_type, item_id, quantity, unit, meal_type, created_at}`
- `daily_goal`: `{id, date, kcal, protein, carbs, fat, is_default, created_at}`
- `exercise`: `{id, name, muscle_group, type, created_at}`
- `personal_record`: `{id, exercise_id, max_weight, max_reps, estimated_1rm, date, session_id}`
- `sleep_log`: `{id, date, start_time, end_time, duration_minutes, deep_sleep_minutes, rem_sleep_minutes, light_sleep_minutes, source}`
- `weight_log`: `{id, date, weight_kg, bmi, body_fat_pct, source}`
- `step_log`: `{id, date, steps, distance_km, source, created_at, updated_at}`

---

## Ingredients

### `create_ingredient`

Create an ingredient; a duplicate (same normalized `name`+`unit`) returns the existing item.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `name` | str | ✔ | — | Ingredient name |
| `unit` | str | ✔ | — | Base unit: `gr` \| `ml` \| `u` |
| `kcal` | float | | `0` | kcal per unit |
| `protein` | float | | `0` | protein per unit (g) |
| `carbs` | float | | `0` | carbs per unit (g) |
| `fat` | float | | `0` | fat per unit (g) |
| `price` | float | | `0` | price per unit |
| `provisional` | bool | | `False` | mark data as unverified |

```json
{"status": "ok", "ingredient": {"id": 1, "name": "chicken breast", "unit": "gr", "kcal": 1.2, "protein": 0.23, "carbs": 0.0, "fat": 0.03, "price": 0.004, "provisional": false, "created_at": "2026-11-09 08:00:00", "updated_at": "2026-11-09 08:00:00"}}
```

Errors: `invalid_input` (bad unit), `internal`.

### `update_ingredient`

Update any subset of an ingredient's fields (all optional; at least one expected).

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `ingredient_id` | int | ✔ | — | Ingredient to update |
| `name`, `unit`, `kcal`, `protein`, `carbs`, `fat`, `price`, `provisional` | … | | `null` | Only the provided fields change |

```json
{"status": "ok", "ingredient": {"id": 1, "name": "chicken breast", "unit": "gr", "...": "..."}}
```

Errors: `not_found`, `invalid_input` (bad unit), `duplicate` (name+unit taken by another ingredient), `internal`.

### `delete_ingredient`

Delete an ingredient and its meal entries.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `ingredient_id` | int | ✔ | — | Ingredient to delete |

```json
{"status": "ok", "ingredient_id": 1, "deleted_entries": 3}
```

Errors: `not_found`, `conflict` (in use by a recipe), `internal`.

### `list_ingredients`

List/search ingredients.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `search` | str | | `null` | Substring (normalized) filter on name |
| `provisional_only` | bool | | `False` | only provisional items |
| `limit` / `offset` | int | | `50` / `0` | pagination |

```json
{"status": "ok", "ingredients": ["ingredient", "..."], "count": 42}
```

Errors: `internal`.

---

## Recipes

### `create_recipe`

Create a recipe. With `ingredients` → **compound** (macros/price computed from the items × ingredient data). Without → **opaque** (direct `price`/macro values). A duplicate name returns the existing recipe.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `name` | str | ✔ | — | Recipe name (unique) |
| `ingredients` | list[dict] | | `null` | items: `{"ingredient_id"?: int, "name"?: str, "quantity": float, "unit"?: str}`. Unknown item names are **auto-created as provisional ingredients** |
| `price` | float | | `null` | opaque mode only (per-unit) |
| `kcal`, `protein`, `carbs`, `fat` | float | | `null` | opaque mode only (per-unit) |
| `provisional` | bool | | `False` | mark recipe as unverified |

```json
{"status": "ok", "recipe": {"id": 1, "name": "chicken salad", "price": 0.05, "kcal": 0.15, "protein": 0.02, "carbs": 0.005, "fat": 0.004, "provisional": false, "created_at": "...", "updated_at": "...", "items": [{"id": 1, "recipe_id": 1, "ingredient_id": 1, "quantity": 100, "unit": "gr"}]}}
```

Errors: `duplicate` (name taken by another recipe, on update paths), `invalid_input` (item missing both `ingredient_id` and `name`, bad unit), `internal`.

### `update_recipe`

Update recipe fields; passing `ingredients` **replaces all items** and recomputes compound macros.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `recipe_id` | int | ✔ | — | Recipe to update |
| `name`, `price`, `kcal`, `protein`, `carbs`, `fat`, `provisional` | … | | `null` | only provided fields change |
| `ingredients` | list[dict] | | `null` | same item shape as `create_recipe`; replaces the whole list |

```json
{"status": "ok", "recipe": {"id": 1, "...": "..."}}
```

Errors: `not_found`, `duplicate`, `invalid_input`, `internal`.

### `delete_recipe`

Delete a recipe and its meal entries.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `recipe_id` | int | ✔ | — | Recipe to delete |

```json
{"status": "ok", "recipe_id": 1, "deleted_entries": 2}
```

Errors: `not_found`, `internal`.

### `list_recipes`

List/search recipes.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `search` | str | | `null` | substring filter on name |
| `provisional_only` | bool | | `False` | only provisional recipes |
| `type` | str | | `null` | `"compound"` (has items) \| `"opaque"` (no items) |
| `limit` / `offset` | int | | `50` / `0` | pagination |

```json
{"status": "ok", "recipes": ["recipe", "..."], "count": 7}
```

Errors: `internal`.

---

## Meals

### `register_meal`

Register a meal. `item_type` optional → resolution: exact/normalized/fuzzy **ingredient** → fuzzy **recipe** → auto-create **provisional ingredient** and use it. `date` defaults to today (`DD-MM-YYYY`).

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `item_name` | str | ✔ | — | ingredient or recipe name |
| `quantity` | float | ✔ | — | amount in `unit` |
| `unit` | str | ✔ | — | `gr` \| `ml` \| `u` (used when creating a new item) |
| `item_type` | str | | `null` | force `"ingredient"` \| `"recipe"` |
| `date` | str | | `null` | `DD-MM-YYYY`; default today |
| `meal_type` | str | | `"tentempie"` | `"desayuno"` \| `"comida"` \| `"merienda"` \| `"cena"` \| `"tentempie"` |

```json
{
  "status": "ok",
  "entry_id": 11,
  "meal_type": "tentempie",
  "macros": {"kcal": 150.0, "protein": 28.0, "carbs": 0.0, "fat": 3.0},
  "price": 0.4,
  "day_summary": {
    "consumed": {"kcal": 850.0, "protein": 60.0, "carbs": 90.0, "fat": 30.0},
    "spend": 4.2,
    "goal": {"date": "01-01-2026", "kcal": 2200.0, "protein": 160.0, "carbs": 200.0, "fat": 70.0, "is_default": true, "id": 1, "created_at": "..."},
    "remaining": {"kcal": 1350.0, "protein": 100.0, "carbs": 110.0, "fat": 40.0},
    "meals": [{"entry": {"id": 11, "date": "09-11-2026", "item_type": "ingredient", "item_id": 1, "quantity": 125.0, "unit": "gr", "meal_type": "tentempie", "created_at": "..."}, "meal_type": "tentempie", "kcal": 150.0, "protein": 28.0, "carbs": 0.0, "fat": 3.0, "price": 0.4}],
    "meals_by_type": {"tentempie": {"meals": [...], "kcal": 150.0, "protein": 28.0, "carbs": 0.0, "fat": 3.0, "spend": 0.4}}
  }
}
```

`day_summary` is `null` when no goal is found for the date.

Errors: `invalid_input` (bad date format, bad unit, invalid meal_type), `internal`.

### `get_day_summary`

Consumed macros, spend, goal, remaining, and per-meal breakdown for a day.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `date` | str | | `null` | `DD-MM-YYYY`; default today. Goal fallback: exact date → closest previous → default |

```json
{
  "status": "ok",
  "consumed": {"kcal": 850.0, "protein": 60.0, "carbs": 90.0, "fat": 30.0},
  "spend": 4.2,
  "goal": {"id": 1, "date": "01-01-2026", "kcal": 2200.0, "protein": 160.0, "carbs": 200.0, "fat": 70.0, "is_default": true, "created_at": "..."},
  "remaining": {"kcal": 1350.0, "protein": 100.0, "carbs": 110.0, "fat": 40.0},
  "meals": [{"entry": {"id": 11, "date": "09-11-2026", "item_type": "ingredient", "item_id": 1, "quantity": 125.0, "unit": "gr", "meal_type": "tentempie", "created_at": "..."}, "meal_type": "tentempie", "kcal": 150.0, "protein": 28.0, "carbs": 0.0, "fat": 3.0, "price": 0.4}],
  "meals_by_type": {
    "desayuno": {"meals": [], "kcal": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0, "spend": 0.0},
    "tentempie": {"meals": [...], "kcal": 150.0, "protein": 28.0, "carbs": 0.0, "fat": 3.0, "spend": 0.4},
    "comida": {"meals": [], "kcal": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0, "spend": 0.0},
    "merienda": {"meals": [], "kcal": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0, "spend": 0.0},
    "cena": {"meals": [], "kcal": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0, "spend": 0.0}
  }
}
```

Errors: `not_found` (no goal for the date or fallback), `invalid_input` (bad date), `internal`.

### `delete_meal`

Delete a logged meal entry by its primary key ID.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `entry_id` | int | ✔ | — | ID of the meal entry to delete |

```json
{"status": "ok", "entry_id": 11}
```

Errors: `not_found`, `invalid_input`, `internal`.

---

## Goals

### `set_daily_goal`

Create or update the goal for a date. `default=True` makes it the global default (clears the flag on all others).

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `kcal` | float | ✔ | — | kcal goal |
| `protein` | float | ✔ | — | protein goal (g) |
| `carbs` | float | ✔ | — | carbs goal (g) |
| `fat` | float | ✔ | — | fat goal (g) |
| `date` | str | | `null` | `DD-MM-YYYY`; default today |
| `default` | bool | | `False` | mark as the global default goal |

```json
{"status": "ok", "goal": {"id": 1, "date": "09-11-2026", "kcal": 2200.0, "protein": 160.0, "carbs": 200.0, "fat": 70.0, "is_default": false, "created_at": "..."}}
```

Errors: `invalid_input` (bad date), `internal`.

### `get_daily_goal`

Get the applicable goal for a date (fallback: exact date → closest previous → default).

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `date` | str | | `null` | `DD-MM-YYYY`; default today |

```json
{"status": "ok", "goal": {"id": 1, "date": "01-01-2026", "kcal": 2200.0, "protein": 160.0, "carbs": 200.0, "fat": 70.0, "is_default": true, "created_at": "..."}}
```

Errors: `not_found` (no goal at all), `invalid_input` (bad date), `internal`.

---

## Workouts

### `register_workout`

Register a workout session. **Atomic**: the session and all its sets are created or none (rollback on any error). Unknown exercises are auto-created (type inferred from the set payload) and reported in `auto_created`. PRs are upserted for `weight_reps` exercises.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `exercises` | list[dict] | ✔ | — | `{"name": str, "sets": [set, ...]}` where set is `{"set_number": int, "reps": int, "weight": float}` (weight_reps), `{"set_number": int, "duration": float}` (time, seconds) or `{"set_number": int, "distance": float}` (distance, meters) |
| `date` | str | | `null` | `DD-MM-YYYY` or `DD-MM-YYYY HH:MM[:SS]`; default now |
| `notes` | str | | `null` | session notes |

```json
{
  "status": "ok",
  "session": {"id": 3, "date": "09-11-2026 17:00:00", "notes": "push day"},
  "sets": [{"exercise": "bench press", "set_number": 1, "reps": 8, "weight": 80.0, "duration": null, "distance": null}],
  "new_prs": [{"exercise": "bench press", "max_weight": 80.0, "max_reps": 8, "estimated_1rm": 94.67, "date": "09-11-2026"}],
  "auto_created": []
}
```

Validation (`invalid_input`): `set_number` positive and unique per exercise; `weight_reps` sets need `reps ≥ 1` + `weight`; `time` sets need `duration > 0`; `distance` sets need `distance > 0`; bad date format. Errors: `invalid_input`, `internal`.

### `get_last_workout`

Last session containing an exercise, with its sets.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `exercise_name` | str | ✔ | — | exercise name (fuzzy-resolved) |

```json
{"status": "ok", "exercise": "bench press", "session_id": 3, "date": "09-11-2026 17:00:00", "sets": [{"set_number": 1, "reps": 8, "weight": 80.0, "duration": null, "distance": null}]}
```

Errors: `not_found` (unknown exercise or no session for it), `internal`.

### `get_personal_record`

The PR (best-set triple) for an exercise.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `exercise_name` | str | ✔ | — | exercise name (fuzzy-resolved) |

```json
{"status": "ok", "personal_record": {"id": 1, "exercise_id": 2, "max_weight": 80.0, "max_reps": 8, "estimated_1rm": 94.67, "date": "09-11-2026", "session_id": 3}}
```

Errors: `not_found` (unknown exercise or no PR yet), `internal`.

### `get_workouts_by_day`

Sessions of a day with all their sets.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `date` | str | | `null` | `DD-MM-YYYY`; default today |

```json
{
  "status": "ok",
  "sessions": [{"id": 3, "date": "09-11-2026 17:00:00", "notes": "push day", "sets": [{"exercise": "bench press", "set_number": 1, "reps": 8, "weight": 80.0, "duration": null, "distance": null}]}],
  "count": 1
}
```

Errors: `invalid_input` (bad date), `internal`.

---

## Exercises

### `list_exercises`

List/search the exercise catalog.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `search` | str | | `null` | substring filter on name |
| `muscle_group` | str | | `null` | filter by muscle group |
| `limit` / `offset` | int | | `50` / `0` | pagination |
| `include_prs` | bool \| str | | `false` | include PR stats (`estimated_1rm`, `max_weight`, `max_weight_reps`, etc.) |

```json
{
  "status": "ok",
  "exercises": [
    {
      "id": 1,
      "name": "bench press",
      "muscle_group": "chest",
      "type": "weight_reps",
      "created_at": "...",
      "pr": {
        "estimated_1rm": 26.7,
        "estimated_1rm_weight": 20.0,
        "estimated_1rm_reps": 10,
        "estimated_1rm_date": "15-05-2026",
        "max_weight": 22.0,
        "max_weight_reps": 6,
        "max_weight_date": "15-05-2026"
      }
    }
  ],
  "count": 1
}
```

Errors: `internal`.

### `create_exercise`

Create an exercise; idempotent — an exact or normalized duplicate returns the existing exercise (fuzzy matches do not block creation).

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `name` | str | ✔ | — | exercise name (unique, normalized) |
| `muscle_group` | str | | `"unknown"` | free-text muscle group |
| `type` | str | | `"weight_reps"` | `"weight_reps"` \| `"time"` \| `"distance"` |

```json
{"status": "ok", "exercise": {"id": 13, "name": "face pull", "muscle_group": "shoulders", "type": "weight_reps", "created_at": "..."}}
```

Errors: `invalid_input` (empty name, bad type), `internal`.

---

## UI Artifacts

### `get_ui_form`

Retrieve an interactive HTML artifact form for Hermes GUI or web view.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `form_type` | str | | `"hub"` | View type: `"hub"`, `"meal"`, `"recipe"`, `"ingredient"`, `"workout"`, or `"summary"` |

```json
{"status": "ok", "form_type": "hub", "html": "<!DOCTYPE html>...", "supported_types": ["hub", "meal", "recipe", "ingredient", "workout", "summary"]}
```

Errors: `invalid_input` (unsupported form_type), `internal`.

---

## Google Health

### `sync_meals_to_google_health`

Upload meals recorded on a specific date to Google Health as nutrition dataPoints.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `date` | str | | `today` | target date in `DD-MM-YYYY` |

```json
{"status": "ok", "date": "10-11-2026", "synced_count": 2, "total_kcal": 650.0, "meals": [{"meal_id": 1, "name": "Eggs", "quantity": 3.0, "unit": "u", "kcal": 210.0, "protein": 18.0, "carbs": 1.5, "fat": 15.0}]}
```

Errors: `invalid_input` (bad date, missing credentials), `internal`.

### `fetch_google_health_sleep`

Fetch sleep session dataPoints from Google Health and store in local `sleep_logs`.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `date` | str | | `today` | reference date in `DD-MM-YYYY` |
| `days` | int | | `1` | days of history |

```json
{"status": "ok", "date": "10-11-2026", "count": 1, "records": [{"id": 1, "date": "10-11-2026", "start_time": "...", "end_time": "...", "duration_minutes": 480.0, "deep_sleep_minutes": 90.0, "rem_sleep_minutes": 90.0, "light_sleep_minutes": 300.0, "source": "google_health"}]}
```

Errors: `invalid_input` (bad date, missing credentials), `internal`.

### `fetch_google_health_weight`

Fetch weight body measurements from Google Health and store in local `weight_logs`.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `date` | str | | `today` | reference date in `DD-MM-YYYY` |
| `days` | int | | `7` | days of history |

```json
{"status": "ok", "date": "10-11-2026", "count": 1, "latest_weight_kg": 75.2, "records": [{"id": 1, "date": "10-11-2026", "weight_kg": 75.2, "bmi": 22.8, "body_fat_pct": null, "source": "google_health"}]}
```

Errors: `invalid_input` (bad date, missing credentials), `internal`.

### `fetch_google_health_steps`

Fetch daily step count from Google Health and store/update in local `step_logs`.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `date` | str | | `today` | reference date in `DD-MM-YYYY` |

```json
{"status": "ok", "date": "10-11-2026", "steps": 8500, "source": "google_health"}
```

Errors: `invalid_input` (bad date, missing credentials), `internal`.

### `sync_google_health`

Full bidirectional synchronization: push meals, pull sleep, weight, and steps metrics.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `date` | str | | `today` | reference date in `DD-MM-YYYY` |

```json
{"status": "ok", "date": "10-11-2026", "meals_synced": 2, "total_kcal_synced": 650.0, "sleep_sessions_fetched": 1, "weight_records_fetched": 1, "latest_weight_kg": 75.2, "steps_fetched": 8500}
```

Errors: `invalid_input` (bad date, missing credentials), `internal`.

### `log_steps`

*Deprecated / Disabled*: Manual step logging is disabled in favor of automated synchronization from Google Health. Always returns `manual_steps_disabled`.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `steps` | int | ✔ | — | step count |
| `date` | str | | `today` | target date in `DD-MM-YYYY` |
| `distance_km` | float | | `null` | estimated distance in kilometers |

```json
{"status": "error", "code": "manual_steps_disabled", "message": "Manual step logging is disabled. Steps are synchronized automatically from Google Health."}
```

Errors: `manual_steps_disabled`.

### `get_health_metrics`

Retrieve aggregated health and activity metrics (sleep, weight, steps) for a specific date.

| Arg | Type | Req | Default | Description |
|---|---|---|---|---|
| `date` | str | | `today` | target date in `DD-MM-YYYY` |

```json
{
  "status": "ok",
  "date": "10-11-2026",
  "steps": 8500,
  "distance_km": 6.2,
  "latest_weight_kg": 75.2,
  "sleep_duration_minutes": 480.0,
  "sleep_records_count": 1,
  "weight_records_count": 1
}
```

Errors: `invalid_input` (bad date format), `internal`.

---

## Interactive Web Routes

In addition to JSON-RPC over MCP, the server serves interactive HTML forms and an HTTP API bridge:

| Route | Method | Description |
|---|---|---|
| `/ui` | `GET` | Render UI view (optional `?form=hub\|meal\|recipe\|ingredient\|workout\|summary`) |
| `/ui/{form_type}` | `GET` | Direct view rendering by form type path |
| `/api/{tool_name}` | `GET`, `POST` | HTTP execution bridge invoking any registered MCP tool and returning JSON |


