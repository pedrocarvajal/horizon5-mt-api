from typing import ClassVar

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from app.collections.log import Log
from app.http.controllers.base import BaseController
from app.http.permissions.role import IsProducerOrRoot
from app.http.requests.log.create_log import CreateLogRequestSerializer
from app.models import Account


class LogController(BaseController):
    permissions: ClassVar[dict] = {
        "store": [IsProducerOrRoot],
    }

    @action(detail=False, methods=["post"], url_path="")
    def store(self, request: Request) -> Response:
        serializer = CreateLogRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        if not Account.objects.filter(id=data["account_id"], user=request.user).exists():
            raise PermissionDenied("Account not found or not owned by you.")

        strategy_id = data.get("strategy_id")

        Log.create(
            {
                "account_id": data["account_id"],
                "strategy_id": str(strategy_id) if strategy_id else None,
                "level": data["level"],
                "message": data["message"],
            }
        )

        return self.reply(status_code=status.HTTP_201_CREATED)
