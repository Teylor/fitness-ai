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
        assert "Hermes Hub" in ui_res.text
        assert "Sincronizar Google Health" in ui_res.text
        assert "syncGoogleHealthUI" in ui_res.text

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
    from src.db.models import SleepLog, StepLog, WeightLog

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
        assert "summary-meals-container" in html
        assert "summary-meals-body" in html
        assert "meal-eating-type" in html
        assert "MEAL_TYPE_SECTIONS" in html
        assert "quick-steps-input" not in html
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

        # 3. Log steps via API is disabled
        step_res = await client.post(
            "/api/log_steps",
            json={"steps": 9450, "date": today_str, "distance_km": 6.8},
        )
        assert step_res.status_code == 200
        assert step_res.json()["status"] == "error"
        assert step_res.json()["code"] == "manual_steps_disabled"

        # Steps are populated via Google Health sync
        StepLog.create(
            date=today_str,
            steps=9450,
            distance_km=6.8,
            source="google_health",
        )

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


@pytest.mark.anyio
async def test_ui_exercises_tab_and_prs_integration(db):
    server = create_server()
    app = server.streamable_http_app()
    transport = httpx2.ASGITransport(app=app)

    async with httpx2.AsyncClient(transport=transport, base_url="http://localhost:9700") as client:
        # 1. GET /ui/exercise
        ui_res = await client.get("/ui/exercise")
        assert ui_res.status_code == 200
        assert "Ejercicios y Récords Personales" in ui_res.text
        assert "1RM Estimado" in ui_res.text
        assert "Peso 1RM" in ui_res.text
        assert "Peso Máx" in ui_res.text
        assert "💪 Ejercicios" in ui_res.text

        # 2. Create exercise
        create_res = await client.post(
            "/api/create_exercise",
            json={"name": "Press Militar", "muscle_group": "hombro", "type": "weight_reps"},
        )
        assert create_res.status_code == 200
        assert create_res.json()["status"] == "ok"

        # 3. Register workout with 20kg x 10, 22kg x 6, 18kg x 12
        workout_res = await client.post(
            "/api/register_workout",
            json={
                "date": "18-05-2026",
                "exercises": [
                    {
                        "name": "Press Militar",
                        "sets": [
                            {"set_number": 1, "reps": 10, "weight": 20.0},
                            {"set_number": 2, "reps": 6, "weight": 22.0},
                            {"set_number": 3, "reps": 12, "weight": 18.0},
                        ],
                    }
                ],
            },
        )
        assert workout_res.status_code == 200
        assert workout_res.json()["status"] == "ok"

        # 4. Fetch /api/list_exercises?include_prs=true
        list_res = await client.get("/api/list_exercises?include_prs=true")
        assert list_res.status_code == 200
        data = list_res.json()
        assert data["status"] == "ok"

        press = next((x for x in data["exercises"] if x["name"] == "Press Militar"), None)
        assert press is not None
        assert press["pr"] is not None
        assert press["pr"]["max_weight"] == 22.0
        assert press["pr"]["max_weight_reps"] == 6
        assert press["pr"]["estimated_1rm"] == 26.7
        assert press["pr"]["estimated_1rm_weight"] == 20.0
        assert press["pr"]["estimated_1rm_reps"] == 10


