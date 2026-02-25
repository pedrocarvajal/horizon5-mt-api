from typing import ClassVar

import structlog
from django.db import connection
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from app.database.mongodb import get_client
from app.http.controllers.base import BaseController
from app.http.permissions.role import IsRootOrPlatform

logger = structlog.get_logger("health")


class HealthController(BaseController):
    permissions: ClassVar[dict] = {
        "check": [IsRootOrPlatform],
    }

    @action(detail=False, methods=["get"], url_path="")
    def check(self, _request: Request) -> Response:
        checks = {
            "postgres": self._check_postgres(),
            "mongodb": self._check_mongodb(),
        }

        all_ok = all(value == "ok" for value in checks.values())

        return self.response(
            data={"status": "ok" if all_ok else "degraded", "checks": checks},
            status_code=status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    def _check_postgres(self) -> str:
        try:
            connection.ensure_connection()
            return "ok"
        except Exception as exc:
            logger.error("health_check_postgres_failed", error=str(exc))
            return "error"

    def _check_mongodb(self) -> str:
        try:
            client = get_client()
            client.admin.command("ping")
            return "ok"
        except Exception as exc:
            logger.error("health_check_mongodb_failed", error=str(exc))
            return "error"
