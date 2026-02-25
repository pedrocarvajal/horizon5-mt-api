from typing import ClassVar

import structlog
from django.db import connection
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from app.database.mongodb import get_client
from app.http.controllers.base import BaseController
from app.http.permissions.role import IsRoot

logger = structlog.get_logger("health")


class HealthController(BaseController):
    permission_map: ClassVar[dict] = {
        "check": [AllowAny],
        "detailed": [IsRoot],
    }
    throttle_map: ClassVar[dict] = {
        "check": [],
    }
    default_permissions: ClassVar[list] = [AllowAny]

    def get_authenticators(self):
        if self.action == "check":
            return []
        return super().get_authenticators()

    @action(detail=False, methods=["get"], url_path="")
    def check(self, _request):
        return Response({"status": "ok"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], url_path="detailed")
    def detailed(self, _request):
        checks = {}

        try:
            connection.ensure_connection()
            checks["postgres"] = "ok"
        except Exception as exc:
            logger.error("health_check_postgres_failed", error=str(exc))
            checks["postgres"] = "error"

        try:
            client = get_client()
            client.admin.command("ping")
            checks["mongodb"] = "ok"
        except Exception as exc:
            logger.error("health_check_mongodb_failed", error=str(exc))
            checks["mongodb"] = "error"

        all_ok = all(v == "ok" for v in checks.values())
        return Response(
            {"status": "ok" if all_ok else "degraded", "checks": checks},
            status=status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE,
        )
