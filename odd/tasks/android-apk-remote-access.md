# android-apk-remote-access

> Feature: android-apk-remote-access (PWA + Tailscale remote access, ref: `docs/architecture/ssd-decisions.md#adr-003-mobile-access-strategy-android-apk--remote-api`)

## Spec

### Context
Currently, the Fitness AI dashboard (`/ui`) and API (`/api/*`) only listen on `127.0.0.1:9700` (`src/config.py`), have no Web App Manifest or Service Worker for mobile installation, and have no documented remote access setup. The user wants to access and install the dashboard on Android from outside the home network using **Tailscale** as the private encrypted network and **PWA** (installable from Chrome on Android) as the mobile app format.

### Objective
Make the Fitness AI dashboard installable on Android as a **Progressive Web App (PWA)** and reachable securely over **Tailscale** (`tailscale serve` for automatic HTTPS `https://<machine>.<tailnet>.ts.net/ui`, or configurable `MCP_HOST` / `MCP_PORT`), without duplicating frontend code or exposing the server to the public internet.

### Acceptance Criteria
- [x] C1: `src/config.py` reads `MCP_HOST` (default `"127.0.0.1"`) and `MCP_PORT` (default `9700`) from environment variables / `.env`.
- [x] C2: `src/mcp/server.py` serves:
  - `GET /manifest.webmanifest` (`application/manifest+json`) with app name (`Fitness AI`), `start_url: "/ui"`, `display: "standalone"`, `theme_color`, `background_color`, and PWA icons (`192x192` / `512x512` PNGs in `src/ui/assets/`).
  - `GET /sw.js` (`application/javascript`, `Service-Worker-Allowed: /`) providing a minimal network-first/pass-through Service Worker required for Chrome Android PWA installability (never serving stale `/api/*` data).
  - `GET /icon-192.png` and `GET /icon-512.png` from `src/ui/assets/`.
- [x] C3: `src/ui/html_generator.py` includes:
  - `<link rel="manifest" href="/manifest.webmanifest">`, `<meta name="theme-color" content="#0f172a">`, `<meta name="mobile-web-app-capable" content="yes">`, and `<meta name="apple-mobile-web-app-capable" content="yes">`.
  - Service Worker registration script (`if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js')`).
  - Mobile-friendly viewport & touch ergonomics verified (no horizontal overflow on mobile widths).
- [x] C4: Documentation (`docs/setup/tailscale-pwa.md` or `README.md` section + `.env.example` if present) explains the step-by-step setup:
  - Installing Tailscale on Windows & Android.
  - Exposing local port `9700` with HTTPS via `tailscale serve --bg 9700` (so Chrome treats the origin as secure and enables PWA install).
  - Installing the PWA from Chrome on Android ("Add to Home screen" / "Install app").
- [x] C5: Integration tests in `tests/integration/test_ui_web_routes.py` verify `/manifest.webmanifest`, `/sw.js`, `/icon-192.png`, `/icon-512.png`, and manifest/SW registration tags in `/ui`; full `pytest tests -q` green.

## Clarify
- **Network / Remote Access**: **Tailscale** (`tailscale serve --bg 9700` provides automatic HTTPS `https://<host>.ts.net` over the private tailnet; no public internet exposure, no domain purchase, no extra backend auth needed).
- **Mobile Format**: **PWA** (installable on Android via Chrome, zero Android SDK/APK build overhead).
- **Same-origin API calls**: Because the PWA is served from `https://<host>.ts.net/ui`, all existing relative `/api/*` calls remain same-origin and require no CORS or `API_BASE_URL` changes.
- **Caching**: Service Worker must NOT cache `/api/*` responses (pass-through / network-only for `/api/*`) so daily summaries, workouts, and meals are always live.

## Plan
- **T1**: Add `MCP_HOST` / `MCP_PORT` env configuration in `src/config.py` (+ unit test if needed).
- **T2**: Add PWA icon assets (`icon-192.png`, `icon-512.png` generated from `apple-touch-icon.png` or `favicon`) in `src/ui/assets/`, plus `/manifest.webmanifest`, `/sw.js`, `/icon-192.png`, `/icon-512.png` routes in `src/mcp/server.py`.
- **T3**: Wire manifest `<link>`, theme meta tags, and `serviceWorker.register('/sw.js')` in `src/ui/html_generator.py`.
- **T4**: Add integration tests in `tests/integration/test_ui_web_routes.py` and Tailscale + PWA setup guide (`docs/setup/tailscale-pwa.md`).
- **T5**: Update OpenSpec (`docs/specs/openspec/api-spec.md` / `requirements.md`), run full `pytest tests -q`, and close task + `odd/BACKLOG.md`.

## Tasks
- [x] T1: Configurable `MCP_HOST` / `MCP_PORT` in `src/config.py`
- [x] T2: PWA assets (`icon-192.png`, `icon-512.png`) + routes (`/manifest.webmanifest`, `/sw.js`, icons) in `src/mcp/server.py`
- [x] T3: PWA meta tags + SW registration in `src/ui/html_generator.py`
- [x] T4: Integration tests + Tailscale/PWA setup guide (`docs/setup/tailscale-pwa.md`)
- [x] T5: OpenSpec docs, full `pytest tests -q`, and ODD close

## Verification
- **Tests**: Full pytest suite passing (`210 passed in 3.05s`), including `test_ui_pwa_manifest_sw_and_icons` in `tests/integration/test_ui_web_routes.py`.
- **PWA**: `/manifest.webmanifest`, `/sw.js` (network-only for `/api/*`), `/icon-192.png`, `/icon-512.png` served and linked in `/ui`.

## Close
- Closed 2026-11: T1–T5 ✅ and Verification filled.
- Backlog item moved to Done; branch `feat/android-apk-remote-access` committed and pushed.
