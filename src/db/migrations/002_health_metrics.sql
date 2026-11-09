-- 002_health_metrics.sql
-- Inbound health data from Google Health: sleep sessions and weight logs.

CREATE TABLE IF NOT EXISTS sleep_logs (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    date                 TEXT    NOT NULL,
    start_time           TEXT    NOT NULL,
    end_time             TEXT    NOT NULL,
    duration_minutes     REAL    NOT NULL,
    deep_sleep_minutes   REAL    NOT NULL DEFAULT 0,
    rem_sleep_minutes    REAL    NOT NULL DEFAULT 0,
    light_sleep_minutes  REAL    NOT NULL DEFAULT 0,
    source               TEXT    NOT NULL DEFAULT 'google_health',
    created_at           TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE (date, start_time)
);

CREATE INDEX IF NOT EXISTS idx_sleep_logs_date ON sleep_logs(date);

CREATE TABLE IF NOT EXISTS weight_logs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    date          TEXT    NOT NULL,
    weight_kg     REAL    NOT NULL,
    bmi           REAL,
    body_fat_pct  REAL,
    source        TEXT    NOT NULL DEFAULT 'google_health',
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    UNIQUE (date, created_at)
);

CREATE INDEX IF NOT EXISTS idx_weight_logs_date ON weight_logs(date);

