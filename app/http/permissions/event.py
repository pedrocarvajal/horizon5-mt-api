from __future__ import annotations

from typing import TYPE_CHECKING, cast

from rest_framework.permissions import BasePermission

from app.enums import SystemRole
from app.models import Account

if TYPE_CHECKING:
    from app.models.user import User


def _is_root(user: User) -> bool:
    return user.role == SystemRole.ROOT


def _is_account_owner(user, account_id):
    return Account.objects.filter(id=account_id, user=user).exists()


class CanPushEvents(BasePermission):
    """Root or account owner with producer/root system role."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user = cast("User", request.user)
        if _is_root(user):
            return True
        account_id = view.kwargs.get("id")
        return _is_account_owner(user, account_id) and user.role in (
            SystemRole.ROOT,
            SystemRole.PRODUCER,
        )


class CanConsumeEvents(BasePermission):
    """Root or account owner with platform/root system role."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user = cast("User", request.user)
        if _is_root(user):
            return True
        account_id = view.kwargs.get("id")
        return _is_account_owner(user, account_id) and user.role in (
            SystemRole.ROOT,
            SystemRole.PLATFORM,
        )


class CanAckEvents(BasePermission):
    """Root or account owner with platform/root system role."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user = cast("User", request.user)
        if _is_root(user):
            return True
        account_id = view.kwargs.get("id")
        return _is_account_owner(user, account_id) and user.role in (
            SystemRole.ROOT,
            SystemRole.PLATFORM,
        )


class CanReadHistory(BasePermission):
    """Root or account owner with any system role."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user = cast("User", request.user)
        if _is_root(user):
            return True
        account_id = view.kwargs.get("id")
        return _is_account_owner(user, account_id)


class CanReadResponses(BasePermission):
    """Root or account owner with producer/root system role."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        user = cast("User", request.user)
        if _is_root(user):
            return True
        account_id = view.kwargs.get("id")
        return _is_account_owner(user, account_id) and user.role in (
            SystemRole.ROOT,
            SystemRole.PRODUCER,
        )
