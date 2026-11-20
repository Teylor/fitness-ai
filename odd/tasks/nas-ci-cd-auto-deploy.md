# Feature: nas-ci-cd-auto-deploy

> Full CI/CD pipeline in GitHub Actions: run `pytest` on PRs and pushes to `main`, publish the Docker image to `ghcr.io`, and automatically deploy to the UGREEN DXP2800 NAS via Tailscale + SSH.

## Spec
> What and why (no technology)

### Context
- `.github/workflows/docker-publish.yml` currently builds and pushes the Docker image to `ghcr.io` on pushes to `main`, but does not run the test suite as a CI gate and does not automatically update the running container on the UGREEN DXP2800 NAS.
- The user wants every change merged/pushed to `main` to be tested automatically and immediately deployed to the NAS over Tailscale + SSH.

### Acceptance Criteria
- [x] C1: **CI Test Gate**:
  - `.github/workflows/docker-publish.yml` triggers on `pull_request` to `main`, `push` to `main`, and `workflow_dispatch`.
  - `test` job installs `requirements.txt` on Python 3.12 and runs `pytest tests/ -v`.
- [x] C2: **Docker Image Build & Push (`build-and-push`)**:
  - Runs only on `push` to `main` or `workflow_dispatch`, after `test` succeeds (`needs: test`).
  - Builds and pushes `ghcr.io/teylor/fitness-ai:latest` and `ghcr.io/teylor/fitness-ai:${{ github.sha }}`.
- [x] C3: **Immediate NAS CD via Tailscale + SSH (`deploy-nas`)**:
  - Runs after `build-and-push` (`needs: build-and-push`).
  - Connects the GitHub Actions runner to the user's Tailnet via `tailscale/github-action@v3` using `TS_OAUTH_CLIENT_ID` and `TS_OAUTH_SECRET`.
  - Connects via SSH (`NAS_SSH_PRIVATE_KEY`, `NAS_HOST`, `NAS_USER`) to `NAS_DEPLOY_DIR` on the UGREEN DXP2800, updates the repo if present, pulls the newly published `ghcr.io` image (or builds if only `docker-compose.yml` is present), and recreates the container (`docker compose up -d --remove-orphans`).
- [x] C4: **Tests**:
  - `tests/unit/test_docker_config.py` validates the CI/CD workflow jobs (`test`, `build-and-push`, `deploy-nas`, `tailscale/github-action`).

## Clarify
> Resolved ambiguities

- **Q1: Which CD strategy to use for the NAS?**
  - **A**: Immediate push via Tailscale + SSH from GitHub Actions (using Tailscale OAuth client and SSH key secrets in GitHub).

## Plan
> Technical decisions + classification

- **Classification**: **Small** — updates `.github/workflows/docker-publish.yml`, `tests/unit/test_docker_config.py`, and ODD docs.
- **Execution Mode**: Fast (default).
- **D1**: Keep the workflow file at `.github/workflows/docker-publish.yml` so existing references remain valid, expanding it into 3 sequential jobs: `test` → `build-and-push` → `deploy-nas`.
- **D2**: In `deploy-nas`, use `webfactory/ssh-agent@v0.9.0` + standard `ssh` with `StrictHostKeyChecking=no`, supporting both `docker-compose.nas.yml` (`ghcr.io` pull) and `docker-compose.yml` (`--build`), and pruning dangling images after deploy.

## Tasks
> Implementation checklist

- [x] T1: Update `tests/unit/test_docker_config.py` to assert `test`, `build-and-push`, `deploy-nas`, and `tailscale/github-action` in `.github/workflows/docker-publish.yml` (RED) → verify: `pytest tests/unit/test_docker_config.py -v`
- [x] T2: Implement the 3-stage CI/CD pipeline in `.github/workflows/docker-publish.yml` (GREEN) → verify: `pytest tests/ -v` → PASSED (224 tests)

## Verification
> Comparison against the spec (filled in at close)

- **C1-C4**: Verified `.github/workflows/docker-publish.yml` contains `test` (`pytest tests/ -v`), `build-and-push` (`ghcr.io`), and `deploy-nas` (`tailscale/github-action@v3` + SSH deploy to `NAS_HOST`).
- **Full test suite**: `pytest tests/ -v` → **224 passed**.

## Close
> Close (filled in at close)

- **Date**: 2026-11-20
- **Implemented**: 3-stage CI/CD pipeline (`test` → `build-and-push` → `deploy-nas` via Tailscale + SSH).
- **Next step**: Configure the 6 GitHub Repository Secrets (`TS_OAUTH_CLIENT_ID`, `TS_OAUTH_SECRET`, `NAS_SSH_PRIVATE_KEY`, `NAS_HOST`, `NAS_USER`, `NAS_DEPLOY_DIR`), commit, push, and open PR to `main`.
