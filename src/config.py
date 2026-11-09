"""System configuration and environment settings."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Settings:
    """Global project settings."""

    # Database
    db_path: str = "data/fitness.db"
    migrations_dir: str = "src/db/migrations"

    # MCP Server
    mcp_host: str = "127.0.0.1"
    mcp_port: int = 9700

    # Google Health API
    google_health_api_url: str = os.environ.get(
        "GOOGLE_HEALTH_API_URL", "https://health.googleapis.com/v4"
    )
    google_health_token: Optional[str] = os.environ.get("GOOGLE_HEALTH_ACCESS_TOKEN")

    # Paths
    base_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent)

    @property
    def db_file(self) -> Path:
        return self.base_dir / self.db_path

    @property
    def migrations_path(self) -> Path:
        return self.base_dir / self.migrations_dir


settings = Settings()
