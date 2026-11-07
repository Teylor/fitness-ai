"""Fixtures compartidos para tests."""

import pytest
from peewee import SqliteDatabase

from src.db.models import (
    db,
    ALL_MODELS,
    Ingredient,
    Recipe,
    RecipeItem,
    MealEntry,
    DailyGoal,
    Exercise,
    WorkoutSession,
    ExerciseSet,
    PersonalRecord,
)


@pytest.fixture
def db():
    """DB SQLite in-memory para tests.

    Reasigna la DB global a :memory: y crea todas las tablas.
    """
    # Guardar la DB original
    original_db = db

    # Crear DB in-memory
    test_db = SqliteDatabase(":memory:")
    test_db.connect()

    # Reasignar la DB en todos los modelos
    for model in ALL_MODELS:
        model._meta.database = test_db

    # Crear tablas
    test_db.create_tables(ALL_MODELS)

    yield test_db

    # Cleanup
    test_db.close()

    # Restaurar DB original
    for model in ALL_MODELS:
        model._meta.database = original_db


@pytest.fixture
def ingredient_service():
    from src.services.ingredient_service import IngredientService
    return IngredientService()


@pytest.fixture
def recipe_service():
    from src.services.recipe_service import RecipeService
    return RecipeService()


@pytest.fixture
def meal_service():
    from src.services.meal_service import MealService
    return MealService()


@pytest.fixture
def goal_service():
    from src.services.goal_service import GoalService
    return GoalService()


@pytest.fixture
def exercise_service():
    from src.services.exercise_service import ExerciseService
    return ExerciseService()


@pytest.fixture
def workout_service():
    from src.services.workout_service import WorkoutService
    return WorkoutService()
