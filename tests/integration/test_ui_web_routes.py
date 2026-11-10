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


@pytest.mark.anyio
async def test_ui_catalogs_and_editing_flow(db):
    server = create_server()
    app = server.streamable_http_app()
    transport = httpx2.ASGITransport(app=app)

    async with httpx2.AsyncClient(transport=transport, base_url="http://localhost:9700") as client:
        # 1. UI rendering assertions for ingredient catalog and edit controls
        ing_ui = await client.get("/ui/ingredient")
        assert ing_ui.status_code == 200
        assert "Catálogo de Ingredientes" in ing_ui.text or "Ingredientes Guardados" in ing_ui.text
        assert "ing-edit-banner" in ing_ui.text
        assert "btn-submit-ingredient" in ing_ui.text
        assert "btn-cancel-ingredient" in ing_ui.text
        assert "startEditIngredient" in ing_ui.text

        # 2. UI rendering assertions for recipe catalog and edit controls
        rec_ui = await client.get("/ui/recipe")
        assert rec_ui.status_code == 200
        assert "Recetas Guardadas" in rec_ui.text
        assert "recipe-edit-banner" in rec_ui.text
        assert "btn-submit-recipe" in rec_ui.text
        assert "btn-cancel-recipe" in rec_ui.text
        assert "startEditRecipe" in rec_ui.text

        # 3. Create ingredient -> List -> Update flow
        create_res = await client.post(
            "/api/create_ingredient",
            json={
                "name": "Oatmeal",
                "unit": "gr",
                "kcal": 368.0,
                "protein": 13.0,
                "carbs": 60.0,
                "fat": 7.0,
                "price": 1.50,
            },
        )
        assert create_res.status_code == 200
        ing_id = create_res.json()["ingredient"]["id"]

        list_ings = await client.get("/api/list_ingredients")
        assert list_ings.status_code == 200
        assert any(i["id"] == ing_id and i["name"] == "Oatmeal" for i in list_ings.json()["ingredients"])

        update_ing = await client.post(
            "/api/update_ingredient",
            json={
                "ingredient_id": ing_id,
                "name": "Rolled Oats",
                "kcal": 375.0,
                "price": 1.80,
            },
        )
        assert update_ing.status_code == 200
        updated_data = update_ing.json()
        assert updated_data["status"] == "ok"
        assert updated_data["ingredient"]["name"] == "Rolled Oats"
        assert updated_data["ingredient"]["kcal"] == 375.0

        # 4. Create Recipe -> List -> Update flow
        create_rec = await client.post(
            "/api/create_recipe",
            json={
                "name": "Porridge",
                "ingredients": [{"name": "Rolled Oats", "quantity": 80, "unit": "gr"}],
            },
        )
        assert create_rec.status_code == 200
        rec_data = create_rec.json()["recipe"]
        rec_id = rec_data["id"]
        assert len(rec_data["items"]) == 1
        assert rec_data["items"][0]["name"] == "Rolled Oats"

        list_recs = await client.get("/api/list_recipes")
        assert list_recs.status_code == 200
        matched_rec = next((r for r in list_recs.json()["recipes"] if r["id"] == rec_id), None)
        assert matched_rec is not None
        assert matched_rec["name"] == "Porridge"
        assert matched_rec["items"][0]["name"] == "Rolled Oats"

        update_rec = await client.post(
            "/api/update_recipe",
            json={
                "recipe_id": rec_id,
                "name": "Power Porridge",
                "ingredients": [{"name": "Rolled Oats", "quantity": 100, "unit": "gr"}],
            },
        )
        assert update_rec.status_code == 200
        updated_rec_data = update_rec.json()["recipe"]
        assert updated_rec_data["name"] == "Power Porridge"
        assert updated_rec_data["items"][0]["quantity"] == 100.0

