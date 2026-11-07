"""Modelos Peewee (ORM) para SQLite.

Una clase por tabla. Heredan de BaseModel para compartir la instancia de DB.
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

# Instancia global de DB (se reasigna en tests a :memory:)
db = SQLiteExtDatabase("data/fitness.db")


class BaseModel(Model):
    """Base class para todos los modelos. Permite cambiar la DB en tests."""

    class Meta:
        database = db


class Ingredient(BaseModel):
    """Ingrediente con macros y precio por unidad base."""

    name = CharField()
    unit = CharField()  # 'gr' | 'ml' | 'u'
    kcal = FloatField(default=0)
    protein = FloatField(default=0)
    carbs = FloatField(default=0)
    fat = FloatField(default=0)
    price = FloatField(default=0)
    provisional = BooleanField(default=False)
    created_at = DateTimeField(default=SQL("datetime('now')"))
    updated_at = DateTimeField(default=SQL("datetime('now')"))

    class Meta:
        table_name = "ingredients"
        indexes = ((("name", "unit"), True),)  # UNIQUE (name, unit)


class Recipe(BaseModel):
    """Receta (compuesta con ingredientes, o opaca con precio directo)."""

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
    """Ingrediente dentro de una receta (con cantidad)."""

    recipe = ForeignKeyField(Recipe, on_delete="CASCADE")
    ingredient = ForeignKeyField(Ingredient, on_delete="RESTRICT")
    quantity = FloatField()
    unit = CharField()  # 'gr' | 'ml' | 'u'

    class Meta:
        table_name = "recipe_items"


class MealEntry(BaseModel):
    """Registro de una ingesta (polimórfico: ingrediente o receta)."""

    date = CharField()  # DD-MM-YYYY
    item_type = CharField()  # 'ingredient' | 'recipe'
    item_id = IntegerField()  # FK polimórfica (sin constraint)
    quantity = FloatField()
    unit = CharField()  # 'gr' | 'ml' | 'u'
    created_at = DateTimeField(default=SQL("datetime('now')"))

    class Meta:
        table_name = "meal_entries"


class DailyGoal(BaseModel):
    """Objetivo diario de macros."""

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
    """Ejercicio del catálogo."""

    name = CharField(unique=True)
    muscle_group = CharField(default="desconocido")
    type = CharField(default="weight_reps")  # 'weight_reps' | 'time' | 'distance'
    created_at = DateTimeField(default=SQL("datetime('now')"))

    class Meta:
        table_name = "exercises"


class WorkoutSession(BaseModel):
    """Sesión de entrenamiento."""

    date = DateTimeField()
    notes = TextField(null=True)
    created_at = DateTimeField(default=SQL("datetime('now')"))

    class Meta:
        table_name = "workout_sessions"


class ExerciseSet(BaseModel):
    """Un set dentro de una sesión."""

    session = ForeignKeyField(WorkoutSession, on_delete="CASCADE")
    exercise = ForeignKeyField(Exercise, on_delete="RESTRICT")
    set_number = IntegerField()
    reps = IntegerField(null=True)
    weight = FloatField(null=True)
    duration = FloatField(null=True)  # segundos
    distance = FloatField(null=True)  # metros

    class Meta:
        table_name = "exercise_sets"


class PersonalRecord(BaseModel):
    """PR de un ejercicio (uno por ejercicio)."""

    exercise = ForeignKeyField(Exercise, on_delete="CASCADE", unique=True)
    max_weight = FloatField()
    max_reps = IntegerField()
    estimated_1rm = FloatField()
    date = CharField()  # DD-MM-YYYY
    session = ForeignKeyField(WorkoutSession, null=True, on_delete="SET NULL")

    class Meta:
        table_name = "personal_records"


# Lista de todos los modelos (para create_tables / migraciones)
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
]