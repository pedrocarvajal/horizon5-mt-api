from typing import ClassVar

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from app.collections.strategy_snapshot import StrategySnapshot
from app.http.controllers.base import BaseController
from app.http.permissions.role import IsProducerOrRoot
from app.http.requests.strategy_snapshot.create_strategy_snapshot import CreateStrategySnapshotRequestSerializer
from app.models import Account


class StrategySnapshotController(BaseController):
    permissions: ClassVar[dict] = {
        "store": [IsProducerOrRoot],
    }

    @action(detail=False, methods=["post"], url_path="")
    def store(self, request: Request) -> Response:
        serializer = CreateStrategySnapshotRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        if not Account.objects.filter(id=data["account_id"], user=request.user).exists():
            raise PermissionDenied("Account not found or not owned by you.")

        StrategySnapshot.create(
            {
                "account_id": data["account_id"],
                "strategy_id": str(data["strategy_id"]),
                "nav": float(data["nav"]),
                "drawdown_pct": float(data["drawdown_pct"]),
                "daily_pnl": float(data["daily_pnl"]),
                "floating_pnl": float(data["floating_pnl"]),
                "open_order_count": data["open_order_count"],
                "exposure_lots": float(data["exposure_lots"]),
            }
        )

        return self.reply(status_code=status.HTTP_201_CREATED)
