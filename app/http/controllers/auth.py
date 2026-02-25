from typing import ClassVar

import structlog
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from app.http.controllers.base import BaseController
from app.http.middleware.login_throttle import LoginThrottle
from app.http.requests.auth.login import LoginRequestSerializer
from app.http.resources.user import UserResource

logger = structlog.get_logger("audit")


class AuthController(BaseController):
    permissions: ClassVar[dict] = {
        "login": [AllowAny],
        "me": [IsAuthenticated],
    }

    throttles: ClassVar[dict] = {
        "login": [LoginThrottle],
        "me": [],
    }

    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request) -> Response:
        serializer = LoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        ip = self._get_client_ip(request)

        user = authenticate(
            request,
            email=email,
            password=password,
        )

        if user is None:
            LoginThrottle.record_failure(email, ip)
            logger.warning("login_failed", email=email, ip=ip, reason="invalid_credentials")

            return self.response(
                message="Invalid credentials.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            logger.warning("login_failed", email=email, ip=ip, reason="inactive_account")

            return self.response(
                message="Account is inactive.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        LoginThrottle.clear_login_attempts(email)
        logger.info("login_success", user_id=str(user.pk), ip=ip)
        token = AccessToken.for_user(user)

        return self.response(
            data={
                "access": str(token),
            },
        )

    @action(detail=False, methods=["get"], url_path="me")
    def me(self, request) -> Response:
        serializer = UserResource(request.user)

        return self.response(
            data=serializer.data,
        )

    def _get_client_ip(self, request) -> str:
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")

        if forwarded:
            return forwarded.split(",")[0].strip()

        return request.META.get("REMOTE_ADDR")
