from typing import Any

from fastapi import status


class APIException(Exception):
    """Base exception for all API errors."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        errors: list[dict[str, Any]] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.errors = errors or []
        super().__init__(self.message)


class ValidationError(APIException):
    """Raised when request validation fails."""

    def __init__(self, message: str, errors: list[dict[str, Any]] | None = None) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=errors,
        )


class NotFoundError(APIException):
    """Raised when a resource is not found."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class UnauthorizedError(APIException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenError(APIException):
    """Raised when authorization fails."""

    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ConflictError(APIException):
    """Raised when a resource conflict occurs."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
        )


class FileTooLargeError(APIException):
    """Raised when uploaded file exceeds size limit."""

    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_413_PAYLOAD_TOO_LARGE,
        )


class RateLimitError(APIException):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Too many requests") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


class InternalServerError(APIException):
    """Raised for unexpected server errors."""

    def __init__(self, message: str = "Internal server error") -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )