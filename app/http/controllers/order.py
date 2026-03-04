from decimal import Decimal
from typing import ClassVar

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from app.collections.order import Order
from app.http.controllers.base import BaseController
from app.http.permissions.role import IsRootOrPlatform
from app.http.requests.order.upsert_order import UpsertOrderRequestSerializer


class OrderController(BaseController):
    permissions: ClassVar[dict] = {
        "upsert": [IsRootOrPlatform],
    }

    @action(detail=False, methods=["post"], url_path="")
    def upsert(self, request: Request) -> Response:
        serializer = UpsertOrderRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        order_id = str(data.pop("id"))
        strategy_id = data.get("strategy_id")
        now = timezone.now()

        document = {
            "account_id": data["account_id"],
            "strategy_id": str(strategy_id) if strategy_id else None,
            "updated_at": now,
        }

        for key, value in data.items():
            if key not in ("account_id", "strategy_id"):
                document[key] = float(value) if isinstance(value, Decimal) else value

        previous = Order.collection().find_one_and_update(
            {"_id": order_id},
            {
                "$set": document,
                "$setOnInsert": {"created_at": now},
            },
            upsert=True,
        )

        is_new = previous is None

        return self.reply(
            data={"id": order_id},
            status_code=status.HTTP_201_CREATED if is_new else status.HTTP_200_OK,
        )
