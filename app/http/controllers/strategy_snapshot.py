from typing import ClassVar

from pymongo import DESCENDING
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from app.collections.strategy_snapshot import StrategySnapshot
from app.http.controllers.base import BaseController
from app.http.permissions.role import IsProducerOrRoot, IsRoot
from app.http.requests.strategy_snapshot.create_strategy_snapshot import CreateStrategySnapshotRequestSerializer
from app.http.requests.strategy_snapshot.list_strategy_snapshot import ListStrategySnapshotRequestSerializer
from app.models import Account


class StrategySnapshotController(BaseController):
    permissions: ClassVar[dict] = {
        "index": [IsRoot],
        "store": [IsProducerOrRoot],
    }

    @action(detail=False, methods=["get"], url_path="")
    def index(self, request: Request) -> Response:
        serializer = ListStrategySnapshotRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data
        page = validated["page"]
        per_page = validated["per_page"]
        offset = (page - 1) * per_page
        query: dict = {"strategy_id": str(validated["strategy_id"])}

        if "account_id" in validated:
            query["account_id"] = validated["account_id"]

        total = StrategySnapshot.count(query)

        snapshots = list(
            StrategySnapshot.where(query)
            .sort([("created_at", DESCENDING), ("_id", DESCENDING)])
            .skip(offset)
            .limit(per_page)
        )

        data = [self._serialize_snapshot(snapshot) for snapshot in snapshots]

        return self.reply(
            data=data,
            meta={
                "count": len(data),
                "pagination": {
                    "total": total,
                    "page": page,
                    "per_page": per_page,
                    "total_pages": (total + per_page - 1) // per_page if total > 0 else 0,
                },
            },
        )

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

    @staticmethod
    def _serialize_snapshot(snapshot: dict) -> dict:
        return {
            "id": str(snapshot["_id"]),
            "account_id": snapshot["account_id"],
            "strategy_id": snapshot["strategy_id"],
            "nav": snapshot["nav"],
            "drawdown_pct": snapshot["drawdown_pct"],
            "daily_pnl": snapshot["daily_pnl"],
            "floating_pnl": snapshot["floating_pnl"],
            "open_order_count": snapshot["open_order_count"],
            "exposure_lots": snapshot["exposure_lots"],
            "created_at": snapshot["created_at"].isoformat(),
        }
