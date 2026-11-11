"""Ingredient Service (CRUD + search + fuzzy)."""

from typing import List, Optional

from src.db.models import Ingredient as IngredientModel, MealEntry, RecipeItem
from src.models.ingredient import Ingredient
from src.utils.errors import ConflictError, DuplicateError, NotFoundError, ValidationError
from src.utils.fuzzy import fuzzy_match, normalize

VALID_UNITS = ("gr", "ml", "u")


class IngredientService:
    """Ingredient CRUD over the database layer."""

    def create(self, ingredient: Ingredient) -> Ingredient:
        """Create an ingredient. Raises ValidationError on invalid unit, DuplicateError if (name, unit) exists."""
        if ingredient.unit not in VALID_UNITS:
            raise ValidationError(f"invalid unit '{ingredient.unit}' (expected gr/ml/u)")
        if self._normalized_exists(ingredient.name, ingredient.unit):
            raise DuplicateError(f"duplicate ingredient '{ingredient.name}' ({ingredient.unit})")
        row = IngredientModel.create(
            name=ingredient.name,
            unit=ingredient.unit,
            kcal=ingredient.kcal or 0,
            protein=ingredient.protein or 0,
            carbs=ingredient.carbs or 0,
            fat=ingredient.fat or 0,
            price=ingredient.price or 0,
            is_supplement=bool(ingredient.is_supplement),
            provisional=ingredient.provisional,
        )
        return self._to_domain(row)

    def get_by_id(self, ingredient_id: int) -> Optional[Ingredient]:
        """Return the ingredient or None if it does not exist."""
        row = IngredientModel.get_or_none(IngredientModel.id == ingredient_id)
        return None if row is None else self._to_domain(row)

    def find_by_name(self, name: str) -> Optional[Ingredient]:
        """Find by name: exact (normalized) match first, then fuzzy."""
        q = normalize(name)
        row = None
        for candidate in IngredientModel.select():
            if normalize(candidate.name) == q:
                row = candidate
                break
        if row is None:
            match = fuzzy_match(name, [r.name for r in IngredientModel.select()])
            if match is not None:
                row = IngredientModel.get_or_none(IngredientModel.name == match)
        return None if row is None else self._to_domain(row)

    def update(self, ingredient_id: int, **fields) -> Ingredient:
        """Update fields. Raises NotFoundError, ValidationError on invalid unit, or DuplicateError."""
        row = IngredientModel.get_or_none(IngredientModel.id == ingredient_id)
        if row is None:
            raise NotFoundError(f"ingredient {ingredient_id} not found")
        new_name = fields.get("name", row.name)
        new_unit = fields.get("unit", row.unit)
        if new_unit not in VALID_UNITS:
            raise ValidationError(f"invalid unit '{new_unit}' (expected gr/ml/u)")
        if self._normalized_exists(new_name, new_unit, exclude_id=ingredient_id):
            raise DuplicateError(f"duplicate ingredient '{new_name}' ({new_unit})")
        for field, value in fields.items():
            setattr(row, field, value)
        row.save()
        return self._to_domain(row)

    def delete(self, ingredient_id: int) -> int:
        """Delete ingredient and its meal entries; returns count of deleted entries.

        Raises NotFoundError if not found, or ConflictError if used in a recipe (RESTRICT).
        """
        row = IngredientModel.get_or_none(IngredientModel.id == ingredient_id)
        if row is None:
            raise NotFoundError(f"ingredient {ingredient_id} not found")
        in_use = RecipeItem.select().where(RecipeItem.ingredient == ingredient_id).count()
        if in_use:
            raise ConflictError(
                f"ingredient '{row.name}' is used by {in_use} recipe(s); delete them first"
            )
        with IngredientModel._meta.database.atomic():
            deleted = MealEntry.delete().where(
                (MealEntry.item_type == "ingredient") & (MealEntry.item_id == ingredient_id)
            ).execute()
            row.delete_instance()
        return deleted

    def list(
        self,
        search: Optional[str] = None,
        provisional_only: bool = False,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Ingredient]:
        """List ingredients with optional search filter and pagination."""
        rows = list(IngredientModel.select().order_by(IngredientModel.id))
        if search:
            q = normalize(search)
            rows = [r for r in rows if q in normalize(r.name)]
        if provisional_only:
            rows = [r for r in rows if r.provisional]
        return [self._to_domain(r) for r in rows[offset : offset + limit]]

    @staticmethod
    def _normalized_exists(name: str, unit: str, exclude_id: Optional[int] = None) -> bool:
        rows = IngredientModel.select()
        if exclude_id is not None:
            rows = rows.where(IngredientModel.id != exclude_id)
        return any(
            r.unit == unit and normalize(r.name) == normalize(name) for r in rows
        )

    @staticmethod
    def _to_domain(row) -> Ingredient:
        return Ingredient(
            id=row.id,
            name=row.name,
            unit=row.unit,
            kcal=row.kcal,
            protein=row.protein,
            carbs=row.carbs,
            fat=row.fat,
            price=row.price,
            is_supplement=bool(getattr(row, "is_supplement", False)),
            provisional=row.provisional,
            created_at=str(row.created_at) if row.created_at is not None else None,
            updated_at=str(row.updated_at) if row.updated_at is not None else None,
        )