@pytest.mark.anyio
async def test_ui_supplements_and_water_integration(db):
    server = create_server()
    app = server.streamable_http_app()
    transport = httpx2.ASGITransport(app=app)

    async with httpx2.AsyncClient(transport=transport, base_url="http://localhost:9700") as client:
        # 1. Verify UI HTML has supplement checkbox and Agua y Suplementos sections
        ui_res = await client.get("/ui/ingredient")
        assert ui_res.status_code == 200
        assert 'id="ing-is-supplement"' in ui_res.text
        assert "Agua y Suplementos" in ui_res.text
        assert "supplements-catalog-table" in ui_res.text
        assert "summary-water-supplements-container" in ui_res.text

        # 2. Set daily goal
        await client.post(
            "/api/set_daily_goal",
            json={"date": "20-05-2026", "kcal": 2000.0, "protein": 150.0, "carbs": 200.0, "fat": 60.0},
        )

        # 3. Create supplement ingredient
        supp_res = await client.post(
            "/api/create_ingredient",
            json={
                "name": "Creatina",
                "unit": "gr",
                "kcal": 0.0,
                "protein": 0.0,
                "carbs": 0.0,
                "fat": 0.0,
                "price": 30.0,
                "is_supplement": True,
            },
        )
        assert supp_res.status_code == 200
        assert supp_res.json()["ingredient"]["is_supplement"] is True

        # 4. Log supplement meal entry
        meal_res = await client.post(
            "/api/register_meal",
            json={
                "item_name": "Creatina",
                "quantity": 5,
                "unit": "gr",
                "item_type": "ingredient",
                "date": "20-05-2026",
            },
        )
        assert meal_res.status_code == 200

        # 5. Verify day summary includes water (3L, 1.25€) and supplement
        sum_res = await client.get("/api/get_day_summary?date=20-05-2026")
        assert sum_res.status_code == 200
        sum_data = sum_res.json()
        assert sum_data["status"] == "ok"
        assert "water_and_supplements" in sum_data
        ws = sum_data["water_and_supplements"]
        assert ws["water"]["quantity"] == 3.0
        assert ws["water"]["price"] == 1.25
        assert len(ws["supplements"]) == 1
        assert ws["supplements"][0]["name"] == "Creatina"
        # 1.25 (water) + 0.15 (5g of 3.0€/100g creatine) = 1.40
        assert ws["spend"] == 1.40
        assert sum_data["spend"] == 1.40


@pytest.mark.anyio
async def test_ui_favicon_routes_and_head_links(db):
    server = create_server()
    app = server.streamable_http_app()
    transport = httpx2.ASGITransport(app=app)

    async with httpx2.AsyncClient(transport=transport, base_url="http://localhost:9700") as client:
        ui_res = await client.get("/ui")
        assert ui_res.status_code == 200
        assert '<link rel="icon" type="image/x-icon" href="/favicon.ico?v=2">' in ui_res.text
        assert '<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png?v=2">' in ui_res.text
        assert '<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png?v=2">' in ui_res.text

        ico_res = await client.get("/favicon.ico")
        assert ico_res.status_code == 200
        assert ico_res.headers.get("content-type", "").startswith("image/x-icon")
        assert len(ico_res.content) > 0

        png_res = await client.get("/favicon-32x32.png")
        assert png_res.status_code == 200
        assert png_res.headers.get("content-type", "").startswith("image/png")
        assert png_res.content.startswith(b"\x89PNG")

        apple_res = await client.get("/apple-touch-icon.png")
        assert apple_res.status_code == 200
        assert apple_res.headers.get("content-type", "").startswith("image/png")
        assert apple_res.content.startswith(b"\x89PNG")


@pytest.mark.anyio
async def test_ui_day_off_toggle_and_goal_profiles(db):
    server = create_server()
    app = server.streamable_http_app()
    transport = httpx2.ASGITransport(app=app)

    async with httpx2.AsyncClient(transport=transport, base_url="http://localhost:9700") as client:
        ui_res = await client.get("/ui/summary")
        assert ui_res.status_code == 200
        assert "btn-toggle-day-off" in ui_res.text
        assert "goal-profiles-panel" in ui_res.text
        assert "toggleDayOffUI" in ui_res.text

        # Configure training default & day off default
        tr_res = await client.post(
            "/api/set_daily_goal",
            json={"kcal": 2500.0, "protein": 180.0, "carbs": 280.0, "fat": 70.0, "default": True},
        )
        assert tr_res.status_code == 200
        assert tr_res.json()["status"] == "ok"

        off_res = await client.post(
            "/api/set_daily_goal",
            json={"kcal": 2050.0, "protein": 180.0, "carbs": 165.0, "fat": 70.0, "day_off_default": True},
        )
        assert off_res.status_code == 200
        assert off_res.json()["status"] == "ok"

        # Toggle Day Off ON for 25-11-2026
        tog_on = await client.post(
            "/api/toggle_day_off",
            json={"date": "25-11-2026", "is_day_off": True},
        )
        assert tog_on.status_code == 200
        assert tog_on.json()["is_day_off"] is True
        assert tog_on.json()["goal"]["kcal"] == 2050.0

        sum_on = await client.get("/api/get_day_summary?date=25-11-2026")
        assert sum_on.status_code == 200
        assert sum_on.json()["goal"]["kcal"] == 2050.0
        assert sum_on.json()["goal"]["is_day_off"] is True

        # Toggle Day Off OFF
        tog_off = await client.post(
            "/api/toggle_day_off",
            json={"date": "25-11-2026", "is_day_off": False},
        )
        assert tog_off.status_code == 200
        assert tog_off.json()["is_day_off"] is False
        assert tog_off.json()["goal"]["kcal"] == 2500.0


