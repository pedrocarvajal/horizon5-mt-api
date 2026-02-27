from typing import ClassVar, cast

from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from app.http.controllers.base import BaseController
from app.http.middleware.login_throttle import LoginThrottle
from app.http.middleware.refresh_throttle import RefreshThrottle
from app.http.requests.auth.login import LoginRequestSerializer
from app.http.requests.auth.logout import LogoutRequestSerializer
from app.http.requests.auth.refresh import RefreshRequestSerializer
from app.models import ApiKey
from app.models.user import User


class AuthController(BaseController):
    permissions: ClassVar[dict] = {
        "login": [AllowAny],
        "refresh": [AllowAny],
        "logout": [IsAuthenticated],
        "me": [IsAuthenticated],
    }

    throttles: ClassVar[dict] = {
        "login": [LoginThrottle],
        "refresh": [RefreshThrottle],
    }

    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request) -> Response:
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if "api_key" in serializer.validated_data:
            return self._login_with_api_key(request, serializer.validated_data["api_key"])

        return self._login_with_credentials(request, serializer.validated_data)

    def _login_with_credentials(self, request, validated_data: dict) -> Response:
        email = validated_data["email"]
        password = validated_data["password"]
        ip = self._get_client_ip(request)

        user = authenticate(
            request,
            email=email,
            password=password,
        )

        if user is None:
            LoginThrottle.record_failure(email, ip)

            return self.reply(
                message="Invalid credentials.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return self.reply(
                message="Account is inactive.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        LoginThrottle.clear_login_attempts(email)

        return self.reply(data=self._build_token_data(user))

    def _login_with_api_key(self, request, raw_key: str) -> Response:
        ip = self._get_client_ip(request)
        key_hash = ApiKey.hash_key(raw_key)

        api_key = ApiKey.objects.select_related("user").filter(key_hash=key_hash).first()

        if api_key is None:
            return self.reply(
                message="Invalid API key.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not api_key.is_usable:
            return self.reply(
                message="API key is inactive or expired.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not api_key.is_ip_allowed(ip):
            return self.reply(
                message="IP address not allowed for this API key.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        user = api_key.user

        if not user.is_active:
            return self.reply(
                message="Account is inactive.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        ApiKey.objects.filter(pk=api_key.pk).update(last_used_at=timezone.now())

        return self.reply(data=self._build_token_data(user))

    @action(detail=False, methods=["post"], url_path="refresh")
    def refresh(self, request) -> Response:
        serializer = RefreshRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            with transaction.atomic():
                old_refresh = RefreshToken(serializer.validated_data["refresh"])
                old_refresh.blacklist()

                user = User.objects.get(id=old_refresh["user_id"])
                new_refresh = RefreshToken.for_user(user)
                new_access = new_refresh.access_token

            return self.reply(
                data={
                    "access": str(new_access),
                    "refresh": str(new_refresh),
                    "expires_at": int(new_access["exp"]),
                },
            )
        except TokenError:
            return self.reply(
                message="Token is invalid or expired",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

    @action(detail=False, methods=["post"], url_path="logout")
    def logout(self, request) -> Response:
        serializer = LogoutRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            token.blacklist()
        except TokenError:
            pass

        return self.reply(message="Logged out successfully")

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request) -> Response:
        user = cast(User, request.user)

        return self.reply(
            data={
                "id": str(user.pk),
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at.isoformat(),
            },
        )

    @staticmethod
    def _build_token_data(user) -> dict:
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return {
            "access": str(access),
            "refresh": str(refresh),
            "expires_at": int(access["exp"]),
        }

    def _get_client_ip(self, request) -> str:
        num_proxies = getattr(settings, "NUM_PROXIES", 0)

        if num_proxies > 0:
            forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
            addresses = [address.strip() for address in forwarded.split(",") if address.strip()]
            if len(addresses) >= num_proxies:
                return addresses[-num_proxies]

        return request.META.get("REMOTE_ADDR", "")
