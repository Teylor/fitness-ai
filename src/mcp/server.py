"""MCP server setup and tool registration."""

from mcp.server.mcpserver import MCPServer

from src.mcp.tools.goal_tools import get_daily_goal, set_daily_goal
from src.mcp.tools.ingredient_tools import (
    create_ingredient,
    delete_ingredient,
    list_ingredients,
    update_ingredient,
)
from src.mcp.tools.meal_tools import get_day_summary, register_meal
from src.mcp.tools.recipe_tools import (
    create_recipe,
    delete_recipe,
    list_recipes,
    update_recipe,
)


def create_server() -> MCPServer:
    """Create and configure the MCPServer instance with active nutrition and goal tools."""
    server = MCPServer("fitness-ai")

    # Ingredient tools (4)
    server.add_tool(create_ingredient, name="create_ingredient")
    server.add_tool(update_ingredient, name="update_ingredient")
    server.add_tool(delete_ingredient, name="delete_ingredient")
    server.add_tool(list_ingredients, name="list_ingredients")

    # Recipe tools (4)
    server.add_tool(create_recipe, name="create_recipe")
    server.add_tool(update_recipe, name="update_recipe")
    server.add_tool(delete_recipe, name="delete_recipe")
    server.add_tool(list_recipes, name="list_recipes")

    # Meal tools (2)
    server.add_tool(register_meal, name="register_meal")
    server.add_tool(get_day_summary, name="get_day_summary")

    # Goal tools (2)
    server.add_tool(set_daily_goal, name="set_daily_goal")
    server.add_tool(get_daily_goal, name="get_daily_goal")

    return server
