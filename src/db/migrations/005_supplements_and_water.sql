-- 005_supplements_and_water.sql: Add is_supplement flag to ingredients table
ALTER TABLE ingredients ADD COLUMN is_supplement BOOLEAN NOT NULL DEFAULT 0;
CREATE INDEX IF NOT EXISTS idx_ingredients_is_supplement ON ingredients (is_supplement);
