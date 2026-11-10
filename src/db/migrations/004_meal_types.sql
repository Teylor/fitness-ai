-- 004_meal_types.sql: Add meal_type to meal_entries table
ALTER TABLE meal_entries ADD COLUMN meal_type VARCHAR(50) NOT NULL DEFAULT 'tentempie';
CREATE INDEX IF NOT EXISTS idx_meal_entries_meal_type ON meal_entries (meal_type);
