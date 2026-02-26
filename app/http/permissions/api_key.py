from __future__ import annotations

from typing import TYPE_CHECKING, cast

from app.http.permissions.base import BaseAppPermission
from app.models import ApiKey

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.views import APIView

    from app.models.user import User


class IsApiKeyOwner(BaseAppPermission):
    def has_authenticated_permission(self, request: Request, view: APIView) -> bool:
        user = cast("User", request.user)

        if self.is_root(user):
            return True

        api_key_id = view.kwargs.get("id")

        if api_key_id is None:
            return True

        return ApiKey.objects.filter(id=api_key_id, user=user).exists()
