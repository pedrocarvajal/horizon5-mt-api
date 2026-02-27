from typing import ClassVar

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from app.collections.account_snapshot import AccountSnapshot
from app.http.controllers.base import PaginatedController
from app.http.permissions.role import IsProducerOrRoot, IsRoot
from app.http.requests.account_snapshot.create_account_snapshot import CreateAccountSnapshotRequestSerializer
from app.http.requests.account_snapshot.list_account_snapshot import ListAccountSnapshotRequestSerializer
from app.models import Account


class AccountSnapshotController(PaginatedController):
    collection = AccountSnapshot
    list_serializer_class = ListAccountSnapshotRequestSerializer
    orderable_columns: ClassVar[list[str]] = ["balance", "equity", "profit", "drawdown_pct", "created_at"]
    filterable_columns: ClassVar[list[str]] = []
    integer_columns: ClassVar[set[str]] = set()
    float_columns: ClassVar[set[str]] = set()

    permissions: ClassVar[dict] = {
        "index": [IsRoot],
        "store": [IsProducerOrRoot],
    }

    def get_base_query(self, validated: dict) -> dict:
        return {"account_id": validated["account_id"]}

    def serialize_document(self, document: dict) -> dict:
        return {
            "id": str(document["_id"]),
            "account_id": document["account_id"],
            "balance": document["balance"],
            "equity": document["equity"],
            "profit": document["profit"],
            "margin_level": document["margin_level"],
            "open_positions": document["open_positions"],
            "drawdown_pct": document["drawdown_pct"],
            "daily_pnl": document["daily_pnl"],
            "floating_pnl": document["floating_pnl"],
            "open_order_count": document["open_order_count"],
            "exposure_lots": document["exposure_lots"],
            "created_at": document["created_at"].isoformat(),
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
