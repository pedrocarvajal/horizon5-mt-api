from typing import ClassVar

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from app.collections.strategy_snapshot import StrategySnapshot
from app.http.controllers.base import PaginatedController
from app.http.permissions.role import IsProducerOrRoot, IsRoot
from app.http.requests.strategy_snapshot.create_strategy_snapshot import CreateStrategySnapshotRequestSerializer
from app.http.requests.strategy_snapshot.list_strategy_snapshot import ListStrategySnapshotRequestSerializer
from app.models import Account


class StrategySnapshotController(PaginatedController):
    collection = StrategySnapshot
    list_serializer_class = ListStrategySnapshotRequestSerializer
    orderable_columns: ClassVar[list[str]] = ["nav", "drawdown_pct", "created_at"]
    filterable_columns: ClassVar[list[str]] = []
    integer_columns: ClassVar[set[str]] = set()
    float_columns: ClassVar[set[str]] = set()

    permissions: ClassVar[dict] = {
        "index": [IsRoot],
        "store": [IsProducerOrRoot],
    }

    def get_base_query(self, validated: dict) -> dict:
        query: dict = {"strategy_id": str(validated["strategy_id"])}

        if "account_id" in validated:
            query["account_id"] = validated["account_id"]

        return query

    def serialize_document(self, document: dict) -> dict:
        return {
            "id": str(document["_id"]),
            "account_id": document["account_id"],
            "strategy_id": document["strategy_id"],
            "nav": document["nav"],
            "drawdown_pct": document["drawdown_pct"],
            "daily_pnl": document["daily_pnl"],
            "floating_pnl": document["floating_pnl"],
            "open_order_count": document["open_order_count"],
            "exposure_lots": document["exposure_lots"],
            "created_at": document["created_at"].isoformat(),
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
