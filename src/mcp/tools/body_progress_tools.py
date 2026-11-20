"""MCP tools: Body progress tracking operations."""

from dataclasses import asdict
from typing import Optional

from src.services.body_progress_service import BodyProgressService
from src.utils.errors import ToolError


def log_body_progress(
    date: Optional[str] = None,
    weight_kg: Optional[float] = None,
    waist_cm: Optional[float] = None,
    chest_cm: Optional[float] = None,
    arm_cm: Optional[float] = None,
    leg_cm: Optional[float] = None,
    notes: Optional[str] = None,
) -> dict:
    """Log or update daily body progress measurements (weight, waist, chest, arm, leg)."""
    service = BodyProgressService()
    try:
        record = service.log_progress(
            date=date,
            weight_kg=weight_kg,
            waist_cm=waist_cm,
            chest_cm=chest_cm,
            arm_cm=arm_cm,
            leg_cm=leg_cm,
            notes=notes,
        )
        return {"status": "ok", "progress": asdict(record)}
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


def list_body_progress(month: Optional[str] = None) -> dict:
    """List body progress records chronologically, optionally filtered by YYYY-MM month."""
    service = BodyProgressService()
    try:
        records = service.list_progress(month=month or None)
        entries = [asdict(r) for r in records]
        return {"status": "ok", "entries": entries, "count": len(entries)}
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


def delete_body_progress(progress_id: int) -> dict:
    """Delete a body progress record by its ID."""
    service = BodyProgressService()
    try:
        service.delete_progress(int(progress_id))
        return {"status": "ok", "deleted_id": int(progress_id)}
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}
