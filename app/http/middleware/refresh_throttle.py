import time

from django.core.cache import cache
from rest_framework.request import Request
from rest_framework.throttling import BaseThrottle
from rest_framework.views import APIView


class RefreshThrottle(BaseThrottle):
    IP_MAX_REQUESTS: int = 10
    IP_WINDOW_SECONDS: int = 60

    CACHE_KEY_IP: str = "refresh_ip:{identifier}"

    def allow_request(self, request: Request, _view: APIView) -> bool:
        ip: str | None = self.get_ident(request)

        if not ip:
            return True

        return self._check_rate(
            self.CACHE_KEY_IP.format(identifier=ip),
            self.IP_MAX_REQUESTS,
            self.IP_WINDOW_SECONDS,
        )

    def wait(self) -> float | None:
        return None

    @staticmethod
    def _check_rate(key: str, max_requests: int, window: int) -> bool:
        now = time.time()
        history: list[float] = cache.get(key, [])
        history = [timestamp for timestamp in history if timestamp > now - window]

        if len(history) >= max_requests:
            return False

        history.append(now)
        cache.set(key, history, timeout=window)

        return True
