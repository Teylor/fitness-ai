"""Entry point del MCP Server."""

from src.config import settings
from src.db.connection import init_db
from src.mcp.server import create_server


def main():
    """Inicia el MCP server local."""
    init_db()
    server = create_server()
    server.run()


if __name__ == "__main__":
    main()