from typing import ClassVar, cast

from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from app.enums import SystemRole
from app.http.controllers.base import BaseController
from app.http.permissions.role import IsRoot
from app.http.requests.account.list_account import ListAccountRequestSerializer
from app.http.requests.account.update_account import UpdateAccountRequestSerializer
from app.http.requests.account.upsert_account import UpsertAccountRequestSerializer
from app.models import Account
from app.models.user import User


class AccountController(BaseController):
    _orderable_columns: ClassVar[list[str]] = ["id", "created_at", "updated_at", "balance", "equity"]
    _filterable_columns: ClassVar[list[str]] = ["id", "status"]
    _integer_columns: ClassVar[set[str]] = {"id"}
    _float_columns: ClassVar[set[str]] = set()

    permissions: ClassVar[dict] = {
        "index": [IsRoot],
        "show": [IsAuthenticated],
        "upsert": [IsAuthenticated],
        "update": [IsAuthenticated],
    }

    @action(detail=False, methods=["get"], url_path="")
    def index(self, request: Request) -> Response:
        serializer = ListAccountRequestSerializer(
            data=request.query_params,
            context={
                "orderable_columns": self._orderable_columns,
                "filterable_columns": self._filterable_columns,
                "integer_columns": self._integer_columns,
                "float_columns": self._float_columns,
            },
        )
        serializer.is_valid(raise_exception=True)

        validated = serializer.validated_data
        page = validated["page"]
        per_page = validated["per_page"]
        offset = (page - 1) * per_page

        queryset = Account.objects.select_related("user").all()

        if "filter_by" in validated and "filter_value" in validated:
            filter_value = serializer.get_cast_filter_value(validated["filter_by"], validated["filter_value"])
            queryset = queryset.filter(**{validated["filter_by"]: filter_value})

        queryset = queryset.order_by(validated["order_by"])

        total = queryset.count()
        data = [self._serialize_account(account) for account in queryset[offset : offset + per_page]]

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
                "filterable_columns": self._filterable_columns,
                "orderable_columns": self._orderable_columns,
            },
        )

    @action(detail=False, methods=["get"], url_path="<int:id>")
    def show(self, request: Request, id: int = 0) -> Response:
        user = cast(User, request.user)
        is_privileged = user.role in (SystemRole.PLATFORM, SystemRole.ROOT)

        account = Account.objects.select_related("user").filter(id=id).first()

        if account is None:
            return self.reply(
                data={"detail": "Account not found."},
                status_code=status.HTTP_404_NOT_FOUND,
            )

        if not is_privileged and account.user_id != user.pk:
            raise PermissionDenied("You do not own this account.")

        return self.reply(data=self._serialize_account(account))

    @action(detail=False, methods=["post"], url_path="")
    def upsert(self, request: Request) -> Response:
        serializer = UpsertAccountRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        account_id = data.pop("account_id")
        user = cast(User, request.user)
        is_platform = user.role == SystemRole.PLATFORM

        trading_fields = {key: value for key, value in data.items() if value is not None}

        with transaction.atomic():
            existing = Account.objects.select_for_update().filter(id=account_id).first()

            if is_platform:
                if existing is None:
                    return self.reply(
                        data={"detail": "Account not found."},
                        status_code=status.HTTP_404_NOT_FOUND,
                    )

                Account.objects.filter(id=account_id).update(**trading_fields)
                account = existing

                return self.reply(
                    data={"id": account.id},
                    status_code=status.HTTP_200_OK,
                )

            if existing and existing.user_id != user.pk:
                raise PermissionDenied("You do not own this account.")

            account, created = Account.objects.update_or_create(
                id=account_id,
                defaults={
                    "user": user,
                    **trading_fields,
                },
            )

        return self.reply(
            data={"id": account.id},
            status_code=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    @action(detail=False, methods=["patch"], url_path="<int:id>")
    def update(self, request: Request, id: int = 0) -> Response:
        serializer = UpdateAccountRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = cast(User, request.user)
        is_privileged = user.role in (SystemRole.PLATFORM, SystemRole.ROOT)

        with transaction.atomic():
            existing = Account.objects.select_for_update().filter(id=id).first()

            if existing is None:
                return self.reply(
                    data={"detail": "Account not found."},
                    status_code=status.HTTP_404_NOT_FOUND,
                )

            if not is_privileged and existing.user_id != user.pk:
                raise PermissionDenied("You do not own this account.")

            fields_to_update = {key: value for key, value in serializer.validated_data.items() if value is not None}
            Account.objects.filter(id=id).update(**fields_to_update)

        return self.reply(
            data={"id": id},
            status_code=status.HTTP_200_OK,
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
            "status": account.status,
            "created_at": account.created_at.isoformat(),
            "updated_at": account.updated_at.isoformat(),
        }
