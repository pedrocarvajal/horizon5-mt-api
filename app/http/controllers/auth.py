from typing import ClassVar

from django.conf import settings
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from app.http.controllers.base import BaseController
from app.http.middleware.login_throttle import LoginThrottle
from app.http.requests.auth.login import LoginRequestSerializer
from app.models import ApiKey


class AuthController(BaseController):
    permissions: ClassVar[dict] = {
        "login": [AllowAny],
    }

    throttles: ClassVar[dict] = {
        "login": [LoginThrottle],
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

            return self.response(
                message="Invalid credentials.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return self.response(
                message="Account is inactive.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        LoginThrottle.clear_login_attempts(email)
        token = AccessToken.for_user(user)

        return self.response(
            data={
                "access": str(token),
            },
        )

    def _login_with_api_key(self, request, raw_key: str) -> Response:
        ip = self._get_client_ip(request)
        key_hash = ApiKey.hash_key(raw_key)

        api_key = ApiKey.objects.select_related("user").filter(key_hash=key_hash).first()

        if api_key is None:
            return self.response(
                message="Invalid API key.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not api_key.is_usable:
            return self.response(
                message="API key is inactive or expired.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not api_key.is_ip_allowed(ip):
            return self.response(
                message="IP address not allowed for this API key.",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        user = api_key.user

        if not user.is_active:
            return self.response(
                message="Account is inactive.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        ApiKey.objects.filter(pk=api_key.pk).update(last_used_at=timezone.now())
        token = AccessToken.for_user(user)

        return self.response(
            data={
                "access": str(token),
            },
        )

    def _get_client_ip(self, request) -> str:
        num_proxies = getattr(settings, "NUM_PROXIES", 0)

        if num_proxies > 0:
            forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
            addresses = [address.strip() for address in forwarded.split(",") if address.strip()]
            if len(addresses) >= num_proxies:
                return addresses[-num_proxies]

        return request.META.get("REMOTE_ADDR", "")
