"""Servicio de registro de comidas."""

from datetime import datetime

from src.db.models import (
    Ingredient as IngredientModel,
    MealEntry as MealEntryModel,
    Recipe as RecipeModel,
)
from src.models.meal_entry import MealEntry
from src.services.goal_service import GoalService
from src.utils.macros import calc_ingredient_macros

ITEM_TYPES = ("ingredient", "recipe")
MACRO_KEYS = ("kcal", "protein", "carbs", "fat")


class MealService:
    """Registro y consulta de ingesta diaria."""

    @staticmethod
    def _parse_date(value: str) -> datetime:
        try:
            parsed = datetime.strptime(value, "%d-%m-%Y")
        except (TypeError, ValueError) as exc:
            raise ValueError(f"invalid date '{value}' (expected DD-MM-YYYY)") from exc
        if parsed.strftime("%d-%m-%Y") != value:
            raise ValueError(f"invalid date '{value}' (expected DD-MM-YYYY)")
        return parsed

    @staticmethod
    def _to_domain(row) -> MealEntry:
        return MealEntry(
            id=row.id,
            date=row.date,
            item_type=row.item_type,
            item_id=row.item_id,
            quantity=row.quantity,
            unit=row.unit,
            created_at=str(row.created_at) if row.created_at is not None else None,
        )

    @staticmethod
    def _ensure_item(item_type: str, item_id: int, unit: str):
        """Crea provisional el item si no existe."""
        if item_type == "ingredient":
            row = IngredientModel.get_or_none(IngredientModel.id == item_id)
            if row is None:
                row = IngredientModel.create(
                    id=item_id, name=f"provisional-{item_id}", unit=unit,
                    provisional=True
                )
        else:
            row = RecipeModel.get_or_none(RecipeModel.id == item_id)
            if row is None:
                row = RecipeModel.create(
                    id=item_id, name=f"provisional-{item_id}", provisional=True
                )
        return row

    def _entry_macros(self, row) -> dict:
        """Macros y precio de una entrada: item × quantity (receta = multiplicador)."""
        if row.item_type == "ingredient":
            item = IngredientModel.get_by_id(row.item_id)
            if item is None:
                item = IngredientModel.create(
                    name=f"provisional-{row.item_id}", unit=row.unit, provisional=True
                )
            return calc_ingredient_macros(item, row.quantity)
        item = RecipeModel.get_by_id(row.item_id)
        if item is None:
            return {**{key: 0.0 for key in MACRO_KEYS}, "price": 0.0}
        return {
            key: round((getattr(item, key) or 0.0) * row.quantity, 2)
            for key in MACRO_KEYS
        } | {"price": round((item.price or 0.0) * row.quantity, 2)}

    def register(self, entry: MealEntry) -> MealEntry:
        """Registra una ingesta. Crea provisional si no existe el item."""
        self._parse_date(entry.date)
        if entry.item_type not in ITEM_TYPES:
            raise ValueError(f"invalid item_type '{entry.item_type}'")
        with MealEntryModel._meta.database.atomic():
            self._ensure_item(entry.item_type, entry.item_id, entry.unit)
            row = MealEntryModel.create(
                date=entry.date,
                item_type=entry.item_type,
                item_id=entry.item_id,
                quantity=entry.quantity,
                unit=entry.unit,
            )
        return self._to_domain(row)

    def get_day_entries(self, date: str) -> list:
        """Devuelve todas las ingesta de un día con macros calculados."""
        self._parse_date(date)
        rows = MealEntryModel.select().where(MealEntryModel.date == date)
        rows = rows.order_by(MealEntryModel.id)
        meals = []
        for row in rows:
            item = self._to_domain(row)
            macros = self._entry_macros(row)
            meals.append({"entry": item, **macros})
        return meals

    def get_day_summary(self, date: str) -> dict:
        """Resumen: consumed, goal, remaining, spend, meals."""
        meals = self.get_day_entries(date)
        consumed = {
            key: round(sum(m[key] for m in meals), 2) for key in MACRO_KEYS
        }
        spend = round(sum(m["price"] for m in meals), 2)
        goal_row = GoalService().get_goal(date)
        goal = {
            "date": goal_row.date,
            "kcal": goal_row.kcal,
            "protein": goal_row.protein,
            "carbs": goal_row.carbs,
            "fat": goal_row.fat,
        }
        remaining = {key: round(goal[key] - consumed[key], 2) for key in MACRO_KEYS}
        return {
            "consumed": consumed,
            "spend": spend,
            "goal": goal,
            "remaining": remaining,
            "meals": meals,
        }

    def update(self, entry_id: int, **fields) -> MealEntry:
        """Actualiza campos de una ingesta (date, item_type, item_id, quantity, unit)."""
        row = MealEntryModel.get_or_none(MealEntryModel.id == entry_id)
        if row is None:
            raise ValueError(f"meal entry {entry_id} not found")
        if "date" in fields:
            self._parse_date(fields["date"])
        if "item_type" in fields and fields["item_type"] not in ITEM_TYPES:
            raise ValueError(f"invalid item_type '{fields['item_type']}'")
        for field, value in fields.items():
            setattr(row, field, value)
        row.save()
        return self._to_domain(row)

    def delete(self, entry_id: int) -> None:
        """Borra una ingesta."""
        row = MealEntryModel.get_or_none(MealEntryModel.id == entry_id)
        if row is None:
            raise ValueError(f"meal entry {entry_id} not found")
        row.delete_instance()