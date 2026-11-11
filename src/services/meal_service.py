"""Meal registration domain service."""

from dataclasses import asdict
from datetime import datetime

from src.db.models import (
    Ingredient as IngredientModel,
    MealEntry as MealEntryModel,
    Recipe as RecipeModel,
)
from src.models.meal_entry import MealEntry
from src.services.goal_service import GoalService
from src.utils.errors import NotFoundError, ValidationError
from src.utils.macros import calc_ingredient_macros

ITEM_TYPES = ("ingredient", "recipe")
MACRO_KEYS = ("kcal", "protein", "carbs", "fat")
ALLOWED_MEAL_TYPES = ("desayuno", "comida", "merienda", "cena", "tentempie")
DAILY_WATER_LITERS = 3.0
DAILY_WATER_PRICE = 1.25


class MealService:
    """Daily food intake registration and queries."""

    @staticmethod
    def _parse_date(value: str) -> datetime:
        try:
            parsed = datetime.strptime(value, "%d-%m-%Y")
        except (TypeError, ValueError) as exc:
            raise ValidationError(f"invalid date '{value}' (expected DD-MM-YYYY)") from exc
        if parsed.strftime("%d-%m-%Y") != value:
            raise ValidationError(f"invalid date '{value}' (expected DD-MM-YYYY)")
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
            meal_type=getattr(row, "meal_type", "tentempie") or "tentempie",
            created_at=str(row.created_at) if row.created_at is not None else None,
        )

    @staticmethod
    def _ensure_item(item_type: str, item_id: int, unit: str):
        """Create item as provisional if it does not exist."""
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
        """Calculate macros and price for an entry (recipe = multiplier)."""
        if row.item_type == "ingredient":
            item = IngredientModel.get_by_id(row.item_id)
            if item is None:
                item = IngredientModel.create(
                    name=f"provisional-{row.item_id}", unit=row.unit, provisional=True
                )
            res = calc_ingredient_macros(item, row.quantity)
            res["name"] = item.name
            res["is_supplement"] = bool(getattr(item, "is_supplement", False))
            return res
        item = RecipeModel.get_by_id(row.item_id)
        if item is None:
            return {
                **{key: 0.0 for key in MACRO_KEYS},
                "price": 0.0,
                "name": f"recipe-{row.item_id}",
                "is_supplement": False,
            }
        res = {
            key: round((getattr(item, key) or 0.0) * row.quantity, 2)
            for key in MACRO_KEYS
        } | {"price": round((item.price or 0.0) * row.quantity, 2)}
        res["name"] = item.name
        res["is_supplement"] = False
        return res

    def register(self, entry: MealEntry) -> MealEntry:
        """Register a meal entry. Creates provisional item if missing."""
        self._parse_date(entry.date)
        if entry.item_type not in ITEM_TYPES:
            raise ValidationError(f"invalid item_type '{entry.item_type}'")

        meal_type = (entry.meal_type or "tentempie").lower().strip()
        if meal_type == "tentempié":
            meal_type = "tentempie"
        if meal_type not in ALLOWED_MEAL_TYPES:
            raise ValidationError(
                f"invalid meal_type '{entry.meal_type}', must be one of {ALLOWED_MEAL_TYPES}"
            )
        entry.meal_type = meal_type

        with MealEntryModel._meta.database.atomic():
            self._ensure_item(entry.item_type, entry.item_id, entry.unit)
            row = MealEntryModel.create(
                date=entry.date,
                item_type=entry.item_type,
                item_id=entry.item_id,
                quantity=entry.quantity,
                unit=entry.unit,
                meal_type=entry.meal_type,
            )
        return self._to_domain(row)

    def get_day_entries(self, date: str) -> list:
        """Return all entries for a given date with computed macros."""
        self._parse_date(date)
        rows = MealEntryModel.select().where(MealEntryModel.date == date)
        rows = rows.order_by(MealEntryModel.id)
        meals = []
        for row in rows:
            item = self._to_domain(row)
            macros = self._entry_macros(row)
            meals.append({"entry": asdict(item), "meal_type": item.meal_type, **macros})
        return meals

    def get_day_summary(self, date: str) -> dict:
        """Day summary: consumed, goal, remaining, spend, individual meals, meals by type, and water/supplements."""
        meals = self.get_day_entries(date)
        consumed = {
            key: round(sum(m[key] for m in meals), 2) for key in MACRO_KEYS
        }
        spend = round(sum(m["price"] for m in meals) + DAILY_WATER_PRICE, 2)

        # Categorize regular meals by meal_type (excluding supplements)
        meals_by_type = {
            mt: {
                "meals": [],
                "kcal": 0.0,
                "protein": 0.0,
                "carbs": 0.0,
                "fat": 0.0,
                "spend": 0.0,
            }
            for mt in ALLOWED_MEAL_TYPES
        }
        supplement_meals = []
        for m in meals:
            if m.get("is_supplement"):
                supplement_meals.append(m)
                continue
            mt = m.get("meal_type") or m["entry"].get("meal_type", "tentempie")
            if mt not in meals_by_type:
                meals_by_type[mt] = {
                    "meals": [],
                    "kcal": 0.0,
                    "protein": 0.0,
                    "carbs": 0.0,
                    "fat": 0.0,
                    "spend": 0.0,
                }
            meals_by_type[mt]["meals"].append(m)
            for key in MACRO_KEYS:
                meals_by_type[mt][key] = round(meals_by_type[mt][key] + m[key], 2)
            meals_by_type[mt]["spend"] = round(meals_by_type[mt]["spend"] + m.get("price", 0.0), 2)

        water_and_supplements = {
            "water": {
                "name": "Agua (3L)",
                "quantity": DAILY_WATER_LITERS,
                "unit": "L",
                "price": DAILY_WATER_PRICE,
                "kcal": 0.0,
                "protein": 0.0,
                "carbs": 0.0,
                "fat": 0.0,
            },
            "supplements": supplement_meals,
            "kcal": round(sum(m["kcal"] for m in supplement_meals), 2),
            "protein": round(sum(m["protein"] for m in supplement_meals), 2),
            "carbs": round(sum(m["carbs"] for m in supplement_meals), 2),
            "fat": round(sum(m["fat"] for m in supplement_meals), 2),
            "spend": round(
                DAILY_WATER_PRICE + sum(m.get("price", 0.0) for m in supplement_meals), 2
            ),
        }

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
            "meals_by_type": meals_by_type,
            "water_and_supplements": water_and_supplements,
        }

    def update(self, entry_id: int, **fields) -> MealEntry:
        """Update fields of a meal entry (date, item_type, item_id, quantity, unit)."""
        row = MealEntryModel.get_or_none(MealEntryModel.id == entry_id)
        if row is None:
            raise NotFoundError(f"meal entry {entry_id} not found")
        if "date" in fields:
            self._parse_date(fields["date"])
        if "item_type" in fields and fields["item_type"] not in ITEM_TYPES:
            raise ValidationError(f"invalid item_type '{fields['item_type']}'")
        for field, value in fields.items():
            setattr(row, field, value)
        row.save()
        return self._to_domain(row)

    def delete(self, entry_id: int) -> None:
        """Delete a meal entry."""
        row = MealEntryModel.get_or_none(MealEntryModel.id == entry_id)
        if row is None:
            raise NotFoundError(f"meal entry {entry_id} not found")
        row.delete_instance()
