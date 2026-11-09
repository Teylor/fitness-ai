"""MCP tools: Google Health API synchronization."""

from typing import Optional

from src.services.google_health_service import GoogleHealthService
from src.utils.errors import ToolError


def sync_meals_to_google_health(date: Optional[str] = None) -> dict:
    """Synchronize locally registered meals for a specific date to Google Health.

    Args:
        date: Date in DD-MM-YYYY format (default: today).

    Returns:
        {"status": "ok", "date": str, "synced_count": int, "total_kcal": float, "meals": list}
    """
    service = GoogleHealthService()
    try:
        return service.sync_meals(date)
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


def fetch_google_health_sleep(date: Optional[str] = None, days: int = 1) -> dict:
    """Fetch sleep session records from Google Health and persist them locally.

    Args:
        date: Reference date in DD-MM-YYYY format (default: today).
        days: Number of days of historical sleep to query (default: 1).

    Returns:
        {"status": "ok", "date": str, "count": int, "records": list}
    """
    service = GoogleHealthService()
    try:
        return service.fetch_sleep(date=date, days=days)
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


def fetch_google_health_weight(date: Optional[str] = None, days: int = 7) -> dict:
    """Fetch body weight measurements from Google Health and persist them locally.

    Args:
        date: Reference date in DD-MM-YYYY format (default: today).
        days: Number of days of historical weight logs to query (default: 7).

    Returns:
        {"status": "ok", "date": str, "count": int, "latest_weight_kg": float, "records": list}
    """
    service = GoogleHealthService()
    try:
        return service.fetch_weight(date=date, days=days)
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


def sync_google_health(date: Optional[str] = None) -> dict:
    """Full synchronization: push meals to Google Health and pull sleep and weight metrics.

    Args:
        date: Target date in DD-MM-YYYY format (default: today).

    Returns:
        {"status": "ok", "date": str, "meals_synced": int, "sleep_sessions_fetched": int, "weight_records_fetched": int}
    """
    service = GoogleHealthService()
    try:
        return service.sync_all(date)
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}
