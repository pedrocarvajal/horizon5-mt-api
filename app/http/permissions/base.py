from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework.permissions import BasePermission

from app.enums import SystemRole
from app.models import Account

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.views import APIView

    from app.models.user import User


class BaseAppPermission(BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        return self.has_authenticated_permission(request, view)

    def has_authenticated_permission(self, _request: Request, _view: APIView) -> bool:
        return True

    @staticmethod
    def is_root(user: User) -> bool:
        return user.role == SystemRole.ROOT

    @staticmethod
    def is_account_owner(user: User, account_id) -> bool:
        return Account.objects.filter(id=account_id, user=user).exists()
