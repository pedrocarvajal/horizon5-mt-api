from typing import ClassVar

from django.contrib.auth import authenticate
from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from app.audit import log_account_locked, log_login_failed, log_login_success, log_token_blacklisted
from app.http.controllers.base import BaseController
from app.http.middleware.login_email import LoginEmailThrottle
from app.http.middleware.login_rate import LoginRateThrottle
from app.http.requests.auth.login import LoginRequestSerializer
from app.http.requests.auth.refresh import RefreshRequestSerializer
from app.http.resources.user import UserResource

LOCKOUT_THRESHOLD = 10
LOCKOUT_DURATION = 900


class AuthController(BaseController):
    permission_map: ClassVar[dict] = {
        "login": [AllowAny],
        "refresh": [AllowAny],
        "logout": [IsAuthenticated],
        "me": [IsAuthenticated],
    }
    throttle_map: ClassVar[dict] = {
        "login": [LoginRateThrottle, LoginEmailThrottle],
    }
    default_throttles: ClassVar[list] = []

    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        ip = self._get_client_ip(request)

        lock_key = f"login_lock:{email}"
        if cache.get(lock_key):
            log_login_failed(email=email, ip=ip, reason="account_locked")
            return Response(
                {"detail": "Account temporarily locked. Try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        user = authenticate(request, email=email, password=password)
        if user is None:
            self._record_failed_attempt(email, ip)
            log_login_failed(email=email, ip=ip, reason="invalid_credentials")
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            log_login_failed(email=email, ip=ip, reason="inactive_account")
            return Response(
                {"detail": "Account is inactive."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        self._clear_failed_attempts(email)
        log_login_success(user_id=user.pk, ip=ip)

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"], url_path="refresh")
    def refresh(self, request):
        serializer = RefreshRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh = RefreshToken(serializer.validated_data["refresh"])
            return Response(
                {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"detail": "Invalid or expired refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    @action(detail=False, methods=["post"], url_path="logout")
    def logout(self, request):
        serializer = RefreshRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh = RefreshToken(serializer.validated_data["refresh"])
            refresh.blacklist()
            log_token_blacklisted(user_id=request.user.id)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(
                {"detail": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request):
        serializer = UserResource(request.user)
        return Response(serializer.data)

    def _record_failed_attempt(self, email, ip):
        attempts_key = f"login_attempts:{email}"
        attempts = cache.get(attempts_key, 0) + 1
        cache.set(attempts_key, attempts, timeout=LOCKOUT_DURATION)
        if attempts >= LOCKOUT_THRESHOLD:
            cache.set(f"login_lock:{email}", True, timeout=LOCKOUT_DURATION)
            log_account_locked(email=email, ip=ip, failed_attempts=attempts)

    def _clear_failed_attempts(self, email):
        cache.delete(f"login_attempts:{email}")
        cache.delete(f"login_lock:{email}")

    def _get_client_ip(self, request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
