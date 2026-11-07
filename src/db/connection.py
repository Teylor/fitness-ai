"""Gestión de conexión SQLite (Peewee)."""

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from src.config import settings
from src.db.models import db, ALL_MODELS, BaseModel


def get_db() -> Generator:
    """Context manager que transacciona automáticamente.

    Uso:
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
            pass  # No cerramos: la conexión es long-lived (servidor 24/7)


def init_db() -> None:
    """Crea el directorio de datos, conecta a la DB y crea tablas si no existen.

    Idempotente: seguro llamarlo múltiples veces.
    """
    # Crear directorio de datos
    db_path = settings.db_file
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Reasignar la DB al path correcto (la instancia global apunta a "data/fitness.db" relativo)
    db.init(str(db_path))

    # Conectar
    if db.is_closed():
        db.connect()

    # Crear tablas si no existen (idempotente)
    db.create_tables(ALL_MODELS, safe=True)

    # Aplicar migraciones SQL pendientes (para índices, vistas, etc.)
    from src.db.migrate import apply_migrations
    apply_migrations(db, settings.migrations_path)