@pytest.mark.anyio
async def test_ui_execute_action_summary(db):
    server = create_server()
    app = server.streamable_http_app()
    transport = httpx2.ASGITransport(app=app)

    async with httpx2.AsyncClient(transport=transport, base_url="http://localhost:9700") as client:
        res = await client.get("/ui/workout")
        assert res.status_code == 200
        html = res.text
        # Success branch renders a one-line summary via the helper
        assert "function summarizeSuccess" in html
        assert "summarizeSuccess(data, payload)" in html
        # Full response stays accessible, collapsed, not as a bare full dump
        assert "<summary>Ver respuesta completa</summary>" in html
        assert "<div>${JSON.stringify(data, null, 2)}</div>" not in html
        # Success contract that callers rely on is preserved
        assert "return data;" in html


@pytest.mark.anyio
async def test_ui_accent_insensitive_search_helpers(db):
    server = create_server()
    app = server.streamable_http_app()
    transport = httpx2.ASGITransport(app=app)

    async with httpx2.AsyncClient(transport=transport, base_url="http://localhost:9700") as client:
        res = await client.get("/ui/ingredient")
        assert res.status_code == 200
        html = res.text
        assert "function normalizeText(" in html
        assert "function attachAutocomplete(" in html
        assert "normalize('NFKD')" in html
        assert "normalizeText(opt.value).includes(q)" in html
        assert "normalizeText(i.name).includes(query)" in html
        assert "normalizeText(r.name).includes(query)" in html
        assert "normalizeText(ex.name).includes(search)" in html
        assert "normalizeText(ex.muscle_group) === group" in html


@pytest.mark.anyio
async def test_ui_daily_creatine_toggle_integration(db):
    server = create_server()
    app = server.streamable_http_app()
    transport = httpx2.ASGITransport(app=app)

    async with httpx2.AsyncClient(transport=transport, base_url="http://localhost:9700") as client:
        res = await client.get("/ui/summary")
        assert res.status_code == 200
        html = res.text
        assert "toggleDailyCreatineUI" in html
        assert "/api/toggle_daily_creatine" in html
        assert "Creatina diaria: 1 u (0.30 €)" in html

        await client.post(
            "/api/set_daily_goal",
            json={"date": "22-11-2026", "kcal": 2200.0, "protein": 150.0, "carbs": 220.0, "fat": 70.0},
        )

        # Default enabled -> 1.25 (water) + 0.30 (creatine) = 1.55
        s1 = await client.get("/api/get_day_summary?date=22-11-2026")
        assert s1.status_code == 200
        assert s1.json()["spend"] == 1.55
        assert s1.json()["water_and_supplements"]["creatine"]["enabled"] is True

        # Toggle OFF via HTTP API
        off = await client.post(
            "/api/toggle_daily_creatine",
            json={"date": "22-11-2026", "enabled": False},
        )
        assert off.status_code == 200
        assert off.json()["enabled"] is False
        assert off.json()["spend"] == 1.25


@pytest.mark.anyio
async def test_ui_pwa_manifest_sw_and_icons(db):
    server = create_server()
    app = server.streamable_http_app()
    transport = httpx2.ASGITransport(app=app)

    async with httpx2.AsyncClient(transport=transport, base_url="http://localhost:9700") as client:
        ui_res = await client.get("/ui")
        assert ui_res.status_code == 200
        html = ui_res.text
        assert '<link rel="manifest" href="/manifest.webmanifest">' in html
        assert '<meta name="theme-color" content="#0f172a">' in html
        assert "navigator.serviceWorker.register('/sw.js')" in html

        mf_res = await client.get("/manifest.webmanifest")
        assert mf_res.status_code == 200
        assert "application/manifest+json" in mf_res.headers.get("content-type", "")
        mf = mf_res.json()
        assert mf["name"] == "Fitness AI"
        assert mf["start_url"] == "/ui"
        assert mf["display"] == "standalone"
        assert {ic["src"] for ic in mf["icons"]} >= {"/icon-192.png", "/icon-512.png"}

        sw_res = await client.get("/sw.js")
        assert sw_res.status_code == 200
        assert "javascript" in sw_res.headers.get("content-type", "")
        assert sw_res.headers.get("service-worker-allowed") == "/"
        assert "/api/" in sw_res.text

        for icon_path in ("/icon-192.png", "/icon-512.png"):
            ic_res = await client.get(icon_path)
            assert ic_res.status_code == 200
            assert ic_res.headers.get("content-type", "").startswith("image/png")
            assert ic_res.content[:4] == b"\x89PNG"


