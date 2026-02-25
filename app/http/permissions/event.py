from __future__ import annotations

from typing import TYPE_CHECKING, cast

from app.enums import SystemRole
from app.http.permissions.base import BaseAppPermission

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.views import APIView

    from app.models.user import User


class CanPushEvents(BaseAppPermission):
    """Root or account owner with producer/root system role."""

    def has_authenticated_permission(self, request: Request, view: APIView) -> bool:
        user = cast("User", request.user)

        if self.is_root(user):
            return True

        account_id = view.kwargs.get("id")

        return self.is_account_owner(user, account_id) and user.role in (
            SystemRole.ROOT,
            SystemRole.PRODUCER,
        )


class CanConsumeEvents(BaseAppPermission):
    """Root or account owner with platform/root system role."""

    def has_authenticated_permission(self, request: Request, view: APIView) -> bool:
        user = cast("User", request.user)

        if self.is_root(user):
            return True

        account_id = view.kwargs.get("id")

        return self.is_account_owner(user, account_id) and user.role in (
            SystemRole.ROOT,
            SystemRole.PLATFORM,
        )


class CanAckEvents(BaseAppPermission):
    """Root or account owner with platform/root system role."""

    def has_authenticated_permission(self, request: Request, view: APIView) -> bool:
        user = cast("User", request.user)

        if self.is_root(user):
            return True

        account_id = view.kwargs.get("id")

        return self.is_account_owner(user, account_id) and user.role in (
            SystemRole.ROOT,
            SystemRole.PLATFORM,
        )


class CanReadHistory(BaseAppPermission):
    """Root or account owner with any system role."""

    def has_authenticated_permission(self, request: Request, view: APIView) -> bool:
        user = cast("User", request.user)

        if self.is_root(user):
            return True

        account_id = view.kwargs.get("id")

        return self.is_account_owner(user, account_id)


class CanReadResponses(BaseAppPermission):
    """Root or account owner with producer/root system role."""

    def has_authenticated_permission(self, request: Request, view: APIView) -> bool:
        user = cast("User", request.user)

        if self.is_root(user):
            return True

        account_id = view.kwargs.get("id")

        return self.is_account_owner(user, account_id) and user.role in (
            SystemRole.ROOT,
            SystemRole.PRODUCER,
        )
