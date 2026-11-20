"""End-to-End tests simulating Hermes Agent interactions over MCP protocol."""

import pytest

EXPECTED_18_TOOLS = {
    # Ingredients (4)
    "create_ingredient",
    "update_ingredient",
    "delete_ingredient",
    "list_ingredients",
    # Recipes (4)
    "create_recipe",
    "update_recipe",
    "delete_recipe",
    "list_recipes",
    # Meals (3)
    "register_meal",
    "get_day_summary",
    "delete_meal",
    "toggle_daily_creatine",
    "toggle_daily_supplement",
    # Goals (2)
    "set_daily_goal",
    "get_daily_goal",
    # Workouts (4)
    "register_workout",
    "get_last_workout",
    "get_personal_record",
    "get_workouts_by_day",
    # Exercises (3)
    "list_exercises",
    "create_exercise",
    "update_exercise",
    # UI Artifacts (1)
    "get_ui_form",
    # Health & Activity (7)
    "sync_meals_to_google_health",
    "fetch_google_health_sleep",
    "fetch_google_health_weight",
    "fetch_google_health_steps",
    "sync_google_health",
    "log_steps",
    "get_health_metrics",
    "toggle_day_off",
    # Body Progress (3)
    "log_body_progress",
    "list_body_progress",
    "delete_body_progress",
}


@pytest.mark.anyio
async def test_hermes_protocol_handshake_and_tool_discovery(hermes_client):
    """Verify that Hermes can connect, initialize session, and discover all tools."""
    tool_names = await hermes_client.list_tool_names()
    assert len(tool_names) == 34
    assert tool_names == EXPECTED_18_TOOLS

    tools = await hermes_client.list_tools()
    for tool in tools:
        assert tool.name in EXPECTED_18_TOOLS
        assert tool.description, f"Tool '{tool.name}' is missing description"
        assert isinstance(tool.input_schema, dict)
        assert tool.input_schema.get("type") == "object"


@pytest.mark.anyio
async def test_hermes_nutrition_and_goals_workflow(hermes_client):
    """E2E Scenario: Hermes registers ingredients, sets goals, creates recipes, logs meals, and gets day summary."""
    # 1. Set a default daily goal
    goal_res = await hermes_client.call_tool(
        "set_daily_goal",
        kcal=2500.0,
        protein=180.0,
        carbs=250.0,
        fat=70.0,
        default=True,
    )
    assert goal_res["status"] == "ok"
    assert goal_res["goal"]["kcal"] == 2500.0
    assert goal_res["goal"]["is_default"] is True

    # 2. Create ingredients
    chicken = await hermes_client.call_tool(
        "create_ingredient",
        name="Chicken Breast",
        unit="gr",
        kcal=165.0,
        protein=31.0,
        carbs=0.0,
        fat=3.6,
        price=1.2,
    )
    assert chicken["status"] == "ok"
    assert chicken["ingredient"]["id"] is not None

    rice = await hermes_client.call_tool(
        "create_ingredient",
        name="White Rice",
        unit="gr",
        kcal=130.0,
        protein=2.7,
        carbs=28.0,
        fat=0.3,
        price=0.2,
    )
    assert rice["status"] == "ok"

    oil = await hermes_client.call_tool(
        "create_ingredient",
        name="Olive Oil",
        unit="ml",
        kcal=884.0,
        protein=0.0,
        carbs=0.0,
        fat=100.0,
        price=0.9,
    )
    assert oil["status"] == "ok"

    # 3. Create a composite recipe
    recipe_res = await hermes_client.call_tool(
        "create_recipe",
        name="Chicken & Rice Bowl",
        ingredients=[
            {"name": "Chicken Breast", "quantity": 200, "unit": "gr"},
            {"name": "White Rice", "quantity": 150, "unit": "gr"},
            {"name": "Olive Oil", "quantity": 10, "unit": "ml"},
        ],
    )
    assert recipe_res["status"] == "ok"
    recipe = recipe_res["recipe"]
    assert recipe["name"] == "Chicken & Rice Bowl"
    # 200g chicken (330 kcal, 62g P) + 150g rice (195 kcal, 4.05g P) + 10ml oil (88.4 kcal, 10g F)
    assert recipe["kcal"] == 613.4
    assert recipe["protein"] == 66.05
    assert recipe["carbs"] == 42.0
    assert recipe["fat"] == 17.65

    # 4. Log meals for date "10-11-2026"
    test_date = "10-11-2026"

    # Breakfast: 100g white rice directly
    meal1 = await hermes_client.call_tool(
        "register_meal",
        date=test_date,
        item_name="White Rice",
        item_type="ingredient",
        quantity=100.0,
        unit="gr",
    )
    assert meal1["status"] == "ok"

    # Lunch: 1 portion of recipe
    meal2 = await hermes_client.call_tool(
        "register_meal",
        date=test_date,
        item_name="Chicken & Rice Bowl",
        item_type="recipe",
        quantity=1.0,
        unit="u",
    )
    assert meal2["status"] == "ok"

    # 5. Query daily summary
    summary = await hermes_client.call_tool("get_day_summary", date=test_date)
    assert summary["status"] == "ok"
    assert len(summary["meals"]) == 2

    consumed = summary["consumed"]
    assert consumed["kcal"] == 743.4
    assert consumed["protein"] == 68.75
    assert consumed["carbs"] == 70.0
    assert consumed["fat"] == 17.95

    assert summary["goal"]["kcal"] == 2500.0
    remaining = summary["remaining"]
    assert remaining["kcal"] == 1756.6
    assert remaining["protein"] == 111.25