@pytest.mark.anyio
async def test_ui_hot_reload_on_mtime_change(db, monkeypatch):
    import importlib
    import src.ui as ui_pkg
    from src.ui import html_generator

    reload_calls = []
    orig_reload = importlib.reload

    def spy_reload(mod):
        reload_calls.append(mod)
        return orig_reload(mod)

    monkeypatch.setattr(importlib, "reload", spy_reload)
    # Force an mtime mismatch on the next request
    monkeypatch.setattr(ui_pkg, "_last_html_mtime_ns", -1)

    server = create_server()
    app = server.streamable_http_app()
    transport = httpx2.ASGITransport(app=app)

    async with httpx2.AsyncClient(transport=transport, base_url="http://localhost:9700") as client:
        res1 = await client.get("/ui")
        assert res1.status_code == 200
        assert len(reload_calls) == 1
        assert reload_calls[0] is html_generator

        # Subsequent request without mtime change does not reload again
        res2 = await client.get("/ui/meal")
        assert res2.status_code == 200
        assert len(reload_calls) == 1


@pytest.mark.anyio
async def test_ui_daily_supplements_toggle_integration(db):
    server = create_server()
    app = server.streamable_http_app()
    transport = httpx2.ASGITransport(app=app)

    async with httpx2.AsyncClient(transport=transport, base_url="http://localhost:9700") as client:
        res = await client.get("/ui/summary")
        assert res.status_code == 200
        html = res.text
        assert "toggleDailySupplementUI" in html
        assert "/api/toggle_daily_supplement" in html

        await client.post(
            "/api/set_daily_goal",
            json={"date": "27-11-2026", "kcal": 2200.0, "protein": 150.0, "carbs": 220.0, "fat": 70.0},
        )
        cr = await client.post(
            "/api/create_ingredient",
            json={"name": "Omega 3", "unit": "u", "kcal": 18, "protein": 0, "carbs": 0, "fat": 2, "price": 0.20, "is_supplement": True},
        )
        ing_id = cr.json()["ingredient"]["id"]

        # Default OFF
        s1 = await client.get("/api/get_day_summary?date=27-11-2026")
        assert s1.status_code == 200
        assert s1.json()["spend"] == 1.55
        ds1 = s1.json()["water_and_supplements"]["daily_supplements"]
        assert len(ds1) == 1 and ds1[0]["enabled"] is False

        # Toggle ON via HTTP API
        on = await client.post(
            "/api/toggle_daily_supplement",
            json={"ingredient_id": ing_id, "date": "27-11-2026", "enabled": True},
        )
        assert on.status_code == 200
        assert on.json()["enabled"] is True
        assert on.json()["spend"] == 1.75


