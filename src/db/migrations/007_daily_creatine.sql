-- 007_daily_creatine.sql: Per-day toggle for automatic daily creatine tracking (enabled by default)
CREATE TABLE IF NOT EXISTS daily_creatine (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL UNIQUE,
    enabled INTEGER NOT NULL DEFAULT 1,
    updated_at DATETIME NOT NULL DEFAULT (datetime('now'))
);
