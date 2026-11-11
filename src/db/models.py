"""Peewee Models (ORM) for SQLite.

A class per table. Inherits from BaseModel to share the DB instance.
"""

from peewee import (
    Model,
    CharField,
    TextField,
    FloatField,
    BooleanField,
    IntegerField,
    DateTimeField,
    ForeignKeyField,
    SQL,
)
from playhouse.sqlite_ext import SqliteDatabase

SQLITE_PRAGMAS = {
    "journal_mode": "wal",
    "cache_size": -1024 * 64,  # 64MB cache
    "foreign_keys": 1,
    "ignore_check_constraints": 0,
    "synchronous": 1,  # NORMAL
    "busy_timeout": 5000,
}

# Global instance of DB (assigned to :memory: in tests)
db = SqliteDatabase("data/fitness.db", pragmas=SQLITE_PRAGMAS)


class BaseModel(Model):
    """Base class for all models. Allows changing the DB in tests."""

    class Meta:
        database = db


class Ingredient(BaseModel):
    """Ingredients with macros and price per unit."""

    name = CharField()
    unit = CharField()  # 'gr' | 'ml' | 'u'
    kcal = FloatField(default=0)
    protein = FloatField(default=0)
    carbs = FloatField(default=0)
    fat = FloatField(default=0)
    price = FloatField(default=0)
    is_supplement = BooleanField(default=False)
    provisional = BooleanField(default=False)
    created_at = DateTimeField(default=SQL("datetime('now')"))
    updated_at = DateTimeField(default=SQL("datetime('now')"))

    class Meta:
        table_name = "ingredients"
        indexes = ((("name", "unit"), True),)  # UNIQUE (name, unit)


class Recipe(BaseModel):
    """Recipe (made with ingredients, or opaque with direct price)."""

    name = CharField(unique=True)
    price = FloatField(null=True)
    kcal = FloatField(null=True)
    protein = FloatField(null=True)
    carbs = FloatField(null=True)
    fat = FloatField(null=True)
    provisional = BooleanField(default=False)
    created_at = DateTimeField(default=SQL("datetime('now')"))
    updated_at = DateTimeField(default=SQL("datetime('now')"))

    class Meta:
        table_name = "recipes"


class RecipeItem(BaseModel):
    """Ingredients in a recipe (with quantity)."""

    recipe = ForeignKeyField(Recipe, on_delete="CASCADE")
    ingredient = ForeignKeyField(Ingredient, on_delete="RESTRICT")
    quantity = FloatField()
    unit = CharField()  # 'gr' | 'ml' | 'u'

    class Meta:
        table_name = "recipe_items"


class MealEntry(BaseModel):
    """Register of a meal (ingredient or recipe)."""

    date = CharField()  # DD-MM-YYYY
    item_type = CharField()  # 'ingredient' | 'recipe'
    item_id = IntegerField()  # FK polymorphic (without constraint)
    quantity = FloatField()
    unit = CharField()  # 'gr' | 'ml' | 'u'
    meal_type = CharField(default="tentempie")  # 'desayuno' | 'comida' | 'merienda' | 'cena' | 'tentempie'
    created_at = DateTimeField(default=SQL("datetime('now')"))

    class Meta:
        table_name = "meal_entries"


class DailyGoal(BaseModel):
    """Daily macro goal."""

    date = CharField(unique=True)  # DD-MM-YYYY
    kcal = FloatField()
    protein = FloatField()
    carbs = FloatField()
    fat = FloatField()
    is_default = BooleanField(default=False)
    created_at = DateTimeField(default=SQL("datetime('now')"))

    class Meta:
        table_name = "daily_goals"


class Exercise(BaseModel):
    """Exercise catalog."""

    name = CharField(unique=True)
    muscle_group = CharField(default="unknown")
    type = CharField(default="weight_reps")  # 'weight_reps' | 'time' | 'distance'
    created_at = DateTimeField(default=SQL("datetime('now')"))

    class Meta:
        table_name = "exercises"


class WorkoutSession(BaseModel):
    """Workout session."""

    date = DateTimeField()
    notes = TextField(null=True)
    created_at = DateTimeField(default=SQL("datetime('now')"))

    class Meta:
        table_name = "workout_sessions"


class ExerciseSet(BaseModel):
    """A set within a workout session."""

    session = ForeignKeyField(WorkoutSession, on_delete="CASCADE")
    exercise = ForeignKeyField(Exercise, on_delete="RESTRICT")
    set_number = IntegerField()
    reps = IntegerField(null=True)
    weight = FloatField(null=True)
    duration = FloatField(null=True)  # seconds
    distance = FloatField(null=True)  # meters

    class Meta:
        table_name = "exercise_sets"


class PersonalRecord(BaseModel):
    """PR of an exercise (one PR per exercise)."""

    exercise = ForeignKeyField(Exercise, on_delete="CASCADE", unique=True)
    max_weight = FloatField()
    max_reps = IntegerField()
    estimated_1rm = FloatField()
    date = CharField()  # DD-MM-YYYY
    session = ForeignKeyField(WorkoutSession, null=True, on_delete="SET NULL")

    class Meta:
        table_name = "personal_records"


class SleepLog(BaseModel):
    """Inbound sleep sessions from Google Health."""

    date = CharField()  # DD-MM-YYYY
    start_time = CharField()
    end_time = CharField()
    duration_minutes = FloatField()
    deep_sleep_minutes = FloatField(default=0.0)
    rem_sleep_minutes = FloatField(default=0.0)
    light_sleep_minutes = FloatField(default=0.0)
    source = CharField(default="google_health")
    created_at = DateTimeField(default=SQL("datetime('now')"))

    class Meta:
        table_name = "sleep_logs"
        indexes = ((("date", "start_time"), True),)


class WeightLog(BaseModel):
    """Inbound weight logs from Google Health."""

    date = CharField()  # DD-MM-YYYY
    weight_kg = FloatField()
    bmi = FloatField(null=True)
    body_fat_pct = FloatField(null=True)
    source = CharField(default="google_health")
    created_at = DateTimeField(default=SQL("datetime('now')"))

    class Meta:
        table_name = "weight_logs"


class StepLog(BaseModel):
    """Daily step count activity tracking."""

    date = CharField(unique=True)  # DD-MM-YYYY
    steps = IntegerField(default=0)
    distance_km = FloatField(null=True)
    source = CharField(default="manual")
    created_at = DateTimeField(default=SQL("datetime('now')"))
    updated_at = DateTimeField(default=SQL("datetime('now')"))

    class Meta:
        table_name = "step_logs"


# List of all models
ALL_MODELS = [
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
    StepLog,
]
