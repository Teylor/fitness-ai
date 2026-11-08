"""MCP tools: Daily goal operations."""

from dataclasses import asdict
from datetime import datetime
from typing import Optional

from src.models.daily_goal import DailyGoal
from src.services.goal_service import GoalService
from src.utils.errors import ToolError


def set_daily_goal(
    kcal: float,
    protein: float,
    carbs: float,
    fat: float,
    date: Optional[str] = None,
    default: bool = False,
) -> dict:
    """Set or update daily goal for a specific date or as global default."""
    service = GoalService()
    if not date:
        date = datetime.now().strftime("%d-%m-%Y")
    try:
        goal = DailyGoal(
            date=date,
            kcal=kcal,
            protein=protein,
            carbs=carbs,
            fat=fat,
            is_default=default,
        )
        if default:
            saved = service.set_default(goal)
        else:
            saved = service.set_goal(goal)
        return {"status": "ok", "goal": asdict(saved)}
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


def get_daily_goal(date: Optional[str] = None) -> dict:
    """Retrieve daily goal for a date with fallback chain (explicit -> closest previous -> default)."""
    service = GoalService()
    if not date:
        date = datetime.now().strftime("%d-%m-%Y")
    try:
        goal = service.get_goal(date)
        return {"status": "ok", "goal": asdict(goal)}
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}
