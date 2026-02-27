import uuid

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient

from app.enums import SystemRole
from app.models import Account, MediaFile
from tests.feature.conftest import create_user


def upload_url(account_id):
    return f"/api/v1/account/{account_id}/media/upload/"


def create_valid_file(name="test.png", content=b"fake-image-content", content_type="image/png"):
    return SimpleUploadedFile(name, content, content_type=content_type)


@pytest.mark.django_db
class TestUploadMedia:
    def test_should_return_201_with_media_file_data(self, platform_client, account, settings, tmp_path):
        settings.STORAGE_ROOT = str(tmp_path)

        response = platform_client.post(upload_url(account.id), {"file": create_valid_file()}, format="multipart")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        data = response.data["data"]
        assert "id" in data
        assert data["account_id"] == account.id
        assert data["original_name"] == "test.png"
        assert data["content_type"] == "image/png"
        assert data["size"] > 0
        assert "expires_at" in data
        assert "created_at" in data

    def test_should_store_file_on_disk(self, platform_client, account, settings, tmp_path):
        settings.STORAGE_ROOT = str(tmp_path)

        response = platform_client.post(upload_url(account.id), {"file": create_valid_file()}, format="multipart")

        media_file = MediaFile.objects.get(id=response.data["data"]["id"])
        file_path = (
            tmp_path
            / str(media_file.user_id)
            / "files"
            / media_file.created_at.strftime("%Y-%m-%d")
            / media_file.file_name
        )
        assert file_path.is_file()

    def test_should_generate_uuid_file_name_with_original_extension(self, platform_client, account, settings, tmp_path):
        settings.STORAGE_ROOT = str(tmp_path)
        file = create_valid_file(name="report.pdf", content_type="application/pdf")

        response = platform_client.post(upload_url(account.id), {"file": file}, format="multipart")

        file_name = response.data["data"]["file_name"]
        assert file_name.endswith(".pdf")
        uuid.UUID(file_name.rsplit(".", 1)[0])

    def test_should_return_400_when_file_is_missing(self, platform_client, account):
        response = platform_client.post(upload_url(account.id), {}, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_should_return_400_when_file_extension_is_not_allowed(self, platform_client, account):
        file = create_valid_file(name="malware.exe", content_type="application/x-msdownload")

        response = platform_client.post(upload_url(account.id), {"file": file}, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_should_return_400_when_content_type_is_not_allowed(self, platform_client, account):
        file = create_valid_file(name="page.png", content_type="text/html")

        response = platform_client.post(upload_url(account.id), {"file": file}, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_should_return_400_when_file_name_starts_with_dot(self, platform_client, account):
        file = create_valid_file(name=".hidden.png")

        response = platform_client.post(upload_url(account.id), {"file": file}, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_should_return_400_when_file_exceeds_max_size(self, platform_client, account, settings):
        settings.STORAGE_MAX_UPLOAD_SIZE = 10
        file = create_valid_file(content=b"x" * 11)

        response = platform_client.post(upload_url(account.id), {"file": file}, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_should_return_400_when_account_does_not_exist(self, root_client):
        file = create_valid_file()

        response = root_client.post(upload_url(999999999), {"file": file}, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_return_401_when_unauthenticated(self, api_client, account):
        response = api_client.post(upload_url(account.id), {"file": create_valid_file()}, format="multipart")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_should_return_403_when_user_is_not_account_owner(self, authenticated_client, account):
        response = authenticated_client.post(upload_url(account.id), {"file": create_valid_file()}, format="multipart")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_return_403_when_account_owner_has_producer_role(self):
        producer = create_user(email="producer@test.co", role=SystemRole.PRODUCER)
        producer_account = Account.objects.create(id=222333, user=producer)
        client = APIClient()
        client.force_authenticate(user=producer)

        response = client.post(upload_url(producer_account.id), {"file": create_valid_file()}, format="multipart")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_allow_root_user_to_upload(self, root_client, account, settings, tmp_path):
        settings.STORAGE_ROOT = str(tmp_path)

        response = root_client.post(upload_url(account.id), {"file": create_valid_file()}, format="multipart")

        assert response.status_code == status.HTTP_201_CREATED
