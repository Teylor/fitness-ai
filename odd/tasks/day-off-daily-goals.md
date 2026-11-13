# Task: Day Off Daily Goals Toggle (`day-off-daily-goals`)

## 1. SPECIFY (What & Why)
- **Goal**: Allow users to configure a separate set of daily macro/calorie targets for rest days ("Day Off") and toggle any specific date between Training Day and Day Off targets from the Daily Summary UI or MCP tools.
- **Why**: Users often eat different calories/carbohydrates on rest days vs training days. Previously `daily_goals` only supported a single global default goal.

## 2. CLARIFY (Decisions & Edge Cases)
- **Two Global Profiles**:
  - Training Day default (`is_default=True`)
  - Day Off default (`is_day_off_default=True`, stored under sentinel date `"01-01-1900"` by default so it never collides with real dates)
- **Per-Date Toggle**:
  - `toggle_day_off(date, is_day_off=None)` enables or disables Day Off for a specific date (`DD-MM-YYYY`).
  - When enabled (`is_day_off=True`), creates/updates the date row in `daily_goals` with the Day Off default macros and `is_day_off=True`.
  - When disabled (`is_day_off=False`), removes the Day Off override for that date so `get_goal(date)` falls back cleanly to the Training Day goal chain.
  - `get_goal(date)` ignores `is_day_off=True` and `is_day_off_default=True` rows when resolving past-date fallbacks for normal days so a single Day Off never leaks into subsequent days.

## 3. PLAN (Technical Changes)
1. **Migration (`006_day_off_goals.sql`) & Models**:
   - Add `is_day_off` and `is_day_off_default` boolean columns to `daily_goals`.
2. **Services (`GoalService`, `MealService`)**:
   - Add `set_day_off_default()`, `toggle_day_off()`, and `get_goal_profiles()` in `GoalService`.
   - Include `is_day_off` in `goal` and `goal_profiles` in `MealService.get_day_summary()`.
3. **MCP Tools (`goal_tools.py`, `server.py`)**:
   - Extend `set_daily_goal` with `day_off_default` and `is_day_off`.
   - Add and register `toggle_day_off` MCP tool.
   - Include `profiles` in `get_daily_goal`.
4. **Web UI (`html_generator.py`)**:
   - Add Day Off toggle button and collapsible `⚙️ Objetivos` configuration panel (Training Day vs Day Off targets) in `📊 Resumen Diario`.
5. **Tests**:
   - Add unit and integration tests for `GoalService`, `goal_tools`, `test_mcp_server`, and `test_ui_web_routes`.

## 4. TASKS
- [x] Create `odd/tasks/day-off-daily-goals.md` and update `odd/BACKLOG.md`.
- [x] Add DB migration `006_day_off_goals.sql` and update `DailyGoal` ORM and domain models.
- [x] Implement `set_day_off_default`, `toggle_day_off`, `get_goal_profiles`, and fallback isolation in `GoalService` and `MealService`.
- [x] Expose `toggle_day_off` and `day_off_default` in `goal_tools.py` and `server.py`.
- [x] Add Day Off toggle and goal profile editor in `src/ui/html_generator.py`.
- [x] Add unit & integration tests and verify full pytest suite passes.

## 5. Verification
- **Tests**: Full pytest suite passing (`193 passed`).
- **UI & API**: Verified `/ui/summary` renders Day Off toggle + goal profile config panel and `/api/toggle_day_off` switches daily targets immediately.
