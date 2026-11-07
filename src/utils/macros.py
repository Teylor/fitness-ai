"""Cálculo de macros y precios."""


def calc_ingredient_macros(ingredient, quantity: float) -> dict:
    """Calcula macros para una cantidad de ingrediente.

    Args:
        ingredient: Objeto Ingredient (valores por unidad base).
        quantity: Cantidad consumida (en la unidad del ingrediente).

    Returns:
        {"kcal": float, "protein": float, "carbs": float, "fat": float, "price": float}
    """
    ...


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