@pytest.mark.anyio
async def test_hermes_training_and_pr_workflow(hermes_client):
    """E2E Scenario: Hermes catalogs exercises, logs multi-set workouts, computes 1RM PRs, and reads workout history."""
    # 1. Create exercise catalog items
    bp = await hermes_client.call_tool(
        "create_exercise",
        name="Bench Press",
        muscle_group="chest",
        type="weight_reps",
    )
    assert bp["status"] == "ok"

    squat = await hermes_client.call_tool(
        "create_exercise",
        name="Barbell Squat",
        muscle_group="legs",
        type="weight_reps",
    )
    assert squat["status"] == "ok"

    plank = await hermes_client.call_tool(
        "create_exercise",
        name="Plank",
        muscle_group="core",
        type="time",
    )
    assert plank["status"] == "ok"

    # 2. Register first workout session
    session1 = await hermes_client.call_tool(
        "register_workout",
        date="01-05-2026 18:00",
        notes="heavy leg & push session",
        exercises=[
            {
                "name": "Bench Press",
                "sets": [
                    {"set_number": 1, "reps": 10, "weight": 60.0},
                    {"set_number": 2, "reps": 8, "weight": 70.0},
                ],
            },
            {
                "name": "Barbell Squat",
                "sets": [
                    {"set_number": 1, "reps": 5, "weight": 100.0},
                ],
            },
            {
                "name": "Plank",
                "sets": [
                    {"set_number": 1, "duration": 60.0},
                ],
            },
        ],
    )
    assert session1["status"] == "ok"
    assert session1["session"]["id"] is not None
    assert len(session1["sets"]) == 4

    # Both weight_reps exercises earn their initial PR
    pr_exercises = {pr["exercise"] for pr in session1["new_prs"]}
    assert pr_exercises == {"Bench Press", "Barbell Squat"}

    # 3. Verify PRs after session 1
    bp_pr = await hermes_client.call_tool(
        "get_personal_record", exercise_name="Bench Press"
    )
    assert bp_pr["status"] == "ok"
    record1 = bp_pr["personal_record"]
    assert record1["max_weight"] == 70.0
    assert record1["max_reps"] == 8
    assert record1["estimated_1rm"] == 88.67
    assert record1["date"] == "01-05-2026"

    squat_pr = await hermes_client.call_tool(
        "get_personal_record", exercise_name="Barbell Squat"
    )
    assert squat_pr["status"] == "ok"
    assert squat_pr["personal_record"]["estimated_1rm"] == 116.67

    # 4. Register progression session on 08-05-2026 with a direct 1-rep max attempt
    session2 = await hermes_client.call_tool(
        "register_workout",
        date="08-05-2026 18:30",
        notes="push day PR attempt",
        exercises=[
            {
                "name": "Bench Press",
                "sets": [
                    {"set_number": 1, "reps": 8, "weight": 70.0},  # equal to previous PR set (88.67)
                    {"set_number": 2, "reps": 1, "weight": 92.5},  # 1-rep attempt: exact weight 92.5 > 88.67
                ],
            }
        ],
    )
    assert session2["status"] == "ok"
    assert len(session2["new_prs"]) == 1
    assert session2["new_prs"][0]["exercise"] == "Bench Press"
    assert session2["new_prs"][0]["estimated_1rm"] == 92.5

    # 5. Verify updated PR
    bp_pr_v2 = await hermes_client.call_tool(
        "get_personal_record", exercise_name="Bench Press"
    )
    assert bp_pr_v2["status"] == "ok"
    record2 = bp_pr_v2["personal_record"]
    assert record2["max_weight"] == 92.5
    assert record2["max_reps"] == 1
    assert record2["estimated_1rm"] == 92.5
    assert record2["date"] == "08-05-2026"

    # 6. Read last workout
    last_bp = await hermes_client.call_tool(
        "get_last_workout", exercise_name="Bench Press"
    )
    assert last_bp["status"] == "ok"
    assert last_bp["date"].startswith("08-05-2026")
    assert len(last_bp["sets"]) == 2

    # 7. Query workouts by day
    day1_workouts = await hermes_client.call_tool(
        "get_workouts_by_day", date="01-05-2026"
    )
    assert day1_workouts["status"] == "ok"
    assert day1_workouts["count"] == 1
    assert len(day1_workouts["sessions"][0]["sets"]) == 4


