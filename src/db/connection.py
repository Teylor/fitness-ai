"""SQLite connection management (Peewee)."""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from src.config import settings
from src.db.models import db, ALL_MODELS, BaseModel


def get_db() -> Generator:
    """Context manager that automatically commits on success and rolls back on error.

    Usage:
        with get_db() as cursor:
            Ingredient.create(name="Pan", unit="gr", ...)
    """
    if not db.is_closed():
        yield db
        db.commit()
    else:
        db.connect()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            pass  # Do not close: the connection is long-lived (server 24/7)


def init_db() -> None:
    """Create the data directory, connect to the DB, and create tables if they do not exist.

    Important: calling multiple times is safe (idempotent).
    """
    # Create the data directory
    db_path = settings.db_file
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Reassign the DB to the correct path (the global instance points to "data/fitness.db" relative)
    db.init(str(db_path))

    # Connect
    if db.is_closed():
        db.connect()

    # Create tables if not exists (idempotent)
    db.create_tables(ALL_MODELS, safe=True)

    # Apply pending SQL migrations (for indexes, views, etc.)
    from src.db.migrate import apply_migrations
    apply_migrations(db, settings.migrations_path)
