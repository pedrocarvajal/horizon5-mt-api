from typing import ClassVar

from pymongo import DESCENDING
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from app.collections.account_snapshot import AccountSnapshot
from app.http.controllers.base import BaseController
from app.http.permissions.role import IsProducerOrRoot, IsRoot
from app.http.requests.account_snapshot.create_account_snapshot import CreateAccountSnapshotRequestSerializer
from app.http.requests.account_snapshot.list_account_snapshot import ListAccountSnapshotRequestSerializer
from app.models import Account


class AccountSnapshotController(BaseController):
    permissions: ClassVar[dict] = {
        "index": [IsRoot],
        "store": [IsProducerOrRoot],
    }

    @action(detail=False, methods=["get"], url_path="")
    def index(self, request: Request) -> Response:
        serializer = ListAccountSnapshotRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data
        page = validated["page"]
        per_page = validated["per_page"]
        offset = (page - 1) * per_page

        query: dict = {"account_id": validated["account_id"]}

        total = AccountSnapshot.count(query)

        snapshots = list(
            AccountSnapshot.where(query)
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

    @staticmethod
    def _serialize_snapshot(snapshot: dict) -> dict:
        return {
            "id": str(snapshot["_id"]),
            "account_id": snapshot["account_id"],
            "balance": snapshot["balance"],
            "equity": snapshot["equity"],
            "profit": snapshot["profit"],
            "margin_level": snapshot["margin_level"],
            "open_positions": snapshot["open_positions"],
            "drawdown_pct": snapshot["drawdown_pct"],
            "daily_pnl": snapshot["daily_pnl"],
            "floating_pnl": snapshot["floating_pnl"],
            "open_order_count": snapshot["open_order_count"],
            "exposure_lots": snapshot["exposure_lots"],
            "created_at": snapshot["created_at"].isoformat(),
        }
