from rest_framework.permissions import BasePermission

from app.enums import SystemRole


class IsRoot(BasePermission):
    """Checks SystemRole: user.role == root"""

    def has_permission(self, request, _view):
        return request.user and request.user.is_authenticated and request.user.role == SystemRole.ROOT
