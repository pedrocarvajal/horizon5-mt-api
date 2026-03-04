from __future__ import annotations

from typing import TYPE_CHECKING, cast

from app.enums import SystemRole
from app.http.permissions.base import BaseAppPermission

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.views import APIView

    from app.models.user import User


class CanPushEvents(BaseAppPermission):
    """Root (unrestricted) or producer who owns the target account."""

    def has_authenticated_permission(self, request: Request, view: APIView) -> bool:
        user = cast("User", request.user)

        if user.role == SystemRole.ROOT:
            return True

        if user.role != SystemRole.PRODUCER:
            return False

        account_id = view.kwargs.get("id")
        return self.is_account_owner(user, account_id)


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
    """Root or platform (unrestricted), or account owner."""

    def has_authenticated_permission(self, request: Request, view: APIView) -> bool:
        user = cast("User", request.user)

        if user.role in (SystemRole.ROOT, SystemRole.PLATFORM):
            return True

        account_id = view.kwargs.get("id")
        return self.is_account_owner(user, account_id)


class CanReadResponses(BaseAppPermission):
    """Root (unrestricted) or producer who owns the target account."""

    def has_authenticated_permission(self, request: Request, view: APIView) -> bool:
        user = cast("User", request.user)

        if user.role == SystemRole.ROOT:
            return True

        if user.role != SystemRole.PRODUCER:
            return False

        account_id = view.kwargs.get("id")
        return self.is_account_owner(user, account_id)
