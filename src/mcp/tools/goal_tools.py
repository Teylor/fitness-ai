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
    day_off_default: bool = False,
    is_day_off: bool = False,
) -> dict:
    """Set or update daily goal for a specific date, training default, or Day Off default."""
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
            is_day_off=is_day_off,
            is_day_off_default=day_off_default,
        )
        if day_off_default:
            saved = service.set_day_off_default(goal)
        elif default:
            saved = service.set_default(goal)
        else:
            saved = service.set_goal(goal)
        return {"status": "ok", "goal": asdict(saved), "profiles": service.get_goal_profiles()}
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
        return {"status": "ok", "goal": asdict(goal), "profiles": service.get_goal_profiles()}
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}


def toggle_day_off(
    date: Optional[str] = None,
    is_day_off: Optional[bool] = None,
) -> dict:
    """Toggle or set Day Off nutritional goals for a specific date (DD-MM-YYYY)."""
    service = GoalService()
    if not date:
        date = datetime.now().strftime("%d-%m-%Y")
    try:
        goal = service.toggle_day_off(date=date, is_day_off=is_day_off)
        return {
            "status": "ok",
            "date": date,
            "is_day_off": goal.is_day_off,
            "goal": asdict(goal),
        }
    except ToolError as err:
        return err.to_dict()
    except Exception as exc:
        return {"status": "error", "code": "internal", "message": str(exc)}
