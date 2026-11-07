"""Runner de migraciones SQL.

Ejecuta archivos .sql en orden y registra cuáles se aplicaron en _migrations.
"""

from pathlib import Path
from typing import List

from peewee import Model, CharField, DateTimeField, SQL


def ensure_migrations_table(db) -> None:
    """Crea la tabla _migrations si no existe."""
    if not db.table_exists("_migrations"):
        db.execute_sql("""
            CREATE TABLE IF NOT EXISTS _migrations (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                filename    TEXT    NOT NULL UNIQUE,
                applied_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)


def get_applied_migrations(db) -> set:
    """Devuelve el set de filenames ya aplicados."""
    ensure_migrations_table(db)
    rows = db.execute_sql("SELECT filename FROM _migrations").fetchall()
    return {row[0] for row in rows}


def get_pending_migrations(db, migrations_dir: Path) -> List[Path]:
    """Devuelve los archivos .sql no aplicados, ordenados por nombre."""
    if not migrations_dir.exists():
        return []
    applied = get_applied_migrations(db)
    all_files = sorted(migrations_dir.glob("*.sql"))
    return [f for f in all_files if f.name not in applied]


def apply_migrations(db, migrations_dir: Path) -> None:
    """Ejecuta migraciones pendientes y las registra en _migrations."""
    pending = get_pending_migrations(db, migrations_dir)
    for migration_file in pending:
        sql_content = migration_file.read_text(encoding="utf-8")
        # Ejecutar el SQL (puede contener múltiples statements)
        db.execute_sql(sql_content)
        # Registrar
        db.execute_sql(
            "INSERT INTO _migrations (filename) VALUES (?)",
            (migration_file.name,),
        )
        print(f"  [migrate] Applied: {migration_file.name}")
```

**T3 done.** Ahora **T5: `src/config.py`** (verificar/ajustar):

```tool
TOOL_NAME: read_file
BEGIN_ARG: filepath
src/config.py