@pytest.mark.anyio
async def test_hermes_provisional_and_fuzzy_adaptive_flows(hermes_client):
    """E2E Scenario: Hermes leverages provisional entries, auto-creation of unknown items, and fuzzy resolution."""
    # 1. Log a meal with an ingredient never seen before -> auto-created as provisional
    meal_res = await hermes_client.call_tool(
        "register_meal",
        date="12-05-2026",
        item_name="Greek Yogurt",
        quantity=200.0,
        unit="gr",
    )
    assert meal_res["status"] == "ok"

    # Verify Greek Yogurt was cataloged as provisional
    ing_list = await hermes_client.call_tool("list_ingredients", search="Greek Yogurt")
    assert ing_list["status"] == "ok"
    assert len(ing_list["ingredients"]) == 1
    assert ing_list["ingredients"][0]["name"] == "Greek Yogurt"
    assert ing_list["ingredients"][0]["provisional"] is True

    # Finalize the ingredient with real macros
    greek_id = ing_list["ingredients"][0]["id"]
    update_res = await hermes_client.call_tool(
        "update_ingredient",
        ingredient_id=greek_id,
        kcal=59.0,
        protein=10.0,
        carbs=3.6,
        fat=0.4,
        price=0.8,
        provisional=False,
    )
    assert update_res["status"] == "ok"
    assert update_res["ingredient"]["provisional"] is False

    # 2. Register workout with unknown exercise -> auto-created
    workout_res = await hermes_client.call_tool(
        "register_workout",
        date="12-05-2026 19:00",
        exercises=[
            {
                "name": "Incline Dumbbell Press",
                "sets": [{"set_number": 1, "reps": 12, "weight": 24.0}],
            }
        ],
    )
    assert workout_res["status"] == "ok"
    assert "Incline Dumbbell Press" in workout_res["auto_created"]

    # Verify auto-created exercise in catalog
    ex_list = await hermes_client.call_tool(
        "list_exercises", search="Incline Dumbbell Press"
    )
    assert ex_list["status"] == "ok"
    assert ex_list["count"] == 1
    assert ex_list["exercises"][0]["muscle_group"] == "unknown"

    # 3. Fuzzy match: query last workout using slightly different casing / spacing
    fuzzy_workout = await hermes_client.call_tool(
        "get_last_workout", exercise_name="incline dumbbell press"
    )
    assert fuzzy_workout["status"] == "ok"
    assert fuzzy_workout["exercise"] == "Incline Dumbbell Press"
    assert fuzzy_workout["sets"][0]["weight"] == 24.0


