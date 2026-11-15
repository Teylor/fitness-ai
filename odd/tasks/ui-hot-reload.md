# ui-hot-reload

> Feature: ui-hot-reload

## Spec

### Context
`src/mcp/server.py` and `src/mcp/tools/ui_tools.py` import `generate_html` from `src.ui.html_generator` at server startup. Because `src/main.py` runs `server.run()` without process reload, edits to `src/ui/html_generator.py` do not take effect on browser refresh until the user manually restarts the MCP server.

### Objective
Automatically reload `src.ui.html_generator` when its source file changes on disk so browser refreshes on `/ui` (and `/ui/{form_type}` / `get_ui_form`) immediately serve the updated UI without restarting the MCP server.

### Acceptance Criteria
- [x] C1: `render_latest_html(form_type)` (in `src/ui/__init__.py`) checks the `mtime_ns` of `src/ui/html_generator.py` under a lock and calls `importlib.reload(html_generator)` whenever the file modification time changes.
- [x] C2: `/ui`, `/ui/{form_type}` in `src/mcp/server.py` and `get_ui_form` in `src/mcp/tools/ui_tools.py` use `render_latest_html`.
- [x] C3: Integration/unit test verifies `importlib.reload` is triggered when `mtime_ns` changes and skipped when unchanged; full `pytest tests -q` green.

## Clarify
- Reloading only when `st_mtime_ns` changes avoids unnecessary reload overhead on normal requests while guaranteeing immediate pickup on file save.
- A `threading.Lock` protects concurrent `/ui` requests during `importlib.reload`.

## Plan
- **T1**: Add RED test in `tests/integration/test_ui_web_routes.py` for `render_latest_html` hot-reload behavior on `/ui`.
- **T2**: Implement `render_latest_html` in `src/ui/__init__.py` and wire it in `src/mcp/server.py` and `src/mcp/tools/ui_tools.py`.
- **T3**: Run full `pytest tests -q` and close `odd/tasks/ui-hot-reload.md` & `odd/BACKLOG.md`.

## Tasks
- [x] T1: Add hot-reload test in `tests/integration/test_ui_web_routes.py` (RED)
- [x] T2: Implement `render_latest_html` in `src/ui/__init__.py` and wire in `server.py` + `ui_tools.py` (GREEN)
- [x] T3: Verify full `pytest tests -q` and close ODD docs

## Verification
- **Tests**: Full pytest suite passing (`216 passed in 3.21s`), including `test_ui_hot_reload_on_mtime_change`.
- **Hot-reload**: `render_latest_html()` reloads `src.ui.html_generator` only when `st_mtime_ns` changes (thread-safe via `_RELOAD_LOCK`).

## Close
- Closed 2026-11: T1–T3 ✅ and Verification filled.
- Backlog item moved to Done; branch `feat/ui-hot-reload` committed and pushed.
