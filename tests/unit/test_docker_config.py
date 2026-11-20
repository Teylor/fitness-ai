"""Unit tests for Docker / NAS deployment configuration and artifacts."""

from pathlib import Path

from src.config import Settings, base_dir, load_persisted_google_token
from src.services.google_health_client import GoogleHealthClient


def test_settings_respects_db_path_env(monkeypatch):
    monkeypatch.setenv("DB_PATH", "/app/data/custom_fitness.db")
    s = Settings(db_path="/app/data/custom_fitness.db")
    assert str(s.db_file).endswith("custom_fitness.db")


def test_google_health_token_persists_to_data_volume(tmp_path, monkeypatch):
    fake_db = tmp_path / "data" / "fitness.db"
    fake_db.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("src.config.settings.db_path", str(fake_db))
    monkeypatch.setattr("src.config.settings.base_dir", tmp_path)

    client = GoogleHealthClient(token="initial-token")
    client._persist_token("refreshed-nas-token-123")

    token_file = fake_db.parent / ".google_health_token"
    assert token_file.is_file()
    assert token_file.read_text(encoding="utf-8").strip() == "refreshed-nas-token-123"
    assert load_persisted_google_token(fake_db.parent) == "refreshed-nas-token-123"


def test_docker_and_ugreen_nas_artifacts_exist():
    dockerfile = base_dir / "Dockerfile"
    compose_local = base_dir / "docker-compose.yml"
    compose_nas = base_dir / "docker-compose.nas.yml"
    dockerignore = base_dir / ".dockerignore"
    gh_workflow = base_dir / ".github" / "workflows" / "docker-publish.yml"

    assert dockerfile.is_file()
    df_text = dockerfile.read_text(encoding="utf-8")
    assert "FROM python:3.12-slim" in df_text
    assert "MCP_HOST=0.0.0.0" in df_text
    assert "MCP_PORT=9700" in df_text
    assert "TAILSCALE_SERVE=false" in df_text
    assert "EXPOSE 9700" in df_text
    assert "HEALTHCHECK" in df_text

    assert compose_local.is_file()
    cl_text = compose_local.read_text(encoding="utf-8")
    assert "build:" in cl_text
    assert "./data:/app/data" in cl_text
    assert ":9700" in cl_text

    assert compose_nas.is_file()
    cn_text = compose_nas.read_text(encoding="utf-8")
    assert "ghcr.io/" in cn_text
    assert "/app/data" in cn_text
    assert "UGREEN" in cn_text or "DXP2800" in cn_text

    assert dockerignore.is_file()
    di_text = dockerignore.read_text(encoding="utf-8")
    assert "data/*.db*" in di_text
    assert ".env" in di_text

    assert gh_workflow.is_file()
    wf_text = gh_workflow.read_text(encoding="utf-8")
    assert "ghcr.io" in wf_text
