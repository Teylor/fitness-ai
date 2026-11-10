"""Unit tests for DB robustness: get_db context manager, transactions, rollbacks, and PRAGMAs."""

import pytest
from peewee import IntegrityError, SqliteDatabase

from src.db.connection import get_db, init_db
from src.db.models import (
    Ingredient,
    Recipe,
    RecipeItem,
    Exercise,
    WorkoutSession,
    ExerciseSet,
    db as global_db,
)


def test_get_db_commits_on_success(db):
    """Changes made inside with get_db(): are committed on normal exit."""
    with get_db():
        Ingredient.create(
            name="Avena",
            unit="gr",
            kcal=3.89,
            protein=0.169,
            carbs=0.663,
            fat=0.069,
            price=0.002,
        )

    ing = Ingredient.get_or_none(Ingredient.name == "Avena")
    assert ing is not None
    assert ing.unit == "gr"
    assert ing.kcal == 3.89


def test_get_db_rolls_back_on_error(db):
    """Changes made inside with get_db(): are completely rolled back if an exception occurs."""
    initial_count = Ingredient.select().count()

    with pytest.raises(ValueError, match="Simulated mid-transaction failure"):
        with get_db():
            Ingredient.create(
                name="Platano",
                unit="u",
                kcal=89.0,
                protein=1.1,
                carbs=22.8,
                fat=0.3,
            )
            # Raise exception before leaving context manager
            raise ValueError("Simulated mid-transaction failure")

    assert Ingredient.select().count() == initial_count
    assert Ingredient.get_or_none(Ingredient.name == "Platano") is None


def test_get_db_nested_savepoints(db):
    """Nested get_db contexts act as savepoints; inner rollback does not taint outer if caught."""
    with get_db():
        Ingredient.create(name="Outer Ingredient", unit="gr", kcal=100)

        try:
            with get_db():
                Ingredient.create(name="Inner Failed Ingredient", unit="gr", kcal=200)
                raise RuntimeError("Inner failure")
        except RuntimeError:
            pass  # Inner transaction rolled back to savepoint

        Ingredient.create(name="Outer Second Ingredient", unit="gr", kcal=150)

    assert Ingredient.get_or_none(Ingredient.name == "Outer Ingredient") is not None
    assert Ingredient.get_or_none(Ingredient.name == "Outer Second Ingredient") is not None
    assert Ingredient.get_or_none(Ingredient.name == "Inner Failed Ingredient") is None


def test_foreign_keys_enforced(db):
    """Foreign key enforcement raises IntegrityError when referencing non-existent parent rows."""
    ing = Ingredient.create(name="Arroz", unit="gr", kcal=130)

    # Valid foreign key
    rec = Recipe.create(name="Arroz Blanco")
    item = RecipeItem.create(recipe=rec, ingredient=ing, quantity=100, unit="gr")
    assert item.id is not None

    # Invalid foreign key reference to non-existent recipe ID
    with pytest.raises(IntegrityError):
        RecipeItem.create(recipe=999999, ingredient=ing, quantity=50, unit="gr")

    # Invalid foreign key reference to non-existent workout session
    ex = Exercise.create(name="Sentadilla", muscle_group="Piernas", type="weight_reps")
    with pytest.raises(IntegrityError):
        ExerciseSet.create(
            session=999999,
            exercise=ex,
            set_order=1,
            reps=10,
            weight_kg=100.0,
        )


def test_get_db_reconnects_if_closed(tmp_path):
    """get_db automatically connects if database was closed."""
    disk_db = SqliteDatabase(str(tmp_path / "reconnect.db"))
    disk_db.connect()
    disk_db.close()
    assert disk_db.is_closed()

    with get_db(disk_db):
        assert not disk_db.is_closed()


def test_init_db_configures_pragmas(tmp_path, monkeypatch):
    """init_db creates disk database with WAL, foreign_keys=1, busy_timeout=5000."""
    temp_db_file = tmp_path / "test_robustness.db"
    from src.config import settings

    monkeypatch.setattr(settings, "db_path", str(temp_db_file))

    # Initialize DB on disk
    init_db()

    # Query PRAGMAs on the real SQLite connection
    fk = global_db.execute_sql("PRAGMA foreign_keys;").fetchone()[0]
    journal = global_db.execute_sql("PRAGMA journal_mode;").fetchone()[0]
    timeout = global_db.execute_sql("PRAGMA busy_timeout;").fetchone()[0]
    sync = global_db.execute_sql("PRAGMA synchronous;").fetchone()[0]

    assert fk == 1
    assert journal.lower() == "wal"
    assert timeout == 5000
    assert sync == 1  # NORMAL

    global_db.close()
