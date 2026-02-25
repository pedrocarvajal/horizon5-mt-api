from rest_framework.throttling import SimpleRateThrottle


class RoleBasedThrottle(SimpleRateThrottle):
    def get_cache_key(self, request, _view):
        if not request.user or not request.user.is_authenticated:
            return None
        role = getattr(request.user, "role", "producer")
        self.scope = f"role_{role}"
        rate = self.THROTTLE_RATES.get(self.scope)
        if rate is None:
            return None
        return self.cache_format % {"scope": self.scope, "ident": request.user.pk}

    def get_rate(self):
        if self.scope is None:
            return None
        return self.THROTTLE_RATES.get(self.scope)
