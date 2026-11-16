"""Meal registration domain service."""

from dataclasses import asdict
from datetime import datetime
from typing import Optional

from src.db.models import (
    DailyCreatine as DailyCreatineModel,
    DailySupplementToggle as DailySupplementToggleModel,
    Ingredient as IngredientModel,
    MealEntry as MealEntryModel,
    Recipe as RecipeModel,
)
from src.models.meal_entry import MealEntry
from src.services.goal_service import GoalService
from src.utils.errors import NotFoundError, ValidationError
from src.utils.fuzzy import normalize
from src.utils.macros import calc_ingredient_macros

ITEM_TYPES = ("ingredient", "recipe")
MACRO_KEYS = ("kcal", "protein", "carbs", "fat")
ALLOWED_MEAL_TYPES = ("desayuno", "comida", "merienda", "cena", "tentempie")
DAILY_WATER_LITERS = 3.0
DAILY_WATER_PRICE = 1.25
DAILY_CREATINE_NAME = "Creatina (5g)"
DAILY_CREATINE_QUANTITY = 1.0
DAILY_CREATINE_UNIT = "u"
DAILY_CREATINE_GRAMS = 5.0
DAILY_CREATINE_PRICE = 0.30


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

    def is_daily_creatine_enabled(self, date: str) -> bool:
        """Return whether daily creatine is enabled for date (defaults to True)."""
        self._parse_date(date)
        row = DailyCreatineModel.get_or_none(DailyCreatineModel.date == date)
        return True if row is None else bool(row.enabled)

    def toggle_daily_creatine(
        self, date: str, enabled: Optional[bool] = None
    ) -> bool:
        """Enable/disable or flip daily creatine for a given DD-MM-YYYY date."""
        self._parse_date(date)
        with DailyCreatineModel._meta.database.atomic():
            row = DailyCreatineModel.get_or_none(DailyCreatineModel.date == date)
            current = True if row is None else bool(row.enabled)
            target = (not current) if enabled is None else bool(enabled)
            if row is None:
                DailyCreatineModel.create(date=date, enabled=target)
            else:
                row.enabled = target
                row.updated_at = datetime.now()
                row.save()
        return target

    def toggle_daily_supplement(
        self, date: str, ingredient_id: int, enabled: Optional[bool] = None
    ) -> bool:
        """Enable/disable or flip a catalog supplement for a DD-MM-YYYY date (default OFF)."""
        self._parse_date(date)
        ing = IngredientModel.get_or_none(IngredientModel.id == int(ingredient_id))
        if ing is None:
            raise NotFoundError(f"ingredient {ingredient_id} not found")
        if not ing.is_supplement:
            raise ValidationError(f"ingredient '{ing.name}' is not a supplement")
        if normalize(ing.name) == "creatina":
            return self.toggle_daily_creatine(date=date, enabled=enabled)
        with DailySupplementToggleModel._meta.database.atomic():
            row = DailySupplementToggleModel.get_or_none(
                (DailySupplementToggleModel.date == date)
                & (DailySupplementToggleModel.ingredient == ing.id)
            )
            current = False if row is None else bool(row.enabled)
            target = (not current) if enabled is None else bool(enabled)
            if row is None:
                DailySupplementToggleModel.create(
                    date=date, ingredient=ing.id, enabled=target
                )
            else:
                row.enabled = target
                row.updated_at = datetime.now()
                row.save()
        return target

    @staticmethod
    def resolve_daily_creatine() -> dict:
        """Resolve daily creatine from catalog ('Creatina') or default 1 u (5g) @ 0.30€."""
        match = None
        for cand in IngredientModel.select():
            if normalize(cand.name) == "creatina":
                match = cand
                break
        if match is not None:
            qty = 1.0 if match.unit == "u" else DAILY_CREATINE_GRAMS
            macros = calc_ingredient_macros(match, qty)
            return {
                "name": match.name,
                "quantity": qty,
                "unit": match.unit,
                "price": macros["price"],
                "kcal": macros["kcal"],
                "protein": macros["protein"],
                "carbs": macros["carbs"],
                "fat": macros["fat"],
                "from_catalog": True,
            }
        return {
            "name": DAILY_CREATINE_NAME,
            "quantity": DAILY_CREATINE_QUANTITY,
            "unit": DAILY_CREATINE_UNIT,
            "price": DAILY_CREATINE_PRICE,
            "kcal": 0.0,
            "protein": 0.0,
            "carbs": 0.0,
            "fat": 0.0,
            "from_catalog": False,
        }

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

        creatine_enabled = self.is_daily_creatine_enabled(date)
        creatine_already_logged = any(
            normalize(m.get("name", "")) == "creatina" for m in supplement_meals
        )
        creatine_info = self.resolve_daily_creatine()
        creatine_active = creatine_enabled and not creatine_already_logged
        if creatine_active:
            for key in MACRO_KEYS:
                consumed[key] = round(consumed[key] + creatine_info[key], 2)
            spend = round(spend + creatine_info["price"], 2)

        creatine_payload = {
            **creatine_info,
            "enabled": creatine_enabled,
            "already_logged": creatine_already_logged,
        }
        creatine_kcal = creatine_info["kcal"] if creatine_active else 0.0
        creatine_protein = creatine_info["protein"] if creatine_active else 0.0
        creatine_carbs = creatine_info["carbs"] if creatine_active else 0.0
        creatine_fat = creatine_info["fat"] if creatine_active else 0.0
        creatine_spend = creatine_info["price"] if creatine_active else 0.0

        toggles_by_ing = {
            row.ingredient_id: bool(row.enabled)
            for row in DailySupplementToggleModel.select().where(
                DailySupplementToggleModel.date == date
            )
        }
        logged_ing_ids = {
            m["entry"].get("item_id")
            for m in supplement_meals
            if m.get("entry", {}).get("item_type") == "ingredient"
        }
        daily_supplements = []
        ds_kcal = 0.0
        ds_protein = 0.0
        ds_carbs = 0.0
        ds_fat = 0.0
        ds_spend = 0.0
        for ing in (
            IngredientModel.select()
            .where(IngredientModel.is_supplement == True)  # noqa: E712
            .order_by(IngredientModel.id)
        ):
            if normalize(ing.name) == "creatina":
                continue
            qty = 1.0 if ing.unit == "u" else 100.0
            macros = calc_ingredient_macros(ing, qty)
            enabled = toggles_by_ing.get(ing.id, False)
            already_logged = ing.id in logged_ing_ids
            active = enabled and not already_logged
            if active:
                for key in MACRO_KEYS:
                    consumed[key] = round(consumed[key] + macros[key], 2)
                spend = round(spend + macros["price"], 2)
                ds_kcal = round(ds_kcal + macros["kcal"], 2)
                ds_protein = round(ds_protein + macros["protein"], 2)
                ds_carbs = round(ds_carbs + macros["carbs"], 2)
                ds_fat = round(ds_fat + macros["fat"], 2)
                ds_spend = round(ds_spend + macros["price"], 2)
            daily_supplements.append(
                {
                    "ingredient_id": ing.id,
                    "name": ing.name,
                    "quantity": qty,
                    "unit": ing.unit,
                    "price": macros["price"],
                    "kcal": macros["kcal"],
                    "protein": macros["protein"],
                    "carbs": macros["carbs"],
                    "fat": macros["fat"],
                    "enabled": enabled,
                    "already_logged": already_logged,
                }
            )

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
            "creatine": creatine_payload,
            "daily_supplements": daily_supplements,
            "supplements": supplement_meals,
            "kcal": round(
                sum(m["kcal"] for m in supplement_meals) + creatine_kcal + ds_kcal, 2
            ),
            "protein": round(
                sum(m["protein"] for m in supplement_meals)
                + creatine_protein
                + ds_protein,
                2,
            ),
            "carbs": round(
                sum(m["carbs"] for m in supplement_meals) + creatine_carbs + ds_carbs, 2
            ),
            "fat": round(
                sum(m["fat"] for m in supplement_meals) + creatine_fat + ds_fat, 2
            ),
            "spend": round(
                DAILY_WATER_PRICE
                + creatine_spend
                + ds_spend
                + sum(m.get("price", 0.0) for m in supplement_meals),
                2,
            ),
        }

        goal_service = GoalService()
        goal_row = goal_service.get_goal(date)
        goal = {
            "date": goal_row.date,
            "kcal": goal_row.kcal,
            "protein": goal_row.protein,
            "carbs": goal_row.carbs,
            "fat": goal_row.fat,
            "is_day_off": goal_row.is_day_off,
        }
        remaining = {key: round(goal[key] - consumed[key], 2) for key in MACRO_KEYS}
        return {
            "consumed": consumed,
            "spend": spend,
            "goal": goal,
            "goal_profiles": goal_service.get_goal_profiles(),
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
