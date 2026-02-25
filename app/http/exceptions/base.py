from typing import Any

from rest_framework.exceptions import APIException, Throttled, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from app.enums import ExceptionMapping
from app.http.exceptions.helpers import extract_message
from app.http.response import build_response


def exception_handler(exception: Exception, context: dict[str, Any]) -> Response | None:
    _ = drf_exception_handler(exception, context)

    if not isinstance(exception, APIException):
        return None

    if isinstance(exception, ValidationError):
        return build_response(
            message=ExceptionMapping.VALIDATION_FAILED.message,
            data={"errors": exception.detail},
            status_code=ExceptionMapping.VALIDATION_FAILED.status_code,
        )

    if isinstance(exception, Throttled):
        wait = getattr(exception, "wait", None)
        message = ExceptionMapping.THROTTLED.message

        if wait is not None:
            message = f"{message} Try again in {int(wait)} seconds."

        return build_response(
            message=message,
            status_code=ExceptionMapping.THROTTLED.status_code,
        )

    mapping = ExceptionMapping.from_exception(type(exception))

    return build_response(
        message=extract_message(
            exception.detail,
            mapping.message if mapping else ExceptionMapping.GENERIC_ERROR.message,
        ),
        status_code=mapping.status_code if mapping else exception.status_code,
    )
