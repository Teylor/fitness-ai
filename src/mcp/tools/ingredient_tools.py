"""MCP tools: Ingredient domain operations."""

from dataclasses import asdict
from typing import Optional

from src.models.ingredient import Ingredient
from src.services.ingredient_service import IngredientService
from src.utils.errors import DuplicateError, ToolError


def create_ingredient(
    name: str,
    unit: str,
    kcal: float = 0,
    protein: float = 0,
    carbs: float = 0,
    fat: float = 0,
    price: float = 0,
    provisional: bool = False,
) -> dict:
    """Create a new ingredient or return the existing one if duplicate (idempotent)."""
    service = IngredientService()
    try:
        created = service.create(
            Ingredient(
                name=name,
                unit=unit,
                kcal=kcal,
                protein=protein,
                carbs=carbs,
                fat=fat,
                price=price,
                provisional=provisional,
            )
        )
        return {"status": "ok", "ingredient": asdict(created)}
    except DuplicateError:
        existing = service.find_by_name(name)
        if existing is not None:
            return {"status": "ok", "ingredient": asdict(existing)}
        return {"status": "error", "code": "duplicate", "message": f"duplicate ingredient '{name}'"}
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


def update_ingredient(
    ingredient_id: int,
    name: str = None,
    unit: str = None,
    kcal: float = None,
    protein: float = None,
    carbs: float = None,
    fat: float = None,
    price: float = None,
    provisional: bool = None,
) -> dict:
    """Update fields on an existing ingredient."""
    service = IngredientService()
    fields = {}
    if name is not None:
        fields["name"] = name
    if unit is not None:
        fields["unit"] = unit
    if kcal is not None:
        fields["kcal"] = kcal
    if protein is not None:
        fields["protein"] = protein
    if carbs is not None:
        fields["carbs"] = carbs
    if fat is not None:
        fields["fat"] = fat
    if price is not None:
        fields["price"] = price
    if provisional is not None:
        fields["provisional"] = provisional

    try:
        updated = service.update(ingredient_id, **fields)
        return {"status": "ok", "ingredient": asdict(updated)}
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


def delete_ingredient(ingredient_id: int) -> dict:
    """Delete an ingredient and its associated meal entries."""
    service = IngredientService()
    try:
        deleted_count = service.delete(ingredient_id)
        return {
            "status": "ok",
            "ingredient_id": ingredient_id,
            "deleted_entries": deleted_count,
        }
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


def list_ingredients(
    search: str = None,
    provisional_only: bool = False,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """List or search ingredients with optional pagination."""
    service = IngredientService()
    try:
        items = service.list(
            search=search,
            provisional_only=provisional_only,
            limit=limit,
            offset=offset,
        )
        return {
            "status": "ok",
            "ingredients": [asdict(item) for item in items],
            "count": len(items),
        }
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}
