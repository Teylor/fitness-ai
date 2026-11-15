"""Entry point for the MCP Server."""

from pathlib import Path
import shutil
import subprocess
from typing import Optional

from src.config import settings
from src.db.connection import init_db
from src.mcp.server import create_server

_WINDOWS_TAILSCALE_PATHS = (
    Path(r"C:\Program Files\Tailscale\tailscale.exe"),
    Path(r"C:\Program Files (x86)\Tailscale\tailscale.exe"),
)


def _find_tailscale_cli() -> Optional[str]:
    """Locate tailscale CLI in PATH or standard Windows install directories."""
    found = shutil.which("tailscale")
    if found:
        return found
    for candidate in _WINDOWS_TAILSCALE_PATHS:
        if candidate.is_file():
            return str(candidate)
    return None


def ensure_tailscale_serve(port: int) -> bool:
    """Best-effort: expose the given local port via `tailscale serve --bg <port>`."""
    if not settings.tailscale_serve:
        return False
    cli = _find_tailscale_cli()
    if not cli:
        print("[tailscale] CLI not found in PATH; skipping tailscale serve")
        return False
    try:
        res = subprocess.run(
            [cli, "serve", "--bg", str(port)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if res.returncode == 0:
            print(f"[tailscale] Serving port {port} over HTTPS (tailscale serve --bg {port})")
            if res.stdout and res.stdout.strip():
                print(res.stdout.strip())
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
