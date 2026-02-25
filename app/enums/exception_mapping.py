from enum import Enum

from rest_framework import status as http_status
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    Throttled,
    ValidationError,
)


class ExceptionMapping(Enum):
    VALIDATION_FAILED = (ValidationError, http_status.HTTP_400_BAD_REQUEST, "Validation failed.")
    NOT_AUTHENTICATED = (
        NotAuthenticated,
        http_status.HTTP_401_UNAUTHORIZED,
        "Authentication credentials were not provided.",
    )
    AUTHENTICATION_FAILED = (AuthenticationFailed, http_status.HTTP_401_UNAUTHORIZED, "Authentication failed.")
    PERMISSION_DENIED = (PermissionDenied, http_status.HTTP_403_FORBIDDEN, "Permission denied.")
    THROTTLED = (Throttled, http_status.HTTP_429_TOO_MANY_REQUESTS, "Request was throttled.")
    GENERIC_ERROR = (None, 0, "An error occurred.")

    def __init__(self, exception_class: type | None, status_code: int, message: str) -> None:
        self.exception_class = exception_class
        self.status_code = status_code
        self.message = message

    @classmethod
    def from_exception(cls, exception_class: type) -> "ExceptionMapping | None":
        for member in cls:
            if member.exception_class is exception_class:
                return member

        return None
