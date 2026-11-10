"""SQLite connection management (Peewee)."""

from contextlib import contextmanager
from typing import Generator, Optional
from peewee import SqliteDatabase

from src.config import settings
from src.db.models import db, ALL_MODELS, BaseModel, SQLITE_PRAGMAS


@contextmanager
def get_db(database: Optional[SqliteDatabase] = None) -> Generator[SqliteDatabase, None, None]:
    """Context manager that automatically commits on success and rolls back on error.

    Supports nested transactions via Peewee atomic blocks (savepoints).

    Usage:
        with get_db() as conn:
            Ingredient.create(name="Pan", unit="gr", ...)
    """
    target_db = database or BaseModel._meta.database or db
    if target_db.is_closed():
        target_db.connect(reuse_if_open=True)

    with target_db.atomic():
        yield target_db


def init_db() -> None:
    """Create the data directory, connect to the DB, apply PRAGMAs and migrations.

    Important: calling multiple times is safe (idempotent).
    """
    # Create the data directory
    db_path = settings.db_file
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Reassign the DB to the correct path with PRAGMAs configured
    db.init(str(db_path), pragmas=SQLITE_PRAGMAS)

    # Connect
    if db.is_closed():
        db.connect(reuse_if_open=True)

    # Apply core SQLite PRAGMAs explicitly
    db.execute_sql("PRAGMA foreign_keys = ON;")
    db.execute_sql("PRAGMA journal_mode = WAL;")
    db.execute_sql("PRAGMA busy_timeout = 5000;")
    db.execute_sql("PRAGMA synchronous = NORMAL;")

    # Create tables if not exists (idempotent)
    db.create_tables(ALL_MODELS, safe=True)

    # Apply pending SQL migrations (for indexes, views, etc.)
    from src.db.migrate import apply_migrations
    apply_migrations(db, settings.migrations_path)