@pytest.mark.anyio
async def test_hermes_error_resilience_and_typed_envelopes(hermes_client):
    """E2E Scenario: Hermes handles invalid input and missing resources with structured error envelopes."""
    # 1. Invalid date format (ISO YYYY-MM-DD instead of DD-MM-YYYY)
    bad_date = await hermes_client.call_tool(
        "get_workouts_by_day", date="2026-05-12"
    )
    assert bad_date["status"] == "error"
    assert bad_date["code"] == "invalid_input"
    assert "date" in bad_date["message"].lower()

    # 2. Invalid measurement unit
    bad_unit = await hermes_client.call_tool(
        "create_ingredient",
        name="Mystery Juice",
        unit="liters",
        kcal=50.0,
    )
    assert bad_unit["status"] == "error"
    assert bad_unit["code"] == "invalid_input"
    assert "unit" in bad_unit["message"].lower()

    # 3. Empty exercise name
    empty_ex = await hermes_client.call_tool(
        "create_exercise",
        name="   ",
    )
    assert empty_ex["status"] == "error"
    assert empty_ex["code"] == "invalid_input"

    # 4. Duplicate set_number within same workout exercise
    dup_set = await hermes_client.call_tool(
        "register_workout",
        date="12-05-2026",
        exercises=[
            {
                "name": "Pushups",
                "sets": [
                    {"set_number": 1, "reps": 20},
                    {"set_number": 1, "reps": 25},
                ],
            }
        ],
    )
    assert dup_set["status"] == "error"
    assert dup_set["code"] == "invalid_input"

    # 5. Non-existent resource lookups
    ghost_workout = await hermes_client.call_tool(
        "get_last_workout", exercise_name="Phantom Press"
    )
    assert ghost_workout["status"] == "error"
    assert ghost_workout["code"] == "not_found"

    ghost_pr = await hermes_client.call_tool(
        "get_personal_record", exercise_name="Phantom Press"
    )
    assert ghost_pr["status"] == "error"
    assert ghost_pr["code"] == "not_found"

    ghost_ing = await hermes_client.call_tool(
        "update_ingredient", ingredient_id=9999, kcal=100.0
    )
    assert ghost_ing["status"] == "error"
    assert ghost_ing["code"] == "not_found"


@pytest.mark.anyio
async def test_hermes_ui_artifact_flow(hermes_client):
    """E2E Scenario: Hermes requests interactive HTML artifacts to render in chat GUI."""
    # Request default hub artifact
    hub_res = await hermes_client.call_tool("get_ui_form", form_type="hub")
    assert hub_res["status"] == "ok"
    assert hub_res["form_type"] == "hub"
    assert "<!DOCTYPE html>" in hub_res["html"]
    assert "Hermes Hub" in hub_res["html"]

    # Request focused workout form artifact
    workout_res = await hermes_client.call_tool("get_ui_form", form_type="workout")
    assert workout_res["status"] == "ok"
    assert workout_res["form_type"] == "workout"
    assert "Registrar Entrenamiento" in workout_res["html"]

    # Request invalid form type -> typed error
    invalid_res = await hermes_client.call_tool("get_ui_form", form_type="invalid_view")
    assert invalid_res["status"] == "error"
    assert invalid_res["code"] == "invalid_input"


