# Feature: dockerize-nas-deployment

> Dockerize the Fitness AI application (`Dockerfile`, `docker-compose.yml` for Windows/local build, `docker-compose.nas.yml` + GHCR workflow for UGREEN DXP2800 NAS, `.dockerignore`, and container-ready settings) so it can run on both Windows PC and 24/7 on a NAS with persistent SQLite and Google Health token storage.

## Spec
> What and why (no technology)

### Context
- Currently, the Fitness AI server (`python -m src.main`) runs directly on the user's desktop PC, storing data in `data/fitness.db` and reading configuration from `.env`.
- The user wants to test and run the containerized application both on their **Windows PC** and 24/7 on their **UGREEN NASync DXP2800** (`x86_64` Intel N100 running UGOS Pro).
- For reliable execution on both Windows and UGREEN NAS, the setup must:
  1. Bind to `0.0.0.0` (instead of `127.0.0.1`) inside the container so the Web UI (`/ui`) and MCP/API endpoints (`/mcp`, `/api/*`) are reachable across the local network or Tailscale.
  2. Persist the entire `data/` directory (`fitness.db`, `fitness.db-wal`, `fitness.db-shm` required by SQLite WAL mode, plus refreshed Google Health OAuth tokens `.google_health_token`) on a single mounted volume (`./data:/app/data`).
  3. Provide two Compose configurations:
     - `docker-compose.yml`: Local / Windows PC & NAS local-build configuration (`docker compose up -d --build`) that builds from the local repository and loads `.env`.
     - `docker-compose.nas.yml` + `.github/workflows/docker-publish.yml`: Standalone UGREEN DXP2800 (UGOS Pro → Docker → Project) configuration that pulls the pre-built `ghcr.io/teylor/fitness-ai:latest` image without requiring source code on the NAS.
  4. Disable local `tailscale serve` invocation inside the container by default (`TAILSCALE_SERVE=false`).

### Acceptance Criteria
- [x] C1: **`Dockerfile` & `.dockerignore`**:
  - Uses `python:3.12-slim` (`linux/amd64` native on Windows x64 and UGREEN DXP2800 Intel N100).
  - Installs runtime dependencies from `requirements.txt` (`mcp>=2.0.0`, `peewee`, `httpx2`).
  - Sets `MCP_HOST=0.0.0.0`, `MCP_PORT=9700`, `TAILSCALE_SERVE=false`, `DB_PATH=data/fitness.db`, `TZ=Europe/Madrid`, exposes port `9700`, defines a `HEALTHCHECK` against `/manifest.webmanifest`, and runs `python -m src.main`.
  - `.dockerignore` excludes `.git`, `.venv`, `__pycache__`, `data/*.db*`, `data/.google_health_token`, and `.env`.
- [x] C2: **Dual Compose Configurations (`docker-compose.yml` & `docker-compose.nas.yml`) + GHCR Workflow**:
  - `docker-compose.yml` builds locally (`build: .`), maps `${MCP_PORT:-9700}:9700`, mounts `./data:/app/data`, and loads `.env` (`required: false`) for Windows PC or local NAS builds.
  - `docker-compose.nas.yml` is tailored for UGREEN DXP2800 (`UGOS Pro → Docker → Project`), pulling `ghcr.io/teylor/fitness-ai:latest` built by `.github/workflows/docker-publish.yml`.
- [x] C3: **Container-ready Configuration & Volume Token Persistence (`src/config.py`, `src/services/google_health_client.py`)**:
  - `Settings.db_path` supports `DB_PATH` environment variable (`os.environ.get("DB_PATH", "data/fitness.db")`).
  - `GoogleHealthClient._persist_token` persists refreshed OAuth access tokens to `data/.google_health_token` inside the mounted `/app/data` volume (in addition to `.env` if present), and `src/config.py` loads `data/.google_health_token` on startup so refreshed tokens survive container recreation on the NAS without needing to bind-mount `.env`.
- [x] C4: **Tests & Documentation**:
  - Unit tests in `tests/unit/test_docker_config.py` verify `DB_PATH`, `data/.google_health_token` persistence, and all Docker/NAS artifacts.
  - `docs/specs/openspec/requirements.md` updated (NFR1).

## Clarify
> Resolved ambiguities

- **Q1: Do we need adaptations for the UGREEN NASync DXP2800?**
  - **A**: Yes: (1) persist refreshed Google Health OAuth tokens inside `/app/data/.google_health_token` so only one directory volume (`./data:/app/data`) needs to be mounted in UGOS Pro; (2) provide both `docker-compose.yml` (for testing/running with `build: .` on Windows PC or NAS) and `docker-compose.nas.yml` + GHCR workflow (for pasting directly into UGOS Pro → Docker → Project on the DXP2800).

## Plan
> Technical decisions + classification

- **Classification**: **Substantial** — touches `src/config.py`, `src/services/google_health_client.py`, `requirements.txt`, adds `Dockerfile`, `docker-compose.yml`, `docker-compose.nas.yml`, `.dockerignore`, `.github/workflows/docker-publish.yml`, unit tests, and OpenSpec docs.
- **Execution Mode**: Fast (default).
- **D1 (`src/config.py` & `src/services/google_health_client.py`)**: Add `DB_PATH` env var support and `load_persisted_google_token` reading/writing `data/.google_health_token` in the SQLite data directory.
- **D2 (`Dockerfile` & `.dockerignore`)**: Build clean `python:3.12-slim` image with `HEALTHCHECK` and `VOLUME ["/app/data"]`.
- **D3 (`docker-compose.yml` & `docker-compose.nas.yml` & `.github/workflows/docker-publish.yml`)**: Provide both local-build Compose (Windows PC / local NAS) and GHCR image Compose for UGREEN DXP2800 UGOS Pro.

## Tasks
> Implementation checklist

- [x] T1: Allow `DB_PATH` env override in `src/config.py`, persist/load refreshed Google Health token in `data/.google_health_token`, and pin `mcp>=2.0.0` in `requirements.txt` → verify: `pytest tests/unit/test_docker_config.py -v` → PASSED
- [x] T2: Create `Dockerfile`, `docker-compose.yml` (Windows/local build), `docker-compose.nas.yml` (UGREEN DXP2800), `.dockerignore`, and `.github/workflows/docker-publish.yml` → verify: `pytest tests/unit/test_docker_config.py -v` → PASSED (3 tests)
- [x] T3: Update `docs/specs/openspec/requirements.md` (NFR1) and run full test suite → verify: `pytest tests/ -v` → PASSED (224 tests)

## Verification
> Comparison against the spec (filled in at close)

- **C1 (`Dockerfile` & `.dockerignore`)**: Verified by `test_docker_and_ugreen_nas_artifacts_exist`.
- **C2 (`docker-compose.yml`, `docker-compose.nas.yml`, `.github/workflows/docker-publish.yml`)**: Verified by `test_docker_and_ugreen_nas_artifacts_exist`.
- **C3 (`DB_PATH` & `data/.google_health_token` persistence)**: Verified by `test_settings_respects_db_path_env` and `test_google_health_token_persists_to_data_volume`.
- **C4 (Full test suite & OpenSpec)**: `pytest tests/ -v` → **224 passed**.

## Close
> Close (filled in at close)

- **Date**: 2026-11-18
- **Implemented**: Full Dockerization for both Windows PC (`docker-compose.yml`) and UGREEN DXP2800 NAS (`docker-compose.nas.yml` + GHCR workflow), with persistent `/app/data` storage for SQLite WAL files and refreshed Google Health OAuth tokens.
- **Next step**: Commit on `feat/dockerize-nas-deployment`, push branch, and open PR to `main`.
