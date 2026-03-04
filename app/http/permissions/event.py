from __future__ import annotations

from typing import TYPE_CHECKING, cast

from app.enums import SystemRole
from app.http.permissions.base import BaseAppPermission

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.views import APIView

    from app.models.user import User


class CanPushEvents(BaseAppPermission):
    """Root or producer role."""

    def has_authenticated_permission(self, request: Request, _view: APIView) -> bool:
        user = cast("User", request.user)
        return user.role in (SystemRole.ROOT, SystemRole.PRODUCER)


class CanConsumeEvents(BaseAppPermission):
    """Root or platform role."""

    def has_authenticated_permission(self, request: Request, _view: APIView) -> bool:
        user = cast("User", request.user)
        return user.role in (SystemRole.ROOT, SystemRole.PLATFORM)


class CanAckEvents(BaseAppPermission):
    """Root or platform role."""

    def has_authenticated_permission(self, request: Request, _view: APIView) -> bool:
        user = cast("User", request.user)
        return user.role in (SystemRole.ROOT, SystemRole.PLATFORM)


class CanReadHistory(BaseAppPermission):
    """Any authenticated user."""

    def has_authenticated_permission(self, _request: Request, _view: APIView) -> bool:
        return True


class CanReadResponses(BaseAppPermission):
    """Root or producer role."""

    def has_authenticated_permission(self, request: Request, _view: APIView) -> bool:
        user = cast("User", request.user)
        return user.role in (SystemRole.ROOT, SystemRole.PRODUCER)
