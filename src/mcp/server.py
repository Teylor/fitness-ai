"""MCP server setup and tool registration."""

import dataclasses
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response

from src.mcp.tools.body_progress_tools import (
    delete_body_progress,
    list_body_progress,
    log_body_progress,
)
from src.mcp.tools.exercise_tools import (
    create_exercise,
    list_exercises,
    update_exercise,
)
from src.mcp.tools.goal_tools import get_daily_goal, set_daily_goal, toggle_day_off
from src.mcp.tools.ingredient_tools import (
    create_ingredient,
    delete_ingredient,
    list_ingredients,
    update_ingredient,
)
from src.mcp.tools.meal_tools import (
    delete_meal,
    get_day_summary,
    register_meal,
    toggle_daily_creatine,
    toggle_daily_supplement,
)
from src.mcp.tools.recipe_tools import (
    create_recipe,
    delete_recipe,
    list_recipes,
    update_recipe,
)
from src.mcp.tools.health_tools import (
    fetch_google_health_sleep,
    fetch_google_health_steps,
    fetch_google_health_weight,
    get_health_metrics,
    log_steps,
    sync_google_health,
    sync_meals_to_google_health,
)
from src.mcp.tools.ui_tools import get_ui_form
from src.mcp.tools.workout_tools import (
    get_last_workout,
    get_personal_record,
    get_workouts_by_day,
    register_workout,
)
from src.ui import render_latest_html


def create_server() -> MCPServer:
    """Create and configure the MCPServer instance with active tools."""
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

    # Meal tools (5)
    server.add_tool(register_meal, name="register_meal")
    server.add_tool(get_day_summary, name="get_day_summary")
    server.add_tool(delete_meal, name="delete_meal")
    server.add_tool(toggle_daily_creatine, name="toggle_daily_creatine")
    server.add_tool(toggle_daily_supplement, name="toggle_daily_supplement")

    # Goal tools (3)
    server.add_tool(set_daily_goal, name="set_daily_goal")
    server.add_tool(get_daily_goal, name="get_daily_goal")
    server.add_tool(toggle_day_off, name="toggle_day_off")

    # Workout tools (4)
    server.add_tool(register_workout, name="register_workout")
    server.add_tool(get_last_workout, name="get_last_workout")
    server.add_tool(get_personal_record, name="get_personal_record")
    server.add_tool(get_workouts_by_day, name="get_workouts_by_day")

    # Exercise tools (3)
    server.add_tool(list_exercises, name="list_exercises")
    server.add_tool(create_exercise, name="create_exercise")
    server.add_tool(update_exercise, name="update_exercise")

    # UI tool (1)
    server.add_tool(get_ui_form, name="get_ui_form")

    # Google Health tools (7)
    server.add_tool(sync_meals_to_google_health, name="sync_meals_to_google_health")
    server.add_tool(fetch_google_health_sleep, name="fetch_google_health_sleep")
    server.add_tool(fetch_google_health_weight, name="fetch_google_health_weight")
    server.add_tool(fetch_google_health_steps, name="fetch_google_health_steps")
    server.add_tool(sync_google_health, name="sync_google_health")
    server.add_tool(log_steps, name="log_steps")
    server.add_tool(get_health_metrics, name="get_health_metrics")

    # Body Progress tools (3)
    server.add_tool(log_body_progress, name="log_body_progress")
    server.add_tool(list_body_progress, name="list_body_progress")
    server.add_tool(delete_body_progress, name="delete_body_progress")

    # Custom HTTP web routes for interactive artifacts
    assets_dir = Path(__file__).resolve().parent.parent / "ui" / "assets"

    def _serve_asset(filename: str, media_type: str) -> Response:
        asset_path = assets_dir / filename
        if not asset_path.is_file():
            return Response(status_code=404)
        return Response(
            content=asset_path.read_bytes(),
            media_type=media_type,
            headers={"Cache-Control": "no-cache"},
        )

    @server.custom_route("/favicon.ico", methods=["GET"])
    async def favicon_ico_handler(request: Request) -> Response:
        return _serve_asset("favicon.ico", "image/x-icon")

    @server.custom_route("/favicon-32x32.png", methods=["GET"])
    async def favicon_png_handler(request: Request) -> Response:
        return _serve_asset("favicon-32x32.png", "image/png")

    @server.custom_route("/apple-touch-icon.png", methods=["GET"])
    async def apple_touch_icon_handler(request: Request) -> Response:
        return _serve_asset("apple-touch-icon.png", "image/png")

    @server.custom_route("/icon-192.png", methods=["GET"])
    async def icon_192_handler(request: Request) -> Response:
        return _serve_asset("icon-192.png", "image/png")

    @server.custom_route("/icon-512.png", methods=["GET"])
    async def icon_512_handler(request: Request) -> Response:
        return _serve_asset("icon-512.png", "image/png")

    @server.custom_route("/manifest.webmanifest", methods=["GET"])
    async def manifest_handler(request: Request) -> JSONResponse:
        return JSONResponse(
            {
                "name": "Fitness AI",
                "short_name": "Fitness AI",
                "description": "Nutrition, workout, and daily health tracker",
                "start_url": "/ui",
                "scope": "/",
                "display": "standalone",
                "background_color": "#0f172a",
                "theme_color": "#0f172a",
                "icons": [
                    {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
                    {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"},
                ],
            },
            media_type="application/manifest+json",
            headers={"Cache-Control": "no-cache"},
        )

    @server.custom_route("/sw.js", methods=["GET"])
    async def service_worker_handler(request: Request) -> Response:
        sw_code = (
            "self.addEventListener('install', () => self.skipWaiting());\n"
            "self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));\n"
            "self.addEventListener('fetch', (e) => {\n"
            "  const url = new URL(e.request.url);\n"
            "  if (url.pathname.startsWith('/api/') || e.request.method !== 'GET') return;\n"
            "  e.respondWith(fetch(e.request));\n"
            "});\n"
        )
        return Response(
            content=sw_code,
            media_type="application/javascript",
            headers={"Cache-Control": "no-cache", "Service-Worker-Allowed": "/"},
        )

    @server.custom_route("/ui", methods=["GET"])
    async def ui_hub_handler(request: Request) -> HTMLResponse:
        form_type = request.query_params.get("form", "hub")
        return HTMLResponse(render_latest_html(form_type))

    @server.custom_route("/ui/{form_type}", methods=["GET"])
    async def ui_form_handler(request: Request) -> HTMLResponse:
        form_type = request.path_params.get("form_type", "hub")
        return HTMLResponse(render_latest_html(form_type))

    @server.custom_route("/api/{tool_name}", methods=["GET", "POST"])
    async def api_dispatch_handler(request: Request) -> JSONResponse:
        tool_name = request.path_params.get("tool_name")
        tool = server._tool_manager.get_tool(tool_name)
        if not tool:
            return JSONResponse(
                {
                    "status": "error",
                    "code": "not_found",
                    "message": f"unknown tool or endpoint '{tool_name}'",
                },
                status_code=404,
            )

        kwargs = {}
        if request.method == "POST":
            try:
                kwargs = await request.json()
            except Exception:
                kwargs = {}
        else:
            kwargs = dict(request.query_params)

        try:
            result = tool.fn(**kwargs)
            return JSONResponse(_to_jsonable(result))
        except Exception as exc:
            return JSONResponse(
                {"status": "error", "code": "internal", "message": str(exc)},
                status_code=500,
            )

    return server


def _to_jsonable(obj: Any) -> Any:
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return dataclasses.asdict(obj)
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_to_jsonable(v) for v in obj]
    return obj
