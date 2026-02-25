from __future__ import annotations

from typing import TYPE_CHECKING, cast

from app.http.permissions.base import BaseAppPermission

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.views import APIView

    from app.models.user import User


class IsAccountOwner(BaseAppPermission):
    """Checks that the authenticated user owns the target account."""

    def has_authenticated_permission(self, request: Request, view: APIView) -> bool:
        account_id = view.kwargs.get("id")

        if not account_id:
            return False

        user = cast("User", request.user)

        return self.is_account_owner(user, account_id)
