-- 003_step_metrics.sql: Daily step count activity tracking
CREATE TABLE IF NOT EXISTS step_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT UNIQUE NOT NULL,
    steps INTEGER NOT NULL DEFAULT 0,
    distance_km REAL,
    source TEXT NOT NULL DEFAULT 'manual',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_step_logs_date ON step_logs(date);

