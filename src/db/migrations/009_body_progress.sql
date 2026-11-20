-- 009_body_progress.sql: Daily body measurements progress tracking
CREATE TABLE IF NOT EXISTS body_progress_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL UNIQUE,
    weight_kg REAL NULL,
    waist_cm REAL NULL,
    chest_cm REAL NULL,
    arm_cm REAL NULL,
    leg_cm REAL NULL,
    notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT (datetime('now')),
    updated_at DATETIME NOT NULL DEFAULT (datetime('now'))
);
