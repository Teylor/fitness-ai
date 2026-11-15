"""System configuration and environment settings."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# Paths
base_dir = Path(__file__).resolve().parent.parent

# Load .env file if present
env_file = base_dir / ".env"
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            key, val = key.strip(), val.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = val


@dataclass
class Settings:
    """Global project settings."""

    # Database
    db_path: str = "data/fitness.db"
    migrations_dir: str = "src/db/migrations"

    # MCP Server
    mcp_host: str = os.environ.get("MCP_HOST", "127.0.0.1")
    mcp_port: int = int(os.environ.get("MCP_PORT", "9700"))
    tailscale_serve: bool = os.environ.get("TAILSCALE_SERVE", "true").strip().lower() not in (
        "0",
        "false",
        "no",
    )

    # Google Health API
    google_health_api_url: str = os.environ.get(
        "GOOGLE_HEALTH_API_URL", "https://health.googleapis.com/v4"
    )
    google_health_token: Optional[str] = os.environ.get("GOOGLE_HEALTH_ACCESS_TOKEN")
    google_health_refresh_token: Optional[str] = os.environ.get("GOOGLE_HEALTH_REFRESH_TOKEN")
    google_client_id: Optional[str] = os.environ.get("GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = os.environ.get("GOOGLE_CLIENT_SECRET")

    # Paths
    base_dir: Path = field(default_factory=lambda: base_dir)

    @property
    def db_file(self) -> Path:
        return self.base_dir / self.db_path

    @property
    def migrations_path(self) -> Path:
        return self.base_dir / self.migrations_dir


settings = Settings()
