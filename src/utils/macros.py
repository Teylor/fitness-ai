"""Cálculo de macros y precios."""


def calc_ingredient_macros(ingredient, quantity: float) -> dict:
    """Calcula macros para una cantidad de ingrediente.

    Args:
        ingredient: Objeto Ingredient (valores por unidad base).
        quantity: Cantidad consumida (en la unidad del ingrediente).

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
    """Calcula macros totales de una receta compuesta.

    Args:
        recipe_items: Lista de RecipeItem.
        ingredients: Dict {ingredient_id: Ingredient}.

    Returns:
        {"kcal": float, "protein": float, "carbs": float, "fat": float, "price": float}
    """
    ...


def estimate_1rm(weight: float, reps: int) -> float:
    """Fórmula de Epley: weight × (1 + reps/30)."""
    ...