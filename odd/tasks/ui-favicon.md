# Task: UI Browser Tab Favicon (`ui-favicon`)

## 1. SPECIFY (What & Why)
- **Goal**: Add the user-provided `favicon.jpg` (2048x2048) as the browser tab favicon and touch icon for the Fitness AI Web UI, optimized to standard web icon sizes.
- **Why**: Currently `/ui` has no `<link rel="icon">` tags and `/favicon.ico` returns 404, leaving a generic browser tab icon. Serving a 2048x2048 JPEG directly is unnecessarily heavy (~hundreds of KB vs a few KB).

## 2. CLARIFY (Decisions & Formats)
- Generate optimized PNG sizes using high-quality bicubic resampling (`src/ui/assets/`):
  - `favicon-16x16.png` (16x16)
  - `favicon-32x32.png` (32x32)
  - `favicon-48x48.png` (48x48)
  - `apple-touch-icon.png` (180x180)
  - `favicon.ico` (multi-resolution ICO bundling 16x16, 32x32, and 48x48 PNG entries)
- Serve `/favicon.ico`, `/favicon-32x32.png`, and `/apple-touch-icon.png` from `src/mcp/server.py` with `Cache-Control: public, max-age=86400`.
- Reference them in the `<head>` of `src/ui/html_generator.py`.

## 3. PLAN (Technical Changes)
1. Resize `favicon.jpg` into `src/ui/assets/` (`favicon-32x32.png`, `apple-touch-icon.png`, and multi-size `favicon.ico`).
2. Add Starlette routes in `src/mcp/server.py` for `/favicon.ico`, `/favicon-32x32.png`, and `/apple-touch-icon.png`.
3. Add `<link rel="icon">` and `<link rel="apple-touch-icon">` tags in `src/ui/html_generator.py`.
4. Add integration tests in `tests/integration/test_ui_web_routes.py` verifying HTML `<head>` links and HTTP `200` responses with proper `Content-Type` headers.

## 4. TASKS
- [x] Create `odd/tasks/ui-favicon.md` and update `odd/BACKLOG.md`.
- [x] Resize `favicon.jpg` into optimal web icon assets under `src/ui/assets/`.
- [x] Serve favicon routes in `src/mcp/server.py` and add `<link>` tags in `src/ui/html_generator.py`.
- [x] Add integration tests in `tests/integration/test_ui_web_routes.py` and run full pytest suite.

## 5. Verification
- **Tests**: Full pytest suite passing (`189 passed`).
- **Asset sizes**: `favicon.ico` (16/32/48px), `favicon-32x32.png` (32x32px), and `apple-touch-icon.png` (180x180px) served with HTTP 200.
