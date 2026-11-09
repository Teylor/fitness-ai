"""Macro and price calculation utilities."""


def calc_ingredient_macros(ingredient, quantity: float) -> dict:
    """Calculate macros for a quantity of an ingredient.

    Args:
        ingredient: Ingredient object (values per base unit).
        quantity: Consumed quantity (in ingredient's unit).

    Returns:
        {"kcal": float, "protein": float, "carbs": float, "fat": float, "price": float}
    """
    unit = ingredient.unit
    scale = quantity if unit == 'u' else quantity / 100.0
    price_scale = quantity if unit == 'u' else quantity / 1000.0
    return {
        'kcal': round(ingredient.kcal * scale, 2),
        'protein': round(ingredient.protein * scale, 2),
        'carbs': round(ingredient.carbs * scale, 2),
        'fat': round(ingredient.fat * scale, 2),
        'price': round(ingredient.price * price_scale, 2),
    }


def calc_recipe_macros(recipe_items: list, ingredients: dict) -> dict:
    """Calculate total macros of a composite recipe.

    Args:
        recipe_items: List of RecipeItem instances.
        ingredients: Dict {ingredient_id: Ingredient}.

    Returns:
        {"kcal": float, "protein": float, "carbs": float, "fat": float, "price": float}
    """
    totals = {'kcal': 0.0, 'protein': 0.0, 'carbs': 0.0, 'fat': 0.0, 'price': 0.0}
    for item in recipe_items:
        part = calc_ingredient_macros(ingredients[item.ingredient_id], item.quantity)
        for key, val in part.items():
            totals[key] += val
    return {key: round(val, 2) for key, val in totals.items()}


def estimate_1rm(weight: float, reps: int) -> float:
    """Epley formula: weight × (1 + reps/30)."""
    return round(weight * (1 + reps / 30.0), 2)
