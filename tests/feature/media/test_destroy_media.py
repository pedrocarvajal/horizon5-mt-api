import pytest
from rest_framework import status
from rest_framework.test import APIClient

from app.enums import SystemRole
from app.models import Account, MediaFile
from tests.feature.conftest import create_user
from tests.feature.media.conftest import create_media_file


def destroy_url(account_id, file_name):
    return f"/api/v1/account/{account_id}/media/{file_name}/"


@pytest.mark.django_db
class TestDestroyMedia:
    def test_should_return_204_and_delete_record(self, platform_client, account, platform_user, settings, tmp_path):
        settings.STORAGE_ROOT = str(tmp_path)
        media_file = create_media_file(account, platform_user, str(tmp_path))

        response = platform_client.delete(destroy_url(account.id, media_file.file_name))

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not MediaFile.objects.filter(id=media_file.id).exists()

    def test_should_delete_file_from_disk(self, platform_client, account, platform_user, settings, tmp_path):
        settings.STORAGE_ROOT = str(tmp_path)
        media_file = create_media_file(account, platform_user, str(tmp_path))
        file_path = (
            tmp_path
            / str(platform_user.pk)
            / "files"
            / media_file.created_at.strftime("%Y-%m-%d")
            / media_file.file_name
        )
        assert file_path.is_file()

        platform_client.delete(destroy_url(account.id, media_file.file_name))

        assert not file_path.is_file()

    def test_should_remove_empty_parent_directory(self, platform_client, account, platform_user, settings, tmp_path):
        settings.STORAGE_ROOT = str(tmp_path)
        media_file = create_media_file(account, platform_user, str(tmp_path))
        file_path = (
            tmp_path
            / str(platform_user.pk)
            / "files"
            / media_file.created_at.strftime("%Y-%m-%d")
            / media_file.file_name
        )
        parent_directory = file_path.parent

        platform_client.delete(destroy_url(account.id, media_file.file_name))

        assert not parent_directory.is_dir()

    def test_should_succeed_even_when_file_not_on_disk(
        self, platform_client, account, platform_user, settings, tmp_path
    ):
        settings.STORAGE_ROOT = str(tmp_path)
        media_file = create_media_file(account, platform_user, str(tmp_path), write_file=False)

        response = platform_client.delete(destroy_url(account.id, media_file.file_name))

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not MediaFile.objects.filter(id=media_file.id).exists()

    def test_should_return_404_when_media_file_not_found(self, platform_client, account, settings, tmp_path):
        settings.STORAGE_ROOT = str(tmp_path)

        response = platform_client.delete(destroy_url(account.id, "nonexistent.png"))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_should_return_400_when_account_does_not_exist(self, root_client):
        response = root_client.delete(destroy_url(999999999, "test.png"))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_return_401_when_unauthenticated(self, api_client, account):
        response = api_client.delete(destroy_url(account.id, "test.png"))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_should_return_403_when_user_is_not_account_owner(
        self, authenticated_client, account, platform_user, settings, tmp_path
    ):
        settings.STORAGE_ROOT = str(tmp_path)
        media_file = create_media_file(account, platform_user, str(tmp_path))

        response = authenticated_client.delete(destroy_url(account.id, media_file.file_name))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_return_403_when_account_owner_has_producer_role(self, settings, tmp_path):
        settings.STORAGE_ROOT = str(tmp_path)
        producer = create_user(email="producer@test.co", role=SystemRole.PRODUCER)
        producer_account = Account.objects.create(id=222333, user=producer)
        media_file = create_media_file(producer_account, producer, str(tmp_path))
        client = APIClient()
        client.force_authenticate(user=producer)

        response = client.delete(destroy_url(producer_account.id, media_file.file_name))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_allow_root_user_to_destroy(self, root_client, account, platform_user, settings, tmp_path):
        settings.STORAGE_ROOT = str(tmp_path)
        media_file = create_media_file(account, platform_user, str(tmp_path))

        response = root_client.delete(destroy_url(account.id, media_file.file_name))

        assert response.status_code == status.HTTP_204_NO_CONTENT
