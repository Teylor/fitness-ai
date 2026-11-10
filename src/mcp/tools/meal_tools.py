"""MCP tools: Meal registration and daily summary operations."""

from datetime import datetime
from typing import Optional

from src.db.models import MealEntry as MealEntryModel
from src.models.ingredient import Ingredient
from src.models.meal_entry import MealEntry
from src.models.recipe import Recipe
from src.services.ingredient_service import IngredientService
from src.services.meal_service import MealService
from src.services.recipe_service import RecipeService
from src.utils.errors import ToolError


def register_meal(
    item_name: str,
    quantity: float,
    unit: str,
    item_type: Optional[str] = None,
    date: Optional[str] = None,
) -> dict:
    """Register a food intake; auto-creates provisional item if missing."""
    meal_service = MealService()
    ingredient_service = IngredientService()
    recipe_service = RecipeService()

    if not date:
        date = datetime.now().strftime("%d-%m-%Y")

    try:
        resolved_type = item_type
        item_id = None

        if resolved_type == "ingredient":
            ing = ingredient_service.find_by_name(item_name)
            if ing is None:
                ing = ingredient_service.create(
                    Ingredient(name=item_name, unit=unit, provisional=True)
                )
            item_id = ing.id
        elif resolved_type == "recipe":
            rec = recipe_service.find_by_name(item_name)
            if rec is None:
                rec = recipe_service.create(
                    Recipe(name=item_name, provisional=True)
                )
            item_id = rec.id
        else:
            # item_type is None -> search both, fallback to provisional ingredient
            ing = ingredient_service.find_by_name(item_name)
            if ing is not None:
                resolved_type = "ingredient"
                item_id = ing.id
            else:
                rec = recipe_service.find_by_name(item_name)
                if rec is not None:
                    resolved_type = "recipe"
                    item_id = rec.id
                else:
                    ing = ingredient_service.create(
                        Ingredient(name=item_name, unit=unit, provisional=True)
                    )
                    resolved_type = "ingredient"
                    item_id = ing.id

        entry = meal_service.register(
            MealEntry(
                date=date,
                item_type=resolved_type,
                item_id=item_id,
                quantity=quantity,
                unit=unit,
            )
        )

        entry_row = MealEntryModel.get_by_id(entry.id)
        macros_full = meal_service._entry_macros(entry_row)
        macros = {
            k: macros_full.get(k, 0.0) for k in ("kcal", "protein", "carbs", "fat")
        }
        price = macros_full.get("price", 0.0)

        try:
            day_summary = meal_service.get_day_summary(date)
        except Exception:
            day_summary = None

        # Auto-sync with Google Health if credentials exist
        gh_synced = False
        try:
            from src.config import settings
            if settings.google_health_token or settings.google_health_refresh_token:
                from src.services.google_health_service import GoogleHealthService
                gh_svc = GoogleHealthService()
                gh_res = gh_svc.sync_meals(date)
                gh_synced = gh_res.get("status") == "ok"
        except Exception:
            gh_synced = False

        return {
            "status": "ok",
            "entry_id": entry.id,
            "macros": macros,
            "price": price,
            "day_summary": day_summary,
            "google_health_synced": gh_synced,
        }
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


def get_day_summary(date: Optional[str] = None) -> dict:
    """Retrieve full day nutrition summary: consumed macros, spend, goal, and remaining."""
    meal_service = MealService()
    if not date:
        date = datetime.now().strftime("%d-%m-%Y")
    try:
        summary = meal_service.get_day_summary(date)
        return {"status": "ok", **summary}
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


def delete_meal(entry_id: int) -> dict:
    """Delete a registered meal entry by ID and auto-sync with Google Health."""
    meal_service = MealService()
    try:
        entry_row = MealEntryModel.get_or_none(MealEntryModel.id == int(entry_id))
        entry_date = entry_row.date if entry_row else None

        meal_service.delete(int(entry_id))

        gh_synced = False
        if entry_date:
            try:
                from src.config import settings
                if settings.google_health_token or settings.google_health_refresh_token:
                    from src.services.google_health_service import GoogleHealthService
                    gh_svc = GoogleHealthService()
                    gh_res = gh_svc.sync_meals(entry_date)
                    gh_synced = gh_res.get("status") == "ok"
            except Exception:
                gh_synced = False

        return {
            "status": "ok",
            "entry_id": int(entry_id),
            "google_health_synced": gh_synced,
        }
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}

