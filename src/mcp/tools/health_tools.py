"""MCP tools: Google Health API synchronization."""

from datetime import datetime
from typing import Optional

from peewee import SQL

from src.db.models import SleepLog, StepLog, WeightLog
from src.services.google_health_service import GoogleHealthService
from src.utils.errors import ToolError


def sync_meals_to_google_health(date: Optional[str] = None) -> dict:
    """Synchronize locally registered meals for a specific date to Google Health.

    Note: Google Health API v4 only exposes a read-only `food` data type,
    so pushing custom nutrition data points is not supported. This tool
    currently fails with code `sync_unsupported`.

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


def log_steps(
    steps: int,
    date: Optional[str] = None,
    distance_km: Optional[float] = None,
) -> dict:
    """Log or update daily step count for a specific date (DD-MM-YYYY)."""
    if not date:
        date = datetime.now().strftime("%d-%m-%Y")
    else:
        try:
            datetime.strptime(date, "%d-%m-%Y")
        except ValueError:
            return {
                "status": "error",
                "code": "invalid_date",
                "message": f"invalid date '{date}' (expected DD-MM-YYYY)",
            }
    try:
        steps_val = int(steps)
        if steps_val < 0:
            return {
                "status": "error",
                "code": "invalid_input",
                "message": "steps cannot be negative",
            }

        row, created = StepLog.get_or_create(
            date=date,
            defaults={
                "steps": steps_val,
                "distance_km": distance_km,
                "source": "manual",
            },
        )
        if not created:
            row.steps = steps_val
            if distance_km is not None:
                row.distance_km = distance_km
            row.updated_at = SQL("datetime('now')")
            row.save()

        return {
            "status": "ok",
            "date": date,
            "steps": row.steps,
            "distance_km": row.distance_km,
        }
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


def get_health_metrics(date: Optional[str] = None) -> dict:
    """Retrieve daily health and activity metrics (sleep, weight, steps) for a specific date."""
    if not date:
        date = datetime.now().strftime("%d-%m-%Y")
    else:
        try:
            datetime.strptime(date, "%d-%m-%Y")
        except ValueError:
            return {
                "status": "error",
                "code": "invalid_date",
                "message": f"invalid date '{date}' (expected DD-MM-YYYY)",
            }

    try:
        # Steps
        step_row = StepLog.get_or_none(StepLog.date == date)
        steps_data = None
        if step_row:
            steps_data = {
                "steps": step_row.steps,
                "distance_km": step_row.distance_km,
                "source": step_row.source,
            }

        # Sleep
        sleep_rows = list(SleepLog.select().where(SleepLog.date == date))
        sleep_data = None
        if sleep_rows:
            total_duration = sum(r.duration_minutes for r in sleep_rows)
            deep_total = sum(r.deep_sleep_minutes for r in sleep_rows)
            rem_total = sum(r.rem_sleep_minutes for r in sleep_rows)
            light_total = sum(r.light_sleep_minutes for r in sleep_rows)
            sleep_data = {
                "duration_minutes": round(total_duration, 1),
                "duration_hours": round(total_duration / 60.0, 1),
                "deep_sleep_minutes": round(deep_total, 1),
                "rem_sleep_minutes": round(rem_total, 1),
                "light_sleep_minutes": round(light_total, 1),
                "sessions_count": len(sleep_rows),
            }

        # Weight
        weight_rows = list(
            WeightLog.select().where(WeightLog.date == date).order_by(WeightLog.id.desc())
        )
        weight_data = None
        if weight_rows:
            latest = weight_rows[0]
            weight_data = {
                "weight_kg": latest.weight_kg,
                "bmi": latest.bmi,
                "body_fat_pct": latest.body_fat_pct,
                "source": latest.source,
            }

        return {
            "status": "ok",
            "date": date,
            "steps": steps_data,
            "sleep": sleep_data,
            "weight": weight_data,
        }
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


