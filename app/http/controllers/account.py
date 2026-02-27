from typing import ClassVar

from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from app.http.controllers.base import BaseController
from app.http.permissions.role import IsProducerOrRoot, IsRoot
from app.http.requests.account.upsert_account import UpsertAccountRequestSerializer
from app.models import Account


class AccountController(BaseController):
    permissions: ClassVar[dict] = {
        "index": [IsRoot],
        "upsert": [IsProducerOrRoot],
    }

    @action(detail=False, methods=["get"], url_path="")
    def index(self, _request: Request) -> Response:
        accounts = Account.objects.select_related("user").all()

        data = [self._serialize_account(account) for account in accounts]

        return self.reply(
            data=data,
            meta={"count": len(data)},
        )

    @action(detail=False, methods=["post"], url_path="")
    def upsert(self, request: Request) -> Response:
        serializer = UpsertAccountRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        account_id = data.pop("account_id")

        with transaction.atomic():
            existing = Account.objects.select_for_update().filter(id=account_id).first()

            if existing and existing.user_id != request.user.pk:
                raise PermissionDenied("You do not own this account.")

            account, created = Account.objects.update_or_create(
                id=account_id,
                defaults={
                    "user": request.user,
                    **{key: value for key, value in data.items() if value is not None},
                },
            )

        return self.reply(
            data={"id": account.id},
            status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @staticmethod
    def _serialize_account(account: Account) -> dict:
        return {
            "id": account.id,
            "user_id": str(account.user_id),
            "user_email": account.user.email,
            "broker": account.broker,
            "server": account.server,
            "currency": account.currency,
            "leverage": account.leverage,
            "balance": str(account.balance),
            "equity": str(account.equity),
            "margin": str(account.margin),
            "free_margin": str(account.free_margin),
            "profit": str(account.profit),
            "margin_level": str(account.margin_level),
            "created_at": account.created_at.isoformat(),
            "updated_at": account.updated_at.isoformat(),
        }
