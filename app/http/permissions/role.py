from __future__ import annotations

from typing import TYPE_CHECKING, cast

from app.enums import SystemRole
from app.http.permissions.base import BaseAppPermission

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.views import APIView

    from app.models.user import User


class IsRoot(BaseAppPermission):
    """Checks SystemRole: user.role == root"""

    def has_authenticated_permission(self, request: Request, _view: APIView) -> bool:
        user = cast("User", request.user)

        return user.role == SystemRole.ROOT


class IsRootOrPlatform(BaseAppPermission):
    """Checks SystemRole: user.role in (root, platform)"""

    def has_authenticated_permission(self, request: Request, _view: APIView) -> bool:
        user = cast("User", request.user)

        return user.role in (SystemRole.ROOT, SystemRole.PLATFORM)


class IsProducerOrRoot(BaseAppPermission):
    """Checks SystemRole: user.role in (root, producer)"""

    def has_authenticated_permission(self, request: Request, _view: APIView) -> bool:
        user = cast("User", request.user)

        return user.role in (SystemRole.ROOT, SystemRole.PRODUCER)
