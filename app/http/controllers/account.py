from typing import ClassVar

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response

from app.http.controllers.base import BaseController
from app.http.permissions.role import IsProducerOrRoot
from app.http.requests.account.upsert_account import UpsertAccountRequestSerializer
from app.models import Account


class AccountController(BaseController):
    permissions: ClassVar[dict] = {
        "upsert": [IsProducerOrRoot],
    }

    @action(detail=False, methods=["post"], url_path="")
    def upsert(self, request: Request) -> Response:
        serializer = UpsertAccountRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        account_id = data.pop("account_id")
        existing = Account.objects.filter(id=account_id).first()

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
