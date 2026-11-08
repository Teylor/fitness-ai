"""Migration SQL Runner.

Executes SQL files in order and records which ones were applied in _migrations.
"""

from pathlib import Path
from typing import List

from peewee import Model, CharField, DateTimeField, SQL


def ensure_migrations_table(db) -> None:
    """Create the _migrations table if it doesn't exist."""
    if not db.table_exists("_migrations"):
        db.execute_sql("""
            CREATE TABLE IF NOT EXISTS _migrations (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                filename    TEXT    NOT NULL UNIQUE,
                applied_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)


def get_applied_migrations(db) -> set:
    """Return the set of applied filenames."""
    ensure_migrations_table(db)
    rows = db.execute_sql("SELECT filename FROM _migrations").fetchall()
    return {row[0] for row in rows}


def get_pending_migrations(db, migrations_dir: Path) -> List[Path]:
    """Return the list of pending SQL files, ordered by name."""
    if not migrations_dir.exists():
        return []
    applied = get_applied_migrations(db)
    all_files = sorted(migrations_dir.glob("*.sql"))
    return [f for f in all_files if f.name not in applied]


def apply_migrations(db, migrations_dir: Path) -> None:
    """Execute pending migrations and register them in _migrations."""
    pending = get_pending_migrations(db, migrations_dir)
    for migration_file in pending:
        sql_content = migration_file.read_text(encoding="utf-8")
        # Execute the SQL (can contain multiple statements)
        db.connection().executescript(sql_content)
        # Register
        db.execute_sql(
            "INSERT INTO _migrations (filename) VALUES (?)",
            (migration_file.name,),
        )
        print(f"  [migrate] Applied: {migration_file.name}")
