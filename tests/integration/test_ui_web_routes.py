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


@pytest.mark.anyio
async def test_ui_new_features_elements_and_interactions(db):
    server = create_server()
    app = server.streamable_http_app()
    transport = httpx2.ASGITransport(app=app)

    async with httpx2.AsyncClient(transport=transport, base_url="http://localhost:9700") as client:
        # 1. Meal tab: date is type="date", meal-item has datalist
        meal_res = await client.get("/ui/meal")
        assert meal_res.status_code == 200
        html = meal_res.text
        assert '<input type="date" id="meal-date"' in html
        assert 'list="meal-items-datalist"' in html
        assert '<datalist id="meal-items-datalist">' in html
        assert 'showPicker' in html

        # 2. Recipe tab: ingredient datalist, clean rows (no hardcoded chicken/rice)
        rec_res = await client.get("/ui/recipe")
        assert rec_res.status_code == 200
        rec_html = rec_res.text
        assert '<datalist id="recipe-ingredients-datalist">' in html
        assert 'list="recipe-ingredients-datalist"' in rec_html
        # Verify default chicken and rice are removed from initial row setup
        assert "addRecipeRow('Pechuga de Pollo', 200, 'gr');" not in rec_html
        assert "addRecipeRow('Arroz', 100, 'gr');" not in rec_html
        assert "addRecipeRow('', 100, 'gr');" in rec_html

        # 3. Workout tab: datetime-local picker
        wo_res = await client.get("/ui/workout")
        assert wo_res.status_code == 200
        wo_html = wo_res.text
        assert '<input type="datetime-local" id="workout-date"' in wo_html
        assert 'toBackendDateTime' in wo_html

        # 4. Summary tab: date picker
        sum_res = await client.get("/ui/summary")
        assert sum_res.status_code == 200
        sum_html = sum_res.text
        assert '<input type="date" id="summary-date"' in sum_html
        assert 'toBackendDate' in sum_html


@pytest.mark.anyio
async def test_ui_full_daily_summary_dashboard(db):
    from datetime import datetime
    from src.db.models import SleepLog, WeightLog

    server = create_server()
    app = server.streamable_http_app()
    transport = httpx2.ASGITransport(app=app)

    today_str = datetime.now().strftime("%d-%m-%Y")

    async with httpx2.AsyncClient(transport=transport, base_url="http://localhost:9700") as client:
        # 1. UI rendering assertions for the full daily summary dashboard
        res = await client.get("/ui/summary")
        assert res.status_code == 200
        html = res.text
        assert "summary-health" in html
        assert "summary-workouts-container" in html
        assert "summary-meals-body" in html
        assert "quickLogSteps" in html
        assert "fetchSummary" in html
        assert "renderSummaryNutrition" in html
        assert "renderSummaryHealth" in html

        # 2. Set daily goal via API
        goal_res = await client.post(
            "/api/set_daily_goal",
            json={
                "date": today_str,
                "kcal": 2200.0,
                "protein": 160.0,
                "carbs": 240.0,
                "fat": 65.0,
            },
        )
        assert goal_res.status_code == 200
        assert goal_res.json()["status"] == "ok"

        # 3. Log steps via API
        step_res = await client.post(
            "/api/log_steps",
            json={"steps": 9450, "date": today_str, "distance_km": 6.8},
        )
        assert step_res.status_code == 200
        assert step_res.json()["status"] == "ok"
        assert step_res.json()["steps"] == 9450

        # 4. Populate sleep & weight logs
        SleepLog.create(
            date=today_str,
            start_time="2026-11-09T23:00:00Z",
            end_time="2026-11-10T07:00:00Z",
            duration_minutes=468.0,
            deep_sleep_minutes=90.0,
            rem_sleep_minutes=95.0,
            light_sleep_minutes=283.0,
            source="manual",
        )
        WeightLog.create(
            date=today_str,
            weight_kg=74.2,
            bmi=22.4,
            body_fat_pct=15.2,
            source="manual",
        )

        # 5. Verify get_health_metrics returns steps, sleep and weight
        metrics_res = await client.get(f"/api/get_health_metrics?date={today_str}")
        assert metrics_res.status_code == 200
        m_data = metrics_res.json()
        assert m_data["status"] == "ok"
        assert m_data["steps"]["steps"] == 9450
        assert m_data["sleep"]["duration_hours"] == 7.8
        assert m_data["weight"]["weight_kg"] == 74.2

        # 6. Create ingredient and register a meal
        ing_res = await client.post(
            "/api/create_ingredient",
            json={
                "name": "Pechuga de Pollo",
                "unit": "gr",
                "kcal": 120.0,
                "protein": 22.0,
                "carbs": 0.0,
                "fat": 2.5,
                "price": 0.80,
            },
        )
        assert ing_res.status_code == 200

        meal_res = await client.post(
            "/api/register_meal",
            json={
                "item_name": "Pechuga de Pollo",
                "quantity": 250,
                "unit": "gr",
                "item_type": "ingredient",
                "date": today_str,
            },
        )
        assert meal_res.status_code == 200
        assert meal_res.json()["status"] == "ok"

        # 7. Register a workout
        wo_res = await client.post(
            "/api/register_workout",
            json={
                "date": f"{today_str} 10:30",
                "notes": "Torso Hipertrofia",
                "exercises": [
                    {
                        "name": "Press Banca",
                        "sets": [
                            {"set_number": 1, "reps": 8, "weight": 80.0}
                        ],
                    }
                ],
            },
        )
        assert wo_res.status_code == 200
        assert wo_res.json()["status"] == "ok"

        # 8. Check day summary API (consumed vs goal vs remaining)
        summary_res = await client.get(f"/api/get_day_summary?date={today_str}")
        assert summary_res.status_code == 200
        s_data = summary_res.json()
        assert s_data["status"] == "ok"
        assert s_data["consumed"]["kcal"] == 300.0
        assert s_data["goal"]["kcal"] == 2200.0
        assert s_data["remaining"]["kcal"] == 1900.0
        assert len(s_data["meals"]) >= 1

        # 9. Check workouts by day API
        wos_res = await client.get(f"/api/get_workouts_by_day?date={today_str}")
        assert wos_res.status_code == 200
        wos_data = wos_res.json()
        assert wos_data["status"] == "ok"
        assert len(wos_data["sessions"]) >= 1
        assert wos_data["sessions"][0]["notes"] == "Torso Hipertrofia"


