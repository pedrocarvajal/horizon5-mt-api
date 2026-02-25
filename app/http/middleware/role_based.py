from __future__ import annotations

from typing import TYPE_CHECKING

from rest_framework.throttling import SimpleRateThrottle

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.views import APIView


class RoleBasedThrottle(SimpleRateThrottle):
    DEFAULT_ROLE: str = "producer"

    def get_cache_key(self, request: Request, _view: APIView) -> str | None:
        if not request.user or not request.user.is_authenticated:
            return None

        role = getattr(request.user, "role", self.DEFAULT_ROLE)
        self.scope = f"role_{role}"
        rate = self.THROTTLE_RATES.get(self.scope)

        if rate is None:
            return None

        return self.cache_format % {"scope": self.scope, "ident": request.user.pk}

    def get_rate(self) -> str | None:
        if self.scope is None:
            return None

        return self.THROTTLE_RATES.get(self.scope)
