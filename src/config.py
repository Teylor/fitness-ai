"""Configuración del sistema."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Settings:
    """Settings globales del proyecto."""

    # Base de datos
    db_path: str = "data/fitness.db"
    migrations_dir: str = "src/db/migrations"

    # MCP Server
    mcp_host: str = "127.0.0.1"
    mcp_port: int = 9700

    # Paths
    base_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent.parent)

    @property
    def db_file(self) -> Path:
        return self.base_dir / self.db_path

    @property
    def migrations_path(self) -> Path:
        return self.base_dir / self.migrations_dir


settings = Settings()