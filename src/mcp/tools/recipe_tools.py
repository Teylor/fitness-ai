"""MCP tools: Recipe domain operations."""

from dataclasses import asdict
from typing import List, Optional

from src.models.ingredient import Ingredient
from src.models.recipe import Recipe, RecipeItem
from src.services.ingredient_service import IngredientService
from src.services.recipe_service import RecipeService
from src.utils.errors import DuplicateError, ToolError, ValidationError


def _parse_recipe_items(items_data: Optional[List[dict]]) -> Optional[List[RecipeItem]]:
    if items_data is None:
        return None
    ingredient_service = IngredientService()
    parsed_items: List[RecipeItem] = []
    for item in items_data:
        ing_id = item.get("ingredient_id")
        unit = item.get("unit", "gr")
        quantity = float(item["quantity"])
        if ing_id is None:
            name = item.get("name")
            if not name:
                raise ValidationError("recipe ingredient item must specify name or ingredient_id")
            existing = ingredient_service.find_by_name(name)
            if existing is None:
                created = ingredient_service.create(
                    Ingredient(name=name, unit=unit, provisional=True)
                )
                ing_id = created.id
            else:
                ing_id = existing.id
                if "unit" not in item:
                    unit = existing.unit
        parsed_items.append(
            RecipeItem(ingredient_id=ing_id, quantity=quantity, unit=unit)
        )
    return parsed_items


def create_recipe(
    name: str,
    ingredients: List[dict] = None,
    price: float = None,
    kcal: float = None,
    protein: float = None,
    carbs: float = None,
    fat: float = None,
    provisional: bool = False,
) -> dict:
    """Create a new recipe (compound with ingredients or opaque with direct macros/price)."""
    service = RecipeService()
    try:
        parsed_items = _parse_recipe_items(ingredients)
        created = service.create(
            Recipe(
                name=name,
                price=price,
                kcal=kcal,
                protein=protein,
                carbs=carbs,
                fat=fat,
                provisional=provisional,
            ),
            items=parsed_items,
        )
        return {"status": "ok", "recipe": asdict(created)}
    except DuplicateError:
        existing = service.find_by_name(name)
        if existing is not None:
            return {"status": "ok", "recipe": asdict(existing)}
        return {"status": "error", "code": "duplicate", "message": f"duplicate recipe '{name}'"}
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


def update_recipe(
    recipe_id: int,
    name: str = None,
    price: float = None,
    kcal: float = None,
    protein: float = None,
    carbs: float = None,
    fat: float = None,
    provisional: bool = None,
    ingredients: List[dict] = None,
) -> dict:
    """Update fields and ingredients of an existing recipe."""
    service = RecipeService()
    fields = {}
    if name is not None:
        fields["name"] = name
    if price is not None:
        fields["price"] = price
    if kcal is not None:
        fields["kcal"] = kcal
    if protein is not None:
        fields["protein"] = protein
    if carbs is not None:
        fields["carbs"] = carbs
    if fat is not None:
        fields["fat"] = fat
    if provisional is not None:
        fields["provisional"] = provisional

    try:
        if ingredients is not None:
            fields["items"] = _parse_recipe_items(ingredients)
        updated = service.update(recipe_id, **fields)
        return {"status": "ok", "recipe": asdict(updated)}
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


def delete_recipe(recipe_id: int) -> dict:
    """Delete a recipe, its items, and referencing meal entries."""
    service = RecipeService()
    try:
        deleted_count = service.delete(recipe_id)
        return {
            "status": "ok",
            "recipe_id": recipe_id,
            "deleted_entries": deleted_count,
        }
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


def list_recipes(
    search: str = None,
    provisional_only: bool = False,
    type: str = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """List or search recipes with optional type filtering and pagination."""
    service = RecipeService()
    try:
        items = service.list(
            search=search,
            provisional_only=provisional_only,
            type=type,
            limit=limit,
            offset=offset,
        )
        return {
            "status": "ok",
            "recipes": [asdict(item) for item in items],
            "count": len(items),
        }
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}