@pytest.mark.anyio
async def test_hermes_google_health_sync_flow(hermes_client, monkeypatch):
    """E2E Scenario: Hermes triggers Google Health bidirectional synchronization over MCP."""
    import httpx2
    from src.config import settings
    from src.services.google_health_client import GoogleHealthClient

    monkeypatch.setattr(settings, "google_health_token", "test-token")

    def mock_handler(request: httpx2.Request) -> httpx2.Response:
        url_str = str(request.url)
        if "/dataTypes/nutrition-log/dataPoints" in url_str:
            return httpx2.Response(200, json={"status": "ok"})
        elif "/dataTypes/sleep/dataPoints" in url_str:
            return httpx2.Response(
                200,
                json={
                    "dataPoints": [
                        {
                            "sleep": {
                                "interval": {
                                    "startTime": "2026-11-10T23:00:00Z",
                                    "endTime": "2026-11-11T07:00:00Z",
                                },
                                "summary": {"minutesAsleep": 480},
                            }
                        }
                    ]
                },
            )
        elif "/dataTypes/weight/dataPoints" in url_str:
            return httpx2.Response(
                200,
                json={
                    "dataPoints": [
                        {
                            "weight": {
                                "sampleTime": {
                                    "physicalTime": "2026-11-11T08:00:00Z",
                                    "utcOffset": "3600s",
                                },
                                "weightGrams": 76000,
                            }
                        }
                    ]
                },
            )
        elif "/dataTypes/steps/dataPoints" in url_str:
            return httpx2.Response(
                200,
                json={
                    "dataPoints": [
                        {
                            "steps": {
                                "count": 10500,
                                "interval": {"startTime": "2026-11-11T12:00:00Z"},
                            }
                        }
                    ]
                },
            )
        return httpx2.Response(404)

    mock_client = httpx2.Client(transport=httpx2.MockTransport(mock_handler))
    orig_init = GoogleHealthClient.__init__

    def patched_init(self, *args, **kwargs):
        orig_init(self, token="test-token", http_client=mock_client)

    monkeypatch.setattr(GoogleHealthClient, "__init__", patched_init)

    # 1. Log a meal
    await hermes_client.call_tool(
        "register_meal",
        date="11-11-2026",
        item_name="Oatmeal",
        quantity=80.0,
        unit="gr",
    )

    # 2. Sync meals to Google Health
    sync_meals_res = await hermes_client.call_tool(
        "sync_meals_to_google_health", date="11-11-2026"
    )
    assert sync_meals_res["status"] == "ok"
    assert sync_meals_res["synced_count"] == 1

    # 3. Fetch sleep
    sleep_res = await hermes_client.call_tool(
        "fetch_google_health_sleep", date="11-11-2026"
    )
    assert sleep_res["status"] == "ok"
    assert sleep_res["count"] == 1
    assert sleep_res["records"][0]["duration_minutes"] == 480.0

    # 4. Fetch weight
    weight_res = await hermes_client.call_tool(
        "fetch_google_health_weight", date="11-11-2026"
    )
    assert weight_res["status"] == "ok"
    assert weight_res["latest_weight_kg"] == 76.0

    # 5. Fetch steps
    steps_res = await hermes_client.call_tool(
        "fetch_google_health_steps", date="11-11-2026"
    )
    assert steps_res["status"] == "ok"
    assert steps_res["steps"] == 10500
    assert steps_res["source"] == "google_health"

    # 6. Full sync
    full_sync = await hermes_client.call_tool(
        "sync_google_health", date="11-11-2026"
    )
    assert full_sync["status"] == "ok"
    assert full_sync["meals_synced"] == 1
    assert full_sync["sleep_sessions_fetched"] == 1
    assert full_sync["weight_records_fetched"] == 0
    assert full_sync["steps_fetched"] == 10500



