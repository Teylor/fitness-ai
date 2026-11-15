"""Unit tests for src.main Tailscale serve startup hook."""

from unittest.mock import MagicMock, patch

from src.main import ensure_tailscale_serve


def test_ensure_tailscale_serve_runs_when_available():
    mock_res = MagicMock(returncode=0, stdout="", stderr="")
    with (
        patch("src.main.settings.tailscale_serve", True),
        patch("src.main.shutil.which", return_value="C:\\Program Files\\Tailscale\\tailscale.exe"),
        patch("src.main.subprocess.run", return_value=mock_res) as mock_run,
    ):
        assert ensure_tailscale_serve(9700) is True
        mock_run.assert_called_once_with(
            ["tailscale", "serve", "--bg", "9700"],
            capture_output=True,
            text=True,
            timeout=10,
        )


def test_ensure_tailscale_serve_skips_when_missing():
    with (
        patch("src.main.settings.tailscale_serve", True),
        patch("src.main.shutil.which", return_value=None),
        patch("src.main.subprocess.run") as mock_run,
    ):
        assert ensure_tailscale_serve(9700) is False
        mock_run.assert_not_called()


def test_ensure_tailscale_serve_handles_failure_gracefully():
    with (
        patch("src.main.settings.tailscale_serve", True),
        patch("src.main.shutil.which", return_value="tailscale"),
        patch("src.main.subprocess.run", side_effect=OSError("boom")),
    ):
        assert ensure_tailscale_serve(9700) is False


def test_ensure_tailscale_serve_respects_disabled_setting():
    with (
        patch("src.main.settings.tailscale_serve", False),
        patch("src.main.shutil.which") as mock_which,
    ):
        assert ensure_tailscale_serve(9700) is False
        mock_which.assert_not_called()
