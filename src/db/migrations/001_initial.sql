-- 001_initial.sql
-- Initial scheme: all tables, indexes and views.

CREATE TABLE IF NOT EXISTS ingredients (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    unit        TEXT    NOT NULL CHECK (unit IN ('gr', 'ml', 'u')),
    kcal        REAL    NOT NULL DEFAULT 0,
    protein     REAL    NOT NULL DEFAULT 0,
    carbs       REAL    NOT NULL DEFAULT 0,
    fat         REAL    NOT NULL DEFAULT 0,
    price       REAL    NOT NULL DEFAULT 0,
    provisional INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE (name, unit)
);

CREATE INDEX IF NOT EXISTS idx_ingredients_name ON ingredients(name);
CREATE INDEX IF NOT EXISTS idx_ingredients_provisional ON ingredients(provisional) WHERE provisional = 1;

CREATE TABLE IF NOT EXISTS recipes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    price       REAL,
    kcal        REAL,
    protein     REAL,
    carbs       REAL,
    fat         REAL,
    provisional INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE (name)
);

CREATE INDEX IF NOT EXISTS idx_recipes_name ON recipes(name);
CREATE INDEX IF NOT EXISTS idx_recipes_provisional ON recipes(provisional) WHERE provisional = 1;

CREATE TABLE IF NOT EXISTS recipe_items (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id     INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE RESTRICT,
    quantity      REAL    NOT NULL,
    unit          TEXT    NOT NULL CHECK (unit IN ('gr', 'ml', 'u'))
);

CREATE INDEX IF NOT EXISTS idx_recipe_items_recipe ON recipe_items(recipe_id);
CREATE INDEX IF NOT EXISTS idx_recipe_items_ingredient ON recipe_items(ingredient_id);

CREATE TABLE IF NOT EXISTS meal_entries (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    date       TEXT    NOT NULL,
    item_type  TEXT    NOT NULL CHECK (item_type IN ('ingredient', 'recipe')),
    item_id    INTEGER NOT NULL,
    quantity   REAL    NOT NULL,
    unit       TEXT    NOT NULL CHECK (unit IN ('gr', 'ml', 'u')),
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_meal_entries_date ON meal_entries(date);
CREATE INDEX IF NOT EXISTS idx_meal_entries_item ON meal_entries(item_type, item_id);
CREATE INDEX IF NOT EXISTS idx_meal_entries_date_item ON meal_entries(date, item_type, item_id);

CREATE TABLE IF NOT EXISTS daily_goals (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    date       TEXT    NOT NULL UNIQUE,
    kcal       REAL    NOT NULL,
    protein    REAL    NOT NULL,
    carbs      REAL    NOT NULL,
    fat        REAL    NOT NULL,
    is_default INTEGER NOT NULL DEFAULT 0,
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS exercises (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL UNIQUE,
    muscle_group  TEXT    NOT NULL DEFAULT 'unknown',
    type          TEXT    NOT NULL DEFAULT 'weight_reps' CHECK (type IN ('weight_reps', 'time', 'distance')),
    created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_exercises_name ON exercises(name);
CREATE INDEX IF NOT EXISTS idx_exercises_muscle ON exercises(muscle_group);

CREATE TABLE IF NOT EXISTS workout_sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    date       TEXT    NOT NULL,
    notes      TEXT,
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_sessions_date ON workout_sessions(date);

CREATE TABLE IF NOT EXISTS exercise_sets (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  INTEGER NOT NULL REFERENCES workout_sessions(id) ON DELETE CASCADE,
    exercise_id INTEGER NOT NULL REFERENCES exercises(id) ON DELETE RESTRICT,
    set_number  INTEGER NOT NULL,
    reps        INTEGER,
    weight      REAL,
    duration    REAL,
    distance    REAL
);

CREATE INDEX IF NOT EXISTS idx_sets_session ON exercise_sets(session_id);
CREATE INDEX IF NOT EXISTS idx_sets_exercise ON exercise_sets(exercise_id);
CREATE INDEX IF NOT EXISTS idx_sets_exercise_session ON exercise_sets(exercise_id, session_id);

CREATE TABLE IF NOT EXISTS personal_records (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id   INTEGER NOT NULL UNIQUE REFERENCES exercises(id) ON DELETE CASCADE,
    max_weight    REAL    NOT NULL,
    max_reps      INTEGER NOT NULL,
    estimated_1rm REAL    NOT NULL,
    date          TEXT    NOT NULL,
    session_id    INTEGER REFERENCES workout_sessions(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_pr_exercise ON personal_records(exercise_id);