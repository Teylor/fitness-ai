"""Recipe Service (CRUD + macro calculation)."""

from typing import List, Optional

from src.db.models import (
    Ingredient as IngredientModel,
    MealEntry,
    Recipe as RecipeModel,
    RecipeItem as RecipeItemModel,
)
from src.models.recipe import Recipe, RecipeItem
from src.utils.fuzzy import fuzzy_match, normalize
from src.utils.macros import calc_recipe_macros


class RecipeService:
    """CRUD + cálculo de macros para recetas."""

    def create(self, recipe: Recipe, items: Optional[List[RecipeItem]] = None) -> Recipe:
        """Crea receta. Si tiene items → calcula macros. Si no → usa precio directo."""
        if self._name_exists(recipe.name):
            raise ValueError(f"duplicate recipe '{recipe.name}'")
        with RecipeModel._meta.database.atomic():
            row = RecipeModel.create(
                name=recipe.name,
                price=recipe.price,
                kcal=recipe.kcal,
                protein=recipe.protein,
                carbs=recipe.carbs,
                fat=recipe.fat,
                provisional=recipe.provisional,
            )
            if items:
                for item in items:
                    RecipeItemModel.create(
                        recipe=row,
                        ingredient=item.ingredient_id,
                        quantity=item.quantity,
                        unit=item.unit,
                    )
                row = self._recompute(row)
        return self._to_domain(row)

    @staticmethod
    def _name_exists(name: str, exclude_id: Optional[int] = None) -> bool:
        rows = RecipeModel.select()
        if exclude_id is not None:
            rows = rows.where(RecipeModel.id != exclude_id)
        return any(normalize(r.name) == normalize(name) for r in rows)

    def _recompute(self, row: RecipeModel) -> RecipeModel:
        items = list(RecipeItemModel.select().where(RecipeItemModel.recipe == row.id))
        if items:
            ingredients = {
                i.ingredient_id: IngredientModel.get_by_id(i.ingredient_id)
                for i in items
            }
            totals = calc_recipe_macros(items, ingredients)
            row.price = totals["price"]
            row.kcal = totals["kcal"]
            row.protein = totals["protein"]
            row.carbs = totals["carbs"]
            row.fat = totals["fat"]
            row.save()
        return row

    def get_by_id(self, recipe_id: int) -> Optional[Recipe]:
        row = RecipeModel.get_or_none(RecipeModel.id == recipe_id)
        return None if row is None else self._to_domain(row)

    def find_by_name(self, name: str) -> Optional[Recipe]:
        """Búsqueda fuzzy por nombre."""
        rows = list(RecipeModel.select())
        row = next((r for r in rows if normalize(r.name) == normalize(name)), None)
        if row is None:
            match = fuzzy_match(name, [r.name for r in rows])
            if match is not None:
                row = RecipeModel.get_or_none(RecipeModel.name == match)
        return None if row is None else self._to_domain(row)

    def update(self, recipe_id: int, **fields) -> Recipe:
        row = RecipeModel.get_or_none(RecipeModel.id == recipe_id)
        if row is None:
            raise ValueError(f"recipe {recipe_id} not found")
        new_name = fields.get("name", row.name)
        if normalize(new_name) != normalize(row.name):
            if self._name_exists(new_name, exclude_id=recipe_id):
                raise ValueError(f"duplicate recipe '{new_name}'")
        items = fields.pop("items", None)
        for field, value in fields.items():
            setattr(row, field, value)
        row.save()
        if items is not None:
            with RecipeModel._meta.database.atomic():
                RecipeItemModel.delete().where(
                    RecipeItemModel.recipe == row.id
                ).execute()
                for item in items:
                    RecipeItemModel.create(
                        recipe=row,
                        ingredient=item.ingredient_id,
                        quantity=item.quantity,
                        unit=item.unit,
                    )
                row = self._recompute(row)
        return self._to_domain(row)

    def delete(self, recipe_id: int) -> int:
        """Borra receta, sus items y sus meal entries. Devuelve nº de meals borradas."""
        row = RecipeModel.get_or_none(RecipeModel.id == recipe_id)
        if row is None:
            raise ValueError(f"recipe {recipe_id} not found")
        with RecipeModel._meta.database.atomic():
            deleted = MealEntry.delete().where(
                (MealEntry.item_type == "recipe") & (MealEntry.item_id == recipe_id)
            ).execute()
            row.delete_instance()
        return deleted

    def list(self, search: str = None, provisional_only: bool = False,
             type: str = None, limit: int = 50, offset: int = 0) -> List[Recipe]:
        rows = list(RecipeModel.select().order_by(RecipeModel.id))
        if search:
            q = normalize(search)
            rows = [r for r in rows if q in normalize(r.name)]
        if provisional_only:
            rows = [r for r in rows if r.provisional]
        if type in ("compound", "opaque"):
            counts = {
                r.id: RecipeItemModel.select().where(
                    RecipeItemModel.recipe == r.id
                ).count()
                for r in rows
            }
            rows = [
                r for r in rows
                if (counts[r.id] > 0) == (type == "compound")
            ]
        return [self._to_domain(r) for r in rows[offset : offset + limit]]

    def calculate_macros(self, recipe_id: int) -> dict:
        """Calcula kcal, P, C, G, price sumando recipe_items × ingredients."""
        row = RecipeModel.get_or_none(RecipeModel.id == recipe_id)
        if row is None:
            raise ValueError(f"recipe {recipe_id} not found")
        items = list(RecipeItemModel.select().where(
            RecipeItemModel.recipe == recipe_id
        ))
        if not items:
            return {
                "kcal": row.kcal,
                "protein": row.protein,
                "carbs": row.carbs,
                "fat": row.fat,
                "price": row.price,
            }
        ingredients = {
            i.ingredient_id: IngredientModel.get_by_id(i.ingredient_id)
            for i in items
        }
        return calc_recipe_macros(items, ingredients)

    def _to_domain(self, row) -> Recipe:
        items = [
            RecipeItem(
                id=i.id,
                recipe_id=i.recipe_id,
                ingredient_id=i.ingredient_id,
                quantity=i.quantity,
                unit=i.unit,
            )
            for i in RecipeItemModel.select().where(RecipeItemModel.recipe == row.id)
        ]
        return Recipe(
            id=row.id,
            name=row.name,
            price=row.price,
            kcal=row.kcal,
            protein=row.protein,
            carbs=row.carbs,
            fat=row.fat,
            provisional=row.provisional,
            created_at=str(row.created_at) if row.created_at is not None else None,
            updated_at=str(row.updated_at) if row.updated_at is not None else None,
            items=items,
        )