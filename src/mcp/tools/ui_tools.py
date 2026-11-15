"""MCP tools: Interactive HTML artifacts and UI form generators."""

from typing import Optional

from src.ui import render_latest_html
from src.ui.html_generator import VALID_FORM_TYPES


def get_ui_form(form_type: Optional[str] = "hub") -> dict:
    """Retrieve an interactive HTML artifact form for Hermes GUI.

    Args:
        form_type: Target form view: 'hub', 'meal', 'recipe', 'ingredient', 'workout', or 'summary'.
                   Default is 'hub'.

    Returns:
        {"status": "ok", "form_type": str, "html": str, "supported_types": list[str]}
    """
    selected = (form_type or "hub").lower().strip()
    if selected not in VALID_FORM_TYPES:
        return {
            "status": "error",
            "code": "invalid_input",
            "message": f"invalid form_type '{form_type}'. Expected one of {list(VALID_FORM_TYPES)}",
        }

    html = render_latest_html(selected)
    return {
        "status": "ok",
        "form_type": selected,
        "html": html,
        "supported_types": list(VALID_FORM_TYPES),
    }