@pytest.mark.anyio
async def test_ui_workout_training_enhancements_pack(db):
    server = create_server()
    app = server.streamable_http_app()
    transport = httpx2.ASGITransport(app=app)

    async with httpx2.AsyncClient(transport=transport, base_url="http://localhost:9700") as client:
        # 1. UI HTML checks for workout cardio time logging, max_weight_sets, and summary 1RM badges
        wo_ui = await client.get("/ui/workout")
        assert wo_ui.status_code == 200
        wo_html = wo_ui.text
        assert "Añadir Cardio (Tiempo)" in wo_html
        assert "set-duration-min" in wo_html
        assert "onExerciseModeChange" in wo_html
        assert "max_weight_sets" in wo_html
        assert "summary-exercise-1rm-badges" in wo_html
        assert "#ingredients-catalog-table td:nth-child(7)" in wo_html
        assert '<td style="white-space: nowrap;">${priceStr}</td>' in wo_html

        # 2. Register workout with multiple sets at max weight (75x10, 75x9) and cardio time (20 min = 1200s)
        reg = await client.post(
            "/api/register_workout",
            json={
                "date": "28-11-2026 18:00",
                "notes": "Push + Cardio",
                "exercises": [
                    {
                        "name": "Press Banca",
                        "sets": [
                            {"set_number": 1, "reps": 10, "weight": 75.0},
                            {"set_number": 2, "reps": 9, "weight": 75.0},
                        ],
                    },
                    {
                        "name": "Cinta",
                        "sets": [
                            {"set_number": 1, "duration": 1200},
                        ],
                    },
                ],
            },
        )
        assert reg.status_code == 200
        assert reg.json()["status"] == "ok"

        # 3. Verify list_exercises?include_prs=true returns max_weight_sets = 2
        ex_res = await client.get("/api/list_exercises?include_prs=true")
        assert ex_res.status_code == 200
        pb = next((x for x in ex_res.json()["exercises"] if x["name"] == "Press Banca"), None)
        assert pb is not None
        assert pb["pr"]["max_weight"] == 75.0
        assert pb["pr"]["max_weight_reps"] == 10
        assert pb["pr"]["max_weight_sets"] == 2

        # 4. Verify get_workouts_by_day returns estimated_1rm on weight sets and duration on cardio sets
        day_wo = await client.get("/api/get_workouts_by_day?date=28-11-2026")
        assert day_wo.status_code == 200
        sets = day_wo.json()["sessions"][0]["sets"]
        pb_sets = [s for s in sets if s["exercise"] == "Press Banca"]
        assert len(pb_sets) == 2
        assert pb_sets[0]["estimated_1rm"] == 100.0
        assert pb_sets[1]["estimated_1rm"] == 97.5
        cinta_set = next(s for s in sets if s["exercise"] == "Cinta")
        assert cinta_set["duration"] == 1200
        assert cinta_set["estimated_1rm"] is None


@pytest.mark.anyio
async def test_ui_workout_exercise_max_weight_reference(db):
    server = create_server()
    app = server.streamable_http_app()
    transport = httpx2.ASGITransport(app=app)

    async with httpx2.AsyncClient(transport=transport, base_url="http://localhost:9700") as client:
        # 1. Verify workout tab HTML includes max-weight reference element and helper functions
        wo_ui = await client.get("/ui/workout")
        assert wo_ui.status_code == 200
        html = wo_ui.text
        assert 'class="ex-max-weight-ref"' in html
        assert "function updateExerciseMaxWeightRef(" in html
        assert "function refreshAllWorkoutExerciseRefs(" in html
        assert "<span>Peso Máx:</span>" in html
        assert "Máx ${ex.pr.max_weight} kg" in html
        assert "if (tabName === 'workout') fetchExercisesList();" in html

        # 2. Verify PR max_weight data is returned for recorded weight exercises and absent for unrecorded/time ones
        await client.post(
            "/api/create_exercise",
            json={"name": "Remo con Barra", "muscle_group": "Espalda", "type": "weight_reps"},
        )
        await client.post(
            "/api/create_exercise",
            json={"name": "Curl Martillo", "muscle_group": "Biceps", "type": "weight_reps"},
        )
        await client.post(
            "/api/register_workout",
            json={
                "date": "20-11-2026 19:00",
                "exercises": [
                    {
                        "name": "Remo con Barra",
                        "sets": [
                            {"set_number": 1, "reps": 8, "weight": 70.0},
                            {"set_number": 2, "reps": 8, "weight": 70.0},
                        ],
                    }
                ],
            },
        )

        ex_res = await client.get("/api/list_exercises?include_prs=true")
        assert ex_res.status_code == 200
        exercises = ex_res.json()["exercises"]
        remo = next(e for e in exercises if e["name"] == "Remo con Barra")
        assert remo["pr"] is not None
        assert remo["pr"]["max_weight"] == 70.0
        assert remo["pr"]["max_weight_reps"] == 8
        assert remo["pr"]["max_weight_sets"] == 2
        assert remo["pr"]["max_weight_date"] == "20-11-2026"

        curl = next(e for e in exercises if e["name"] == "Curl Martillo")
        assert curl["pr"] is None or curl["pr"].get("max_weight") is None







