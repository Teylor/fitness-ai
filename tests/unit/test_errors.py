"""Unit tests for the typed error hierarchy."""

import pytest

from src.utils.errors import (
    ConflictError,
    DuplicateError,
    NotFoundError,
    ToolError,
    ValidationError,
)


def test_tool_error_base_properties():
    err = ToolError("generic failure", code="internal")
    assert isinstance(err, ValueError)
    assert err.code == "internal"
    assert err.message == "generic failure"
    assert str(err) == "generic failure"
    assert err.to_dict() == {
        "status": "error",
        "code": "internal",
        "message": "generic failure",
    }


def test_not_found_error():
    err = NotFoundError("Ingredient not found")
    assert isinstance(err, ToolError)
    assert isinstance(err, ValueError)
    assert err.code == "not_found"
    assert err.message == "Ingredient not found"
    assert err.to_dict() == {
        "status": "error",
        "code": "not_found",
        "message": "Ingredient not found",
    }


def test_duplicate_error():
    err = DuplicateError("Duplicate entity exists")
    assert isinstance(err, ToolError)
    assert isinstance(err, ValueError)
    assert err.code == "duplicate"
    assert err.message == "Duplicate entity exists"
    assert err.to_dict() == {
        "status": "error",
        "code": "duplicate",
        "message": "Duplicate entity exists",
    }


def test_validation_error():
    err = ValidationError("Invalid date format")
    assert isinstance(err, ToolError)
    assert isinstance(err, ValueError)
    assert err.code == "invalid_input"
    assert err.message == "Invalid date format"
    assert err.to_dict() == {
        "status": "error",
        "code": "invalid_input",
        "message": "Invalid date format",
    }


def test_conflict_error():
    err = ConflictError("Cannot delete ingredient used in recipe")
    assert isinstance(err, ToolError)
    assert isinstance(err, ValueError)
    assert err.code == "conflict"
    assert err.message == "Cannot delete ingredient used in recipe"
    assert err.to_dict() == {
        "status": "error",
        "code": "conflict",
        "message": "Cannot delete ingredient used in recipe",
    }

