from rest_framework.permissions import BasePermission

from app.models import Account


class IsAccountOwner(BasePermission):
    """Checks that the authenticated user owns the target account."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        account_id = view.kwargs.get("id")
        if not account_id:
            return False
        return Account.objects.filter(id=account_id, user=request.user).exists()
