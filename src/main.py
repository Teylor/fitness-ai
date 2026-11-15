"""Entry point for the MCP Server."""

import shutil
import subprocess

from src.config import settings
from src.db.connection import init_db
from src.mcp.server import create_server


def ensure_tailscale_serve(port: int) -> bool:
    """Best-effort: expose the given local port via `tailscale serve --bg <port>`."""
    if not settings.tailscale_serve:
        return False
    if not shutil.which("tailscale"):
        return False
    try:
        res = subprocess.run(
            ["tailscale", "serve", "--bg", str(port)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if res.returncode == 0:
            print(f"[tailscale] Serving port {port} over HTTPS (tailscale serve --bg {port})")
            return True
        err = (res.stderr or res.stdout or "").strip()
        print(f"[tailscale] Warning: could not enable serve on port {port}: {err}")
    except Exception as exc:
        print(f"[tailscale] Warning: failed to run tailscale serve: {exc}")
    return False


def main():
    """Start the local MCP server with streamable-http transport."""
    init_db()
    ensure_tailscale_serve(settings.mcp_port)
    server = create_server()
    server.run(
        transport="streamable-http",
        host=settings.mcp_host,
        port=settings.mcp_port,
    )


if __name__ == "__main__":
    main()
