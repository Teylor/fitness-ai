# Task: Google Health Sync Optimization (`sync-optimization`)

## 1. SPECIFY (What & Why)
- **Problem**: Synchronization with Google Health API (`sync_meals`, `sync_all`, and auto-sync during `register_meal` / `delete_meal`) suffers from high latency and redundant I/O:
  1. `GoogleHealthClient` opens and closes a new `httpx2.Client` (full TCP + TLS handshake) for every single HTTP request.
  2. `GoogleHealthService.sync_meals()` performs N+1 SQLite queries per meal, uploads 0-kcal supplements as nutrition logs, and sends `POST` requests sequentially one by one.
  3. `GoogleHealthService.sync_all()` executes nutrition, sleep, weight, and steps network requests sequentially instead of concurrently.
  4. `fetch_sleep()` and `fetch_steps()` unconditionally rewrite unchanged historical rows in SQLite on every sync.
  5. Adding or deleting a meal from the Web UI blocks on full cloud synchronization before updating the UI.

## 2. CLARIFY (Decisions & Scope)
- **Scope**: Full optimization selected by user:
  1. Persistent HTTP connection pooling (`keep-alive`) and thread-safe token refresh in `GoogleHealthClient`.
  2. Parallel network I/O (`ThreadPoolExecutor`) in `sync_all()` and concurrent `POST` uploads in `sync_meals()`, while keeping SQLite persistence on the calling thread for thread safety with `:memory:` and file databases.
  3. Eliminate N+1 queries in `sync_meals()`, skip 0-kcal supplements (`is_supplement=True` with 0 macros/kcal), and skip redundant SQLite `.save()` calls when `SleepLog` / `StepLog` records have not changed.
  4. Non-blocking background auto-sync (`async_sync=True`) with per-date coalescing for Web UI meal registration/deletion, while keeping synchronous behavior (`async_sync=False` default) for direct MCP tool calls and existing integration tests.

## 3. PLAN (Technical Changes)
1. **`src/services/google_health_client.py`**:
   - Add a shared persistent `httpx2.Client` connection pool for default client instances and a `threading.Lock` around OAuth token refresh.
2. **`src/services/google_health_service.py`**:
   - Batch-prefetch `IngredientModel` and `RecipeModel` records in `sync_meals()`.
   - Exclude zero-calorie/zero-macro supplements (`is_supplement=True` and `kcal == 0`) from Google Health `nutrition-log` uploads.
   - Post meal datapoints concurrently using `ThreadPoolExecutor`.
   - Prefetch `nutrition-log`, `sleep`, `weight`, and `steps` endpoints concurrently in `sync_all()`.
   - Add dirty checks before `.save()` in `fetch_sleep()` and `fetch_steps()`.
3. **`src/mcp/tools/meal_tools.py` & `src/ui/html_generator.py`**:
   - Add coalesced background sync worker `_schedule_meal_sync(date)` and `async_sync: bool = False` parameter to `register_meal()` and `delete_meal()`.
   - Pass `async_sync: true` from UI `submitMeal` and `deleteMeal` handlers and include `steps_fetched` in the `syncGoogleHealthUI` toast summary.
4. **`tests/unit/test_google_health_service.py`**:
   - Add unit tests covering connection reuse, 0-kcal supplement filtering in `sync_meals`, concurrent `sync_all`, and coalesced background meal sync.

## 4. TASKS
- [x] Create `odd/tasks/sync-optimization.md` and update `odd/BACKLOG.md`.
- [x] Optimize `GoogleHealthClient` with persistent HTTP connection pooling and thread-safe token refresh.
- [x] Optimize `GoogleHealthService` (`sync_meals` batch query + 0-kcal supplement skip + concurrent POSTs, parallel `sync_all` HTTP prefetch, and dirty-checked DB saves).
- [x] Add coalesced background auto-sync (`async_sync`) to `meal_tools.py` and enable it in `html_generator.py`.
- [x] Add unit tests in `tests/unit/test_google_health_service.py` and verify full pytest suite passes.

## 5. Verification
- **Unit & Integration Tests**: Full pytest suite passing (`188 passed`).
- **Performance**: Persistent `httpx2.Client` reuses connections across calls, `sync_all` runs HTTP fetches in parallel, and UI meal registration/deletion returns immediately via coalesced background sync.
