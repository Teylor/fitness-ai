"""Google Health API (v4) HTTP client."""

from typing import Any, Dict, List, Optional
import httpx2

from src.config import settings
from src.utils.errors import ValidationError


class GoogleHealthClient:
    """REST Client for Google Health API (v4)."""

    def __init__(
        self,
        token: Optional[str] = None,
        base_url: Optional[str] = None,
        http_client: Optional[httpx2.Client] = None,
        refresh_token: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ):
        self.token = token if token is not None else settings.google_health_token
        self.refresh_token = (
            refresh_token
            if refresh_token is not None
            else settings.google_health_refresh_token
        )
        self.client_id = (
            client_id if client_id is not None else settings.google_client_id
        )
        self.client_secret = (
            client_secret
            if client_secret is not None
            else settings.google_client_secret
        )
        self.base_url = (base_url or settings.google_health_api_url).rstrip("/")
        self._http_client = http_client

    def _ensure_authenticated(self) -> str:
        if not self.token:
            if self.refresh_token and self.client_id and self.client_secret:
                refreshed = self.refresh_access_token()
                if refreshed:
                    return refreshed
            raise ValidationError(
                "Missing Google Health credentials. Set GOOGLE_HEALTH_ACCESS_TOKEN environment variable."
            )
        return self.token

    def refresh_access_token(self) -> Optional[str]:
        """Request a fresh access_token using refresh_token and client credentials."""
        if not (self.refresh_token and self.client_id and self.client_secret):
            return None
        url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }
        try:
            client = self._http_client or httpx2.Client(timeout=10.0)
            close_client = self._http_client is None
            try:
                resp = client.post(url, data=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    new_token = data.get("access_token")
                    if new_token:
                        self.token = new_token
                        self._persist_token(new_token)
                        return new_token
            finally:
                if close_client:
                    client.close()
        except Exception:
            pass
        return None

    def _persist_token(self, token: str) -> None:
        try:
            env_file = settings.base_dir / ".env"
            if env_file.exists():
                lines = [
                    l
                    for l in env_file.read_text(encoding="utf-8").splitlines()
                    if not l.startswith("GOOGLE_HEALTH_ACCESS_TOKEN=")
                ]
                lines.append(f"GOOGLE_HEALTH_ACCESS_TOKEN={token}")
                env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        except Exception:
            pass

    def _get_headers(self) -> Dict[str, str]:
        token = self._ensure_authenticated()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(
        self,
        method: str,
        url: str,
        json: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> httpx2.Response:
        headers = self._get_headers()
        client = self._http_client or httpx2.Client(timeout=10.0)
        close_client = self._http_client is None

        try:
            resp = client.request(
                method, url, json=json, params=params, headers=headers
            )
            if resp.status_code == 401 and self.refresh_access_token():
                headers = self._get_headers()
                resp = client.request(
                    method, url, json=json, params=params, headers=headers
                )
            return resp
        finally:
            if close_client:
                client.close()

    def post_nutrition_datapoint(self, data_point: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a nutrition dataPoint to Google Health API via nutrition-log."""
        url = f"{self.base_url}/users/me/dataTypes/nutrition-log/dataPoints"
        resp = self._request("POST", url, json=data_point)
        if resp.status_code not in (200, 201, 202):
            raise ValidationError(
                f"Google Health API error ({resp.status_code}): {resp.text}"
            )
        return resp.json() if resp.text else {"status": "ok"}

    def _get_datapoints(self, data_type: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/users/me/dataTypes/{data_type}/dataPoints"
        resp = self._request("GET", url)
        if resp.status_code != 200:
            raise ValidationError(
                f"Google Health API error ({resp.status_code}): {resp.text}"
            )
        data = resp.json()
        return data.get("dataPoints", []) if isinstance(data, dict) else data

    def get_sleep_datapoints(self) -> List[Dict[str, Any]]:
        """Fetch sleep dataPoints from Google Health API."""
        return self._get_datapoints("sleep")

    def get_steps_datapoints(self) -> List[Dict[str, Any]]:
        """Fetch step count dataPoints from Google Health API."""
        return self._get_datapoints("steps")

    def get_weight_datapoints(self) -> List[Dict[str, Any]]:
        """Fetch weight body measurement dataPoints from Google Health API."""
        return self._get_datapoints("weight")

    def get_nutrition_datapoints(self) -> List[Dict[str, Any]]:
        """Fetch nutrition-log dataPoints from Google Health API."""
        return self._get_datapoints("nutrition-log")

    def batch_delete_datapoints(self, data_type: str, names: List[str]) -> Dict[str, Any]:
        """Delete dataPoints by resource names using batchDelete."""
        url = f"{self.base_url}/users/me/dataTypes/{data_type}/dataPoints:batchDelete"
        payload = {"names": names}
        resp = self._request("POST", url, json=payload)
        if resp.status_code not in (200, 204):
            raise ValidationError(
                f"Google Health API batchDelete error ({resp.status_code}): {resp.text}"
            )
        return resp.json() if resp.text else {"status": "ok"}

