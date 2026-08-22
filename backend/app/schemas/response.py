from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper for all endpoints."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "message": "Operation successful.",
                "data": {},
            }
        }
    )

    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Human-readable message")
    data: T | None = Field(
        default=None, description="Response data payload"
    )


class ErrorResponse(BaseModel):
    """Standard error response format."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": False,
                "message": "Validation failed",
                "errors": [
                    {
                        "field": "email",
                        "detail": "Invalid email format",
                    }
                ],
            }
        }
    )

    success: bool = Field(default=False, description="Always false for errors")
    message: str = Field(..., description="Error message")
    errors: list[dict[str, Any]] = Field(
        default_factory=list, description="Detailed error information"
    )
