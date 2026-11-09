"""Integration tests: MCP Server setup and tool registration."""

from mcp.server.mcpserver import MCPServer

from src.config import settings
from src.mcp.server import create_server


EXPECTED_TOOLS = {
    "create_ingredient",
    "update_ingredient",
    "delete_ingredient",
    "list_ingredients",
    "create_recipe",
    "update_recipe",
    "delete_recipe",
    "list_recipes",
    "register_meal",
    "get_day_summary",
    "set_daily_goal",
    "get_daily_goal",
    "register_workout",
    "get_last_workout",
    "get_personal_record",
    "get_workouts_by_day",
    "list_exercises",
    "create_exercise",
    "get_ui_form",
    "sync_meals_to_google_health",
    "fetch_google_health_sleep",
    "fetch_google_health_weight",
    "sync_google_health",
}


def test_create_server_returns_configured_mcp_server():
    server = create_server()
    assert isinstance(server, MCPServer)
    assert server.name == "fitness-ai"


def test_server_registers_all_twenty_three_tools():
    server = create_server()
    tools = server._tool_manager.list_tools()
    tool_names = {t.name for t in tools}

    assert len(tools) == 23
    assert tool_names == EXPECTED_TOOLS


def test_streamable_http_app_exposes_mcp_and_ui_routes():
    server = create_server()
    app = server.streamable_http_app()
    route_paths = [r.path for r in app.routes]

    assert "/mcp" in route_paths
    assert "/ui" in route_paths
    assert "/ui/{form_type}" in route_paths
    assert "/api/{tool_name}" in route_paths


def test_registered_tools_have_descriptions_and_parameters():
    server = create_server()
    tools = {t.name: t for t in server._tool_manager.list_tools()}

    for tool_name in EXPECTED_TOOLS:
        tool = tools[tool_name]
        assert tool.description, f"Tool '{tool_name}' is missing description"
        assert isinstance(tool.parameters, dict)
        assert tool.parameters.get("type") == "object"


def test_server_tool_invocation_via_manager(db):
    server = create_server()
    tool = server._tool_manager.get_tool("create_ingredient")
    assert tool is not None

    result = tool.fn(name="Rolled Oats", unit="gr", kcal=389.0, protein=16.9)
    assert result["status"] == "ok"
    assert result["ingredient"]["name"] == "Rolled Oats"
    assert result["ingredient"]["kcal"] == 389.0


def test_main_settings_wiring():
    assert settings.mcp_host in ("127.0.0.1", "localhost")
    assert settings.mcp_port == 9700

