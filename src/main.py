"""Entry point for the MCP Server."""

from src.config import settings
from src.db.connection import init_db
from src.mcp.server import create_server


def main():
    """Start the local MCP server with streamable-http transport."""
    init_db()
    server = create_server()
    server.run(
        transport="streamable-http",
        host=settings.mcp_host,
        port=settings.mcp_port,
    )


if __name__ == "__main__":
    main()
