from typing import Any

from rest_framework import status as http_status
from rest_framework.response import Response

from app.enums import HttpStatusFamily


def build_response(
    message: str | None = None,
    data: Any = None,
    status_code: int = http_status.HTTP_200_OK,
    meta: dict[str, Any] | None = None,
) -> Response:
    success = HttpStatusFamily.SUCCESS <= status_code < HttpStatusFamily.REDIRECTION
    response: dict[str, Any] = {"success": success}

    if message is not None:
        response["message"] = message

    if data is not None:
        response["data"] = data

    if meta is not None:
        response["meta"] = meta

    return Response(response, status=status_code)
