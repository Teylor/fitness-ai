"""Smoke test: init → insert → select → cleanup."""

from src.db.models import Ingredient, MealEntry, Exercise


def test_insert_and_select_ingredient(db):
    """Insert un ingrediente y selecciónalo."""
    ing = Ingredient.create(
        name="Pan",
        unit="gr",
        kcal=2.2,
        protein=0.07,
        carbs=0.45,
        fat=0.02,
        price=0.003,
        provisional=False,
    )
    assert ing.id is not None

    fetched = Ingredient.get_by_id(ing.id)
    assert fetched.name == "Pan"
    assert fetched.unit == "gr"
    assert fetched.kcal == 2.2


def test_insert_and_select_meal_entry(db):
    """Insert un meal_entry y selecciónalo."""
    ing = Ingredient.create(
        name="Kiwi", unit="u", kcal=49, protein=0.8,
        carbs=11.5, fat=0.5, price=0.15,
    )
    entry = MealEntry.create(
        date="15-01-2025",
        item_type="ingredient",
        item_id=ing.id,
        quantity=2,
        unit="u",
    )
    assert entry.id is not None

    fetched = MealEntry.get_by_id(entry.id)
    assert fetched.quantity == 2
    assert fetched.item_type == "ingredient"


def test_insert_and_select_exercise(db):
    """Insert un ejercicio y selecciónalo."""
    ex = Exercise.create(
        name="Press de banca",
        muscle_group="Pecho",
        type="weight_reps",
    )
    assert ex.id is not None

    fetched = Exercise.get_by_id(ex.id)
    assert fetched.name == "Press de banca"
    assert fetched.muscle_group == "Pecho"


def test_unique_constraint_ingredient(db):
    """No se puede crear dos ingredientes con mismo name+unit."""
    from peewee import IntegrityError

    Ingredient.create(name="Pan", unit="gr", kcal=2.2)
    try:
        Ingredient.create(name="Pan", unit="gr", kcal=3.0)
        assert False, "Debería lanzar IntegrityError"
    except IntegrityError:
        pass  # Esperado


def test_all_tables_created(db):
    """Verificar que las 9 tablas existen."""
    expected = {
        "ingredients", "recipes", "recipe_items", "meal_entries",
        "daily_goals", "exercises", "workout_sessions",
        "exercise_sets", "personal_records",
    }
    cursor = db.execute_sql("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cursor.fetchall()}
    assert expected.issubset(tables), f"Faltan tablas: {expected - tables}"