from typing import Any, ClassVar

from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from app.http.response import build_response


class BaseController(ViewSet):
    permissions: ClassVar[dict[str, list[type]]] = {}
    throttles: ClassVar[dict[str, list[type]]] = {}
    default_permissions: ClassVar[list[type]] = [IsAuthenticated]

    def get_permissions(self) -> list:
        permission_classes = self.permissions.get(self.action, self.default_permissions)
        return [permission() for permission in permission_classes]

    def get_throttles(self) -> list:
        if self.action in self.throttles:
            return [throttle() for throttle in self.throttles[self.action]]

        return super().get_throttles()

    def response(
        self,
        message: str | None = None,
        data: Any = None,
        status_code: int = http_status.HTTP_200_OK,
        meta: dict[str, Any] | None = None,
    ) -> Response:
        return build_response(
            message=message,
            data=data,
            status_code=status_code,
            meta=meta,
        )