@pytest.mark.anyio
async def test_ui_delete_actions_and_api(db):
    server = create_server()
    app = server.streamable_http_app()
    transport = httpx2.ASGITransport(app=app)

    async with httpx2.AsyncClient(transport=transport, base_url="http://localhost:9700") as client:
        # 1. UI rendering assertions for delete controls and functions
        ing_ui = await client.get("/ui/ingredient")
        assert ing_ui.status_code == 200
        assert "deleteIngredient" in ing_ui.text

        rec_ui = await client.get("/ui/recipe")
        assert rec_ui.status_code == 200
        assert "deleteRecipe" in rec_ui.text

        sum_ui = await client.get("/ui/summary")
        assert sum_ui.status_code == 200
        assert "deleteMeal" in sum_ui.text
        assert "<th>Acción</th>" in sum_ui.text

        # 2. Ingredient create -> delete API flow
        create_ing = await client.post(
            "/api/create_ingredient",
            json={"name": "Avocado", "unit": "u", "kcal": 160.0, "fat": 15.0},
        )
        assert create_ing.status_code == 200
        ing_id = create_ing.json()["ingredient"]["id"]

        del_ing = await client.post(
            "/api/delete_ingredient",
            json={"ingredient_id": ing_id},
        )
        assert del_ing.status_code == 200
        assert del_ing.json()["status"] == "ok"

        list_ings = await client.get("/api/list_ingredients")
        assert not any(i["id"] == ing_id for i in list_ings.json()["ingredients"])

        # 3. Recipe create -> delete API flow
        create_rec = await client.post(
            "/api/create_recipe",
            json={"name": "Guacamole", "kcal": 200.0, "price": 2.50},
        )
        assert create_rec.status_code == 200
        rec_id = create_rec.json()["recipe"]["id"]

        del_rec = await client.post(
            "/api/delete_recipe",
            json={"recipe_id": rec_id},
        )
        assert del_rec.status_code == 200
        assert del_rec.json()["status"] == "ok"

        list_recs = await client.get("/api/list_recipes")
        assert not any(r["id"] == rec_id for r in list_recs.json()["recipes"])

        # 4. Meal create -> delete API flow with summary update
        await client.post(
            "/api/set_daily_goal",
            json={"date": "15-11-2026", "kcal": 2000.0, "protein": 150.0, "carbs": 200.0, "fat": 60.0},
        )
        reg_meal = await client.post(
            "/api/register_meal",
            json={"item_name": "Quick Snack", "quantity": 1, "unit": "u", "date": "15-11-2026"},
        )
        assert reg_meal.status_code == 200
        entry_id = reg_meal.json()["entry_id"]

        sum_before = await client.get("/api/get_day_summary?date=15-11-2026")
        assert any(m["entry"]["id"] == entry_id for m in sum_before.json()["meals"])

        del_meal = await client.post(
            "/api/delete_meal",
            json={"entry_id": entry_id},
        )
        assert del_meal.status_code == 200
        assert del_meal.json()["status"] == "ok"

        sum_after = await client.get("/api/get_day_summary?date=15-11-2026")
        assert not any(m["entry"]["id"] == entry_id for m in sum_after.json()["meals"])




