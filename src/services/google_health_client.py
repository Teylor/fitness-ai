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
        self.token = token if token is not None else settings.google_health_token
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
        """Upload a nutrition dataPoint to Google Health API.

        The Google Health API v4 `food` data type is read-only (it mirrors data
        synced from other apps); creating custom nutrition data points is not
        supported. This call therefore always fails with a `sync_unsupported`
        ValidationError by design.
        """
        raise ValidationError(
            "Google Health API v4 does not support writing nutrition data "
            "points (the 'food' data type is read-only). Meals cannot be "
            "pushed to Google Health from this system.",
            code="sync_unsupported",
        )

    def _get_datapoints(self, data_type: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/users/me/dataTypes/{data_type}/dataPoints"
        headers = self._get_headers()

        if self._http_client is not None:
            resp = self._http_client.get(url, headers=headers)
        else:
            with httpx2.Client(timeout=10.0) as client:
                resp = client.get(url, headers=headers)

        if resp.status_code != 200:
            raise ValidationError(
                f"Google Health API error ({resp.status_code}): {resp.text}"
            )
        data = resp.json()
        return data.get("dataPoints", []) if isinstance(data, dict) else data

    def get_sleep_datapoints(self) -> List[Dict[str, Any]]:
        """Fetch sleep dataPoints from Google Health API."""
        return self._get_datapoints("sleep")

    def get_weight_datapoints(self) -> List[Dict[str, Any]]:
        """Fetch weight body measurement dataPoints from Google Health API."""
        return self._get_datapoints("weight")

