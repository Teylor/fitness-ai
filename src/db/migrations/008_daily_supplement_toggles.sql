-- 008_daily_supplement_toggles.sql: Per-day toggle for catalog supplements (default OFF, except Creatina)
CREATE TABLE IF NOT EXISTS daily_supplement_toggles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
    enabled INTEGER NOT NULL DEFAULT 0,
    updated_at DATETIME NOT NULL DEFAULT (datetime('now')),
    UNIQUE (date, ingredient_id)
);
