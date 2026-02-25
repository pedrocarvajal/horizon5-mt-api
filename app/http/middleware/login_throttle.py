import time

import structlog
from django.core.cache import cache
from rest_framework.request import Request
from rest_framework.throttling import BaseThrottle
from rest_framework.views import APIView

logger = structlog.get_logger("audit")


class LoginThrottle(BaseThrottle):
    IP_MAX_REQUESTS: int = 5
    IP_WINDOW_SECONDS: int = 60
    EMAIL_MAX_REQUESTS: int = 10
    EMAIL_WINDOW_SECONDS: int = 3600
    LOCKOUT_THRESHOLD: int = 10
    LOCKOUT_DURATION_SECONDS: int = 900

    CACHE_KEY_IP: str = "login_ip:{identifier}"
    CACHE_KEY_EMAIL: str = "login_email:{identifier}"
    CACHE_KEY_ATTEMPTS: str = "login_attempts:{identifier}"
    CACHE_KEY_LOCK: str = "login_lock:{identifier}"

    def allow_request(self, request: Request, _view: APIView) -> bool:
        email: str = request.data.get("email", "")
        ip: str | None = self.get_ident(request)

        if email and self._is_locked(email):
            return False

        if ip and not self._check_rate(
            self.CACHE_KEY_IP.format(identifier=ip),
            self.IP_MAX_REQUESTS,
            self.IP_WINDOW_SECONDS,
        ):
            return False

        return not email or self._check_rate(
            self.CACHE_KEY_EMAIL.format(identifier=email),
            self.EMAIL_MAX_REQUESTS,
            self.EMAIL_WINDOW_SECONDS,
        )

    def wait(self) -> float | None:
        return None

    @classmethod
    def record_failure(cls, email: str, ip: str) -> None:
        attempts_key = cls.CACHE_KEY_ATTEMPTS.format(identifier=email)
        attempts = cache.get(attempts_key, 0) + 1
        cache.set(attempts_key, attempts, timeout=cls.LOCKOUT_DURATION_SECONDS)

        if attempts >= cls.LOCKOUT_THRESHOLD:
            lock_key = cls.CACHE_KEY_LOCK.format(identifier=email)
            cache.set(lock_key, True, timeout=cls.LOCKOUT_DURATION_SECONDS)
            logger.warning("account_locked", email=email, ip=ip, failed_attempts=attempts)

    @classmethod
    def clear_login_attempts(cls, email: str) -> None:
        cache.delete(cls.CACHE_KEY_ATTEMPTS.format(identifier=email))
        cache.delete(cls.CACHE_KEY_LOCK.format(identifier=email))

    @classmethod
    def _is_locked(cls, email: str) -> bool:
        return bool(cache.get(cls.CACHE_KEY_LOCK.format(identifier=email)))

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
