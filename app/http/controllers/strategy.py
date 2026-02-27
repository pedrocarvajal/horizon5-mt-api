from typing import ClassVar

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from app.http.controllers.base import BaseController
from app.http.permissions.role import IsProducerOrRoot, IsRoot
from app.http.requests.strategy.upsert_strategy import UpsertStrategyRequestSerializer
from app.models import Account, Strategy


class StrategyController(BaseController):
    permissions: ClassVar[dict] = {
        "index": [IsRoot],
        "upsert": [IsProducerOrRoot],
    }

    @action(detail=False, methods=["get"], url_path="")
    def index(self, _request: Request) -> Response:
        strategies = Strategy.objects.select_related("account").all()
        data = [self._serialize_strategy(strategy) for strategy in strategies]

        return self.reply(
            data=data,
            meta={"count": len(data)},
        )

    @action(detail=False, methods=["post"], url_path="")
    def upsert(self, request: Request) -> Response:
        serializer = UpsertStrategyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        account_id = data.pop("account_id")
        strategy_id = data.pop("id")

        if not Account.objects.filter(id=account_id, user=request.user).exists():
            raise PermissionDenied("Account not found or not owned by you.")

        existing = Strategy.objects.filter(id=strategy_id).first()
        if existing and existing.account.user_id != request.user.pk:
            raise PermissionDenied("You do not own this strategy.")

        strategy, created = Strategy.objects.update_or_create(
            id=strategy_id,
            defaults={
                "account_id": account_id,
                **data,
            },
        )

        return self.reply(
            data={"id": str(strategy.id)},
            status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @staticmethod
    def _serialize_strategy(strategy: Strategy) -> dict:
        return {
            "id": str(strategy.id),
            "account_id": strategy.account_id,
            "symbol": strategy.symbol,
            "prefix": strategy.prefix,
            "name": strategy.name,
            "magic_number": strategy.magic_number,
            "balance": str(strategy.balance),
            "created_at": strategy.created_at.isoformat(),
            "updated_at": strategy.updated_at.isoformat(),
        }
