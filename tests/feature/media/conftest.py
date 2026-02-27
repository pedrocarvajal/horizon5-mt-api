import uuid
from datetime import timedelta
from pathlib import Path

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from app.enums import SystemRole
from app.models import Account, MediaFile
from tests.feature.conftest import create_user


def create_media_file(account, user, storage_root, *, write_file=True, **overrides):
    file_name = overrides.pop("file_name", f"{uuid.uuid4()}.png")
    defaults = {
        "account": account,
        "user": user,
        "file_name": file_name,
        "original_name": "test.png",
        "content_type": "image/png",
        "size": 100,
        "expires_at": timezone.now() + timedelta(hours=24),
    }
    defaults.update(overrides)
    media_file = MediaFile.objects.create(**defaults)

    if write_file:
        file_path = Path(storage_root) / str(user.pk) / "files" / media_file.created_at.strftime("%Y-%m-%d") / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(b"fake-image-content")

    return media_file


@pytest.fixture()
def platform_user(db):  # noqa: ARG001
    return create_user(email="platform@test.co", role=SystemRole.PLATFORM)


@pytest.fixture()
def platform_client(platform_user):
    client = APIClient()
    client.force_authenticate(user=platform_user)
    return client


@pytest.fixture()
def account(platform_user):
    return Account.objects.create(id=111222, user=platform_user)
