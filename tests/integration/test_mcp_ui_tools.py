"""Integration tests: MCP UI Artifact tools."""

from src.mcp.tools.ui_tools import get_ui_form


def test_get_ui_form_default_hub():
    res = get_ui_form()
    assert res["status"] == "ok"
    assert res["form_type"] == "hub"
    assert "<!DOCTYPE html>" in res["html"]
    assert "Hermes Hub" in res["html"]
    assert "meal" in res["supported_types"]
    assert "workout" in res["supported_types"]
    assert "exercise" in res["supported_types"]


def test_get_ui_form_specific_views():
    for ftype in ("meal", "recipe", "ingredient", "workout", "exercise", "summary"):
        res = get_ui_form(ftype)
        assert res["status"] == "ok"
        assert res["form_type"] == ftype
        assert "<!DOCTYPE html>" in res["html"]


def test_get_ui_form_invalid_type():
    res = get_ui_form("unknown_type")
    assert res["status"] == "error"
    assert res["code"] == "invalid_input"
    assert "invalid form_type" in res["message"]
