-- 006_day_off_goals.sql: Add is_day_off and is_day_off_default flags to daily_goals
ALTER TABLE daily_goals ADD COLUMN is_day_off INTEGER NOT NULL DEFAULT 0;
ALTER TABLE daily_goals ADD COLUMN is_day_off_default INTEGER NOT NULL DEFAULT 0;
