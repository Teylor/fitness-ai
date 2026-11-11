# Task: Fix Steps Discrepancy (`fix-steps`)

## 1. SPECIFY (What & Why)
- **Problem**: The step count displayed in the local dashboard (`119` steps on `11-11-2026`) does not match the step count shown in Google Health / Fitbit (~`4647` steps).
- **Root Cause Analysis**:
  1. `GoogleHealthClient.get_steps_datapoints()` queries `GET /users/me/dataTypes/steps/dataPoints` without `pageSize` and without `:reconcile`.
     - Raw `steps/dataPoints` returns minute-level intervals with a tiny default page size of **11 dataPoints** (which summed to `119` steps on the first page) and truncates the rest behind `nextPageToken`.
     - Raw `steps/dataPoints` also contains overlapping multi-source records (`Fitbit Air`, `MobileTrack`, and `Nothing Phone` via Health Connect), which would double/triple count if summed naively.
  2. Google Health API v4 provides `GET /users/me/dataTypes/steps/dataPoints:reconcile`, which deduplicates and reconciles overlapping step intervals across all connected devices. Passing `pageSize=1440` retrieves the full day's minute-level reconciled intervals in a single request.
  3. `GoogleHealthService.fetch_steps()` prioritized UTC `interval.startTime` over `interval.civilStartTime.date`, causing steps recorded between `00:00` and `01:00`/`02:00` local time to be bucketed into the previous UTC date.

## 2. CLARIFY (Decisions & Edge Cases)
- **Endpoint**: Use `/users/me/dataTypes/steps/dataPoints:reconcile` with `params={"pageSize": 1440}`.
- **Date Attribution**: Prefer `interval.civilStartTime.date` (`{"year", "month", "day"}`) when present to bucket steps into the user's local calendar date (`DD-MM-YYYY`), falling back to `interval.startTime` ISO parsing when `civilStartTime` is omitted (preserving backwards compatibility with existing unit test fixtures).

## 3. PLAN (Technical Changes)
1. **`src/services/google_health_client.py`**:
   - Update `get_steps_datapoints(self, page_size: int = 1440)` to call `GET {self.base_url}/users/me/dataTypes/steps/dataPoints:reconcile` with `params={"pageSize": page_size}`.
2. **`src/services/google_health_service.py`**:
   - Update `fetch_steps()` to inspect `interval.get("civilStartTime")`: if it is a dictionary containing `"date": {"year", "month", "day"}`, format `pt_date` directly as `DD-MM-YYYY`; otherwise fall back to `interval.get("startTime")`.
3. **`tests/unit/test_google_health_service.py`**:
   - Add unit test verifying `:reconcile` endpoint with `pageSize=1440` and `civilStartTime.date` local date bucketing.

## 4. TASKS
- [x] Create `odd/tasks/fix-steps.md` and update `odd/BACKLOG.md` (including `sync-optimization` in Proposed).
- [x] Update `GoogleHealthClient.get_steps_datapoints()` in `src/services/google_health_client.py` to use `:reconcile` and `pageSize=1440`.
- [x] Update `GoogleHealthService.fetch_steps()` in `src/services/google_health_service.py` to prioritize `civilStartTime.date`.
- [x] Add unit test in `tests/unit/test_google_health_service.py` and run full pytest suite.
- [x] Verify live sync for `11-11-2026` updates the local database with reconciled steps and restart server on port `9700`.

## 5. Verification
- **Unit Tests**: Full pytest suite passing (`185 passed`).
- **Live API Check**: `GoogleHealthService().fetch_steps("11-11-2026")` retrieves reconciled data points via `:reconcile?pageSize=1440` and stores the reconciled step count (`4462`+ steps instead of `119`).
