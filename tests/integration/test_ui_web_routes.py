"""Integration tests: Starlette UI web routes and API dispatch."""

import httpx2
import pytest

from src.mcp.server import create_server


@pytest.mark.anyio
async def test_ui_web_routes_and_api_dispatch(db):
    server = create_server()
    app = server.streamable_http_app()
    transport = httpx2.ASGITransport(app=app)

    async with httpx2.AsyncClient(transport=transport, base_url="http://localhost:9700") as client:
        # 1. GET /ui hub
        ui_res = await client.get("/ui")
        assert ui_res.status_code == 200
        assert "text/html" in ui_res.headers.get("content-type", "")
        assert "Fitness AI Hub" in ui_res.text

        # 2. GET /ui/workout
        workout_res = await client.get("/ui/workout")
        assert workout_res.status_code == 200
        assert "Registrar Entrenamiento" in workout_res.text

        # 3. POST /api/create_ingredient
        api_ing = await client.post(
            "/api/create_ingredient",
            json={
                "name": "Almonds",
                "unit": "gr",
                "kcal": 579.0,
                "protein": 21.0,
                "carbs": 22.0,
                "fat": 50.0,
            },
        )
        assert api_ing.status_code == 200
        ing_data = api_ing.json()
        assert ing_data["status"] == "ok"
        assert ing_data["ingredient"]["name"] == "Almonds"

        # 4. GET /api/list_exercises
        api_ex = await client.get("/api/list_exercises")
        assert api_ex.status_code == 200
        assert api_ex.json()["status"] == "ok"

        # 5. Unknown tool endpoint -> 404
        unknown = await client.post("/api/unknown_action", json={})
        assert unknown.status_code == 404
        assert unknown.json()["status"] == "error"
        assert unknown.json()["code"] == "not_found"
