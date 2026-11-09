"""Typed error hierarchy for domain services and MCP tools.

Subclasses inherit from ValueError so existing service callers and tests expecting
ValueError remain compatible while exposing machine-readable codes.
"""

from typing import Any, Dict


class ToolError(ValueError):
    """Base error for all tool and domain service failures."""

    def __init__(self, message: str, code: str = "internal") -> None:
        super().__init__(message)
        self.message = message
        self.code = code

    def to_dict(self) -> Dict[str, Any]:
        """Return api-spec compatible error dictionary."""
        return {
            "status": "error",
            "code": self.code,
            "message": self.message,
        }


class NotFoundError(ToolError):
    """Raised when an entity is not found."""

    def __init__(self, message: str, code: str = "not_found") -> None:
        super().__init__(message, code=code)


class DuplicateError(ToolError):
    """Raised when an entity already exists (e.g. name conflict)."""

    def __init__(self, message: str, code: str = "duplicate") -> None:
        super().__init__(message, code=code)


class ValidationError(ToolError):
    """Raised when user input fails domain validation."""

    def __init__(self, message: str, code: str = "invalid_input") -> None:
        super().__init__(message, code=code)


class ConflictError(ToolError):
    """Raised when an operation conflicts with existing relationships or state."""

    def __init__(self, message: str, code: str = "conflict") -> None:
        super().__init__(message, code=code)

