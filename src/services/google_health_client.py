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
    ):
        self.token = token or settings.google_health_token
        self.base_url = (base_url or settings.google_health_api_url).rstrip("/")
        self._http_client = http_client

    def _ensure_authenticated(self) -> str:
        if not self.token:
            raise ValidationError(
                "Missing Google Health credentials. Set GOOGLE_HEALTH_ACCESS_TOKEN environment variable."
            )
        return self.token

    def _get_headers(self) -> Dict[str, str]:
        token = self._ensure_authenticated()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _client(self) -> httpx2.Client:
        if self._http_client is not None:
            return self._http_client
        return httpx2.Client(timeout=10.0)

    def post_nutrition_datapoint(self, data_point: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a nutrition dataPoint to Google Health API."""
        url = f"{self.base_url}/users/me/dataTypes/nutrition/dataPoints"
        headers = self._get_headers()

        if self._http_client is not None:
            resp = self._http_client.post(url, json=data_point, headers=headers)
        else:
            with httpx2.Client(timeout=10.0) as client:
                resp = client.post(url, json=data_point, headers=headers)

        if resp.status_code not in (200, 201, 202):
            raise ValidationError(
                f"Google Health API error ({resp.status_code}): {resp.text}"
            )
        return resp.json() if resp.text else {"status": "ok"}

    def get_sleep_datapoints(
        self, start_time: Optional[str] = None, end_time: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch sleep dataPoints from Google Health API."""
        url = f"{self.base_url}/users/me/dataTypes/sleep/dataPoints"
        headers = self._get_headers()
        params = {}
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        if self._http_client is not None:
            resp = self._http_client.get(url, params=params, headers=headers)
        else:
            with httpx2.Client(timeout=10.0) as client:
                resp = client.get(url, params=params, headers=headers)

        if resp.status_code != 200:
            raise ValidationError(
                f"Google Health API error ({resp.status_code}): {resp.text}"
            )
        data = resp.json()
        return data.get("dataPoints", []) if isinstance(data, dict) else data

    def get_weight_datapoints(
        self, start_time: Optional[str] = None, end_time: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch weight body measurement dataPoints from Google Health API."""
        url = f"{self.base_url}/users/me/dataTypes/weight/dataPoints"
        headers = self._get_headers()
        params = {}
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time

        if self._http_client is not None:
            resp = self._http_client.get(url, params=params, headers=headers)
        else:
            with httpx2.Client(timeout=10.0) as client:
                resp = client.get(url, params=params, headers=headers)

        if resp.status_code != 200:
            raise ValidationError(
                f"Google Health API error ({resp.status_code}): {resp.text}"
            )
        data = resp.json()
        return data.get("dataPoints", []) if isinstance(data, dict) else data
