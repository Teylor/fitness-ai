"""Shared test fixtures."""

import pytest
from peewee import SqliteDatabase
from src.config import settings
from src.db.models import (
    db as real_db,
    ALL_MODELS,
    BaseModel,
    Ingredient,
    Recipe,
    RecipeItem,
    MealEntry,
    DailyGoal,
    Exercise,
    WorkoutSession,
    ExerciseSet,
    PersonalRecord,
    SleepLog,
    WeightLog,
)


@pytest.fixture
def db():
    """In-memory SQLite DB for tests.

    Rebinds global DB to :memory: and creates all tables.
    """
    # Create in-memory DB with foreign keys enabled
    test_db = SqliteDatabase(
        ":memory:",
        pragmas={"foreign_keys": 1, "busy_timeout": 5000},
    )
    test_db.connect()

    # Rebind DB on all models
    models_to_bind = ALL_MODELS + [BaseModel]
    for model in models_to_bind:
        model._meta.database = test_db

    # Create tables
    test_db.create_tables(ALL_MODELS)

    yield test_db

    # Cleanup
    test_db.close()

    # Restore original DB
    for model in models_to_bind:
        model._meta.database = real_db


@pytest.fixture(autouse=True)
def isolate_external_apis(monkeypatch):
    """Ensure tests run offline by default without hitting live Google Health APIs."""
    monkeypatch.setattr(settings, "google_health_token", None)
    monkeypatch.setattr(settings, "google_health_refresh_token", None)


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
