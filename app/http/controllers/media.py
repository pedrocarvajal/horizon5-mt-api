import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import ClassVar, cast
from uuid import UUID

from django.conf import settings
from django.http import FileResponse
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response

from app.http.controllers.base import BaseController
from app.http.permissions.media import CanDownloadMedia, CanUploadMedia
from app.http.requests.media.upload import UploadMediaRequestSerializer
from app.http.resources.media_file import MediaFileResource
from app.models import Account, MediaFile


class MediaController(BaseController):
    parser_classes: ClassVar[list] = [MultiPartParser]

    permissions: ClassVar[dict] = {
        "upload": [CanUploadMedia],
        "download": [CanDownloadMedia],
        "destroy": [CanUploadMedia],
    }

    @action(detail=False, methods=["post"], url_path="upload")
    def upload(self, request: Request, id: UUID) -> Response:
        self._validate_account(id)
        serializer = UploadMediaRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uploaded_file = serializer.validated_data["file"]
        now = timezone.now()
        file_extension = Path(uploaded_file.name).suffix
        file_name = f"{uuid.uuid4()}{file_extension}"

        self._store_file(uploaded_file, cast(UUID, request.user.pk), now, file_name)

        media_file = MediaFile.objects.create(
            account_id=id,
            user=request.user,
            file_name=file_name,
            original_name=uploaded_file.name,
            content_type=uploaded_file.content_type or "application/octet-stream",
            size=uploaded_file.size,
            expires_at=now + timedelta(hours=settings.STORAGE_FILE_EXPIRATION_HOURS),
        )

        return self.reply(
            data=MediaFileResource(media_file).data,
            status_code=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, _request: Request, id: UUID, file_name: str) -> Response | FileResponse:
        self._validate_account(id)
        media_file = self._get_media_file(id, file_name)

        if media_file.expires_at < timezone.now():
            return self.reply(
                message="File has expired.",
                status_code=status.HTTP_410_GONE,
            )

        file_path = self._build_file_path(media_file.user_id, media_file.created_at, file_name)

        if not file_path.is_file():
            return self.reply(
                message="File not found on disk.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        safe_content_types = {"image/jpeg", "image/png", "image/gif", "image/webp", "application/pdf"}
        safe_content_type = (
            media_file.content_type if media_file.content_type in safe_content_types else "application/octet-stream"
        )

        response = FileResponse(
            file_path.open("rb"),
            content_type=safe_content_type,
            as_attachment=True,
            filename=media_file.original_name,
        )
        response["X-Content-Type-Options"] = "nosniff"
        return response

    @action(detail=True, methods=["delete"], url_path="")
    def destroy(self, _request: Request, id: UUID, file_name: str) -> Response:
        self._validate_account(id)
        media_file = self._get_media_file(id, file_name)
        file_path = self._build_file_path(media_file.user_id, media_file.created_at, file_name)

        if file_path.is_file():
            file_path.unlink()

            parent_directory = file_path.parent
            if parent_directory.is_dir() and not any(parent_directory.iterdir()):
                parent_directory.rmdir()

        media_file.delete()

        return self.reply(status_code=status.HTTP_204_NO_CONTENT)

    def _validate_account(self, account_id: UUID) -> None:
        if not Account.objects.filter(id=account_id).exists():
            raise serializers.ValidationError({"detail": "Account not found."})

    def _get_media_file(self, account_id: UUID, file_name: str) -> MediaFile:
        media_file = MediaFile.objects.filter(account_id=account_id, file_name=file_name).first()
        if media_file is None:
            raise NotFound("File not found.")
        return media_file

    def _build_file_path(self, user_id: UUID, created_at: datetime, file_name: str) -> Path:
        return Path(settings.STORAGE_ROOT) / str(user_id) / "files" / created_at.strftime("%Y-%m-%d") / file_name

    def _store_file(self, uploaded_file, user_id: UUID, created_at: datetime, file_name: str) -> None:
        file_path = self._build_file_path(user_id, created_at, file_name)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with file_path.open("wb") as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
