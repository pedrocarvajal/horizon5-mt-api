from typing import ClassVar, cast

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from app.enums import SystemRole
from app.http.controllers.base import BaseController
from app.http.permissions.api_key import IsApiKeyOwner
from app.http.requests.api_key.create_api_key import CreateApiKeyRequestSerializer
from app.http.requests.api_key.update_api_key import UpdateApiKeyRequestSerializer
from app.models import ApiKey
from app.models.user import User


class ApiKeyController(BaseController):
    permissions: ClassVar[dict] = {
        "store": [IsApiKeyOwner],
        "index": [IsApiKeyOwner],
        "show": [IsApiKeyOwner],
        "update": [IsApiKeyOwner],
        "destroy": [IsApiKeyOwner],
    }

    @action(detail=False, methods=["post"], url_path="")
    def store(self, request) -> Response:
        serializer = CreateApiKeyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = cast(User, request.user)
        raw_key, key_hash = ApiKey.generate_key()

        api_key = ApiKey.objects.create(
            user=user,
            name=serializer.validated_data["name"],
            key_hash=key_hash,
            prefix=raw_key[: ApiKey.PREFIX_LENGTH],
            allowed_ips=serializer.validated_data["allowed_ips"],
            expires_at=serializer.validated_data.get("expires_at"),
        )

        data = self._serialize_api_key(api_key, user)
        data["key"] = raw_key

        return self.reply(
            data=data,
            message="API key created. Store the key securely, it will not be shown again.",
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"], url_path="")
    def index(self, request) -> Response:
        user = cast(User, request.user)

        if self._is_root(user):
            api_keys = ApiKey.objects.select_related("user").all()
        else:
            api_keys = ApiKey.objects.filter(user=user)

        data = [self._serialize_api_key(key, user) for key in api_keys]

        return self.reply(
            data=data,
            meta={"count": len(data)},
        )

    @action(detail=False, methods=["get"], url_path="<uuid:id>")
    def show(self, request, id=None) -> Response:
        user = cast(User, request.user)
        api_key = self._find_api_key(id, user)

        data = self._serialize_api_key(api_key, user)
        data["updated_at"] = api_key.updated_at.isoformat()

        return self.reply(data=data)

    @action(detail=False, methods=["patch"], url_path="<uuid:id>")
    def update(self, request, id=None) -> Response:
        serializer = UpdateApiKeyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = cast(User, request.user)
        api_key = self._find_api_key(id, user)

        validated = serializer.validated_data

        for field in ("name", "allowed_ips", "is_active", "expires_at"):
            if field in validated:
                setattr(api_key, field, validated[field])

        api_key.save()

        data = self._serialize_api_key(api_key, user)
        data["updated_at"] = api_key.updated_at.isoformat()

        return self.reply(data=data)

    @action(detail=False, methods=["delete"], url_path="<uuid:id>")
    def destroy(self, request, id=None) -> Response:
        user = cast(User, request.user)
        api_key = self._find_api_key(id, user)

        api_key.delete()

        return self.reply(message="API key deleted.")

    def _find_api_key(self, api_key_id, user: User) -> ApiKey:
        queryset = ApiKey.objects.select_related("user").filter(id=api_key_id)

        if not self._is_root(user):
            queryset = queryset.filter(user=user)

        api_key = queryset.first()

        if api_key is None:
            raise NotFound("API key not found.")

        return api_key

    def _serialize_api_key(self, api_key: ApiKey, requester: User) -> dict:
        data = {
            "id": str(api_key.id),
            "name": api_key.name,
            "prefix": api_key.prefix,
            "allowed_ips": api_key.allowed_ips,
            "is_active": api_key.is_active,
            "is_expired": api_key.is_expired,
            "expires_at": api_key.expires_at.isoformat() if api_key.expires_at else None,
            "last_used_at": api_key.last_used_at.isoformat() if api_key.last_used_at else None,
            "created_at": api_key.created_at.isoformat(),
        }

        if self._is_root(requester):
            data["user_id"] = str(api_key.user.pk)
            data["user_email"] = api_key.user.email

        return data

    @staticmethod
    def _is_root(user: User) -> bool:
        return user.role == SystemRole.ROOT
