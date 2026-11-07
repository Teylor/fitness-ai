"""Setup del MCP Server."""

from src.config import settings


def create_server():
    """Crea y configura el MCP server con todas las tools registradas."""
    from mcp.server import Server  # or whatever MCP Python SDK

    server = Server("fitness-ai")

    # Registrar tools
    from src.mcp.tools.meal_tools import register_meal, get_day_summary
    from src.mcp.tools.ingredient_tools import (
        create_ingredient, update_ingredient,
        delete_ingredient, list_ingredients,
    )
    from src.mcp.tools.recipe_tools import (
        create_recipe, update_recipe,
        delete_recipe, list_recipes,
    )
    from src.mcp.tools.goal_tools import set_daily_goal, get_daily_goal
    from src.mcp.tools.workout_tools import (
        register_workout, get_last_workout,
        get_personal_record, get_workouts_by_day,
    )
    from src.mcp.tools.exercise_tools import list_exercises, create_exercise

    # Aquí se registran cada tool con su schema
    # (depende del SDK MCP usado)

    return server