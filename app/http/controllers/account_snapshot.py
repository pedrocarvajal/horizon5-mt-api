from typing import ClassVar

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from app.collections.account_snapshot import AccountSnapshot
from app.http.controllers.base import BaseController
from app.http.permissions.role import IsProducerOrRoot
from app.http.requests.account_snapshot.create_account_snapshot import CreateAccountSnapshotRequestSerializer
from app.models import Account


class AccountSnapshotController(BaseController):
    permissions: ClassVar[dict] = {
        "store": [IsProducerOrRoot],
    }

    @action(detail=False, methods=["post"], url_path="")
    def store(self, request: Request) -> Response:
        serializer = CreateAccountSnapshotRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        if not Account.objects.filter(id=data["account_id"], user=request.user).exists():
            raise PermissionDenied("Account not found or not owned by you.")

        AccountSnapshot.create(
            {
                "account_id": data["account_id"],
                "balance": float(data["balance"]),
                "equity": float(data["equity"]),
                "profit": float(data["profit"]),
                "margin_level": float(data["margin_level"]),
                "open_positions": data["open_positions"],
                "drawdown_pct": float(data["drawdown_pct"]),
                "daily_pnl": float(data["daily_pnl"]),
                "floating_pnl": float(data["floating_pnl"]),
                "open_order_count": data["open_order_count"],
                "exposure_lots": float(data["exposure_lots"]),
            }
        )

        return self.reply(status_code=status.HTTP_201_CREATED)
