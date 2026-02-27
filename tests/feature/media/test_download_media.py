from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from app.enums import SystemRole
from app.models import Account
from tests.feature.conftest import create_user
from tests.feature.media.conftest import create_media_file


def download_url(account_id, file_name):
    return f"/api/v1/account/{account_id}/media/{file_name}/download/"


@pytest.mark.django_db
class TestDownloadMedia:
    def test_should_return_file_as_attachment(self, platform_client, account, platform_user, settings, tmp_path):
        settings.STORAGE_ROOT = str(tmp_path)
        media_file = create_media_file(account, platform_user, str(tmp_path))

        response = platform_client.get(download_url(account.id, media_file.file_name))

        assert response.status_code == status.HTTP_200_OK
        assert "attachment" in response["Content-Disposition"]
        assert media_file.original_name in response["Content-Disposition"]

    def test_should_set_safe_content_type_for_known_types(
        self, platform_client, account, platform_user, settings, tmp_path
    ):
        settings.STORAGE_ROOT = str(tmp_path)
        media_file = create_media_file(account, platform_user, str(tmp_path), content_type="image/png")

        response = platform_client.get(download_url(account.id, media_file.file_name))

        assert response["Content-Type"] == "image/png"

    def test_should_fallback_to_octet_stream_for_unknown_content_types(
        self, platform_client, account, platform_user, settings, tmp_path
    ):
        settings.STORAGE_ROOT = str(tmp_path)
        media_file = create_media_file(account, platform_user, str(tmp_path), content_type="text/csv")

        response = platform_client.get(download_url(account.id, media_file.file_name))

        assert response["Content-Type"] == "application/octet-stream"

    def test_should_set_nosniff_header(self, platform_client, account, platform_user, settings, tmp_path):
        settings.STORAGE_ROOT = str(tmp_path)
        media_file = create_media_file(account, platform_user, str(tmp_path))

        response = platform_client.get(download_url(account.id, media_file.file_name))

        assert response["X-Content-Type-Options"] == "nosniff"

    def test_should_return_410_when_file_has_expired(self, platform_client, account, platform_user, settings, tmp_path):
        settings.STORAGE_ROOT = str(tmp_path)
        media_file = create_media_file(
            account,
            platform_user,
            str(tmp_path),
            expires_at=timezone.now() - timedelta(hours=1),
        )

        response = platform_client.get(download_url(account.id, media_file.file_name))

        assert response.status_code == status.HTTP_410_GONE
        assert response.data["success"] is False
        assert response.data["message"] == "File has expired."

    def test_should_return_404_when_file_not_found_on_disk(
        self, platform_client, account, platform_user, settings, tmp_path
    ):
        settings.STORAGE_ROOT = str(tmp_path)
        media_file = create_media_file(account, platform_user, str(tmp_path), write_file=False)

        response = platform_client.get(download_url(account.id, media_file.file_name))

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["message"] == "File not found on disk."

    def test_should_return_404_when_media_file_record_not_found(self, platform_client, account, settings, tmp_path):
        settings.STORAGE_ROOT = str(tmp_path)

        response = platform_client.get(download_url(account.id, "nonexistent.png"))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_should_return_400_when_account_does_not_exist(self, root_client):
        response = root_client.get(download_url(999999999, "test.png"))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_return_401_when_unauthenticated(self, api_client, account):
        response = api_client.get(download_url(account.id, "test.png"))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_should_return_403_when_user_is_not_account_owner(
        self, authenticated_client, account, platform_user, settings, tmp_path
    ):
        settings.STORAGE_ROOT = str(tmp_path)
        media_file = create_media_file(account, platform_user, str(tmp_path))

        response = authenticated_client.get(download_url(account.id, media_file.file_name))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_allow_account_owner_with_producer_role_to_download(self, settings, tmp_path):
        settings.STORAGE_ROOT = str(tmp_path)
        producer = create_user(email="producer@test.co", role=SystemRole.PRODUCER)
        producer_account = Account.objects.create(id=222333, user=producer)
        media_file = create_media_file(producer_account, producer, str(tmp_path))
        client = APIClient()
        client.force_authenticate(user=producer)

        response = client.get(download_url(producer_account.id, media_file.file_name))

        assert response.status_code == status.HTTP_200_OK

    def test_should_allow_root_user_to_download(self, root_client, account, platform_user, settings, tmp_path):
        settings.STORAGE_ROOT = str(tmp_path)
        media_file = create_media_file(account, platform_user, str(tmp_path))

        response = root_client.get(download_url(account.id, media_file.file_name))

        assert response.status_code == status.HTTP_200_OK
