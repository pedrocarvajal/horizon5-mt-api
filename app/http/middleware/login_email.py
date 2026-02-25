from rest_framework.throttling import SimpleRateThrottle


class LoginEmailThrottle(SimpleRateThrottle):
    scope = "login_email"

    def get_cache_key(self, request, _view):
        email = request.data.get("email", "")
        if not email:
            return None
        return self.cache_format % {"scope": self.scope, "ident": email}
