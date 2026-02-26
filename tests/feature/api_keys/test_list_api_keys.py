import pytest
from rest_framework import status

from app.models import ApiKey
from tests.feature.conftest import create_user

URL = "/api/v1/api-keys/"


def create_api_key(user, name="Test Key", **kwargs):
    raw_key, key_hash = ApiKey.generate_key()
    return ApiKey.objects.create(
        user=user,
        name=name,
        key_hash=key_hash,
        prefix=raw_key[: ApiKey.PREFIX_LENGTH],
        **kwargs,
    )


@pytest.mark.django_db
class TestListApiKeys:
    def test_should_return_200_with_empty_list_when_no_keys_exist(self, authenticated_client):
        response = authenticated_client.get(URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"] == []
        assert response.data["meta"]["count"] == 0

    def test_should_return_200_with_users_api_keys(self, authenticated_client, active_user):
        create_api_key(active_user, name="Key One")
        create_api_key(active_user, name="Key Two")

        response = authenticated_client.get(URL)

        assert response.status_code == status.HTTP_200_OK
        names = {key["name"] for key in response.data["data"]}
        assert names == {"Key One", "Key Two"}

    def test_should_return_only_own_keys_for_regular_user(self, authenticated_client, active_user, db):  # noqa: ARG002
        create_api_key(active_user, name="My Key")
        other_user = create_user(email="other@test.co")
        create_api_key(other_user, name="Other Key")

        response = authenticated_client.get(URL)

        assert len(response.data["data"]) == 1
        assert response.data["data"][0]["name"] == "My Key"

    def test_should_return_all_keys_for_root_user(self, root_client, root_user, active_user):
        create_api_key(root_user, name="Root Key")
        create_api_key(active_user, name="User Key")

        response = root_client.get(URL)

        assert len(response.data["data"]) == 2
        names = {key["name"] for key in response.data["data"]}
        assert names == {"Root Key", "User Key"}

    def test_should_include_user_fields_for_root_user(self, root_client, active_user):
        create_api_key(active_user, name="User Key")

        response = root_client.get(URL)

        key_data = response.data["data"][0]
        assert "user_id" in key_data
        assert "user_email" in key_data
        assert key_data["user_email"] == active_user.email

    def test_should_not_include_user_fields_for_regular_user(self, authenticated_client, active_user):
        create_api_key(active_user, name="My Key")

        response = authenticated_client.get(URL)

        key_data = response.data["data"][0]
        assert "user_id" not in key_data
        assert "user_email" not in key_data

    def test_should_return_meta_with_correct_count(self, authenticated_client, active_user):
        create_api_key(active_user, name="Key One")
        create_api_key(active_user, name="Key Two")
        create_api_key(active_user, name="Key Three")

        response = authenticated_client.get(URL)

        assert response.data["meta"]["count"] == 3

    def test_should_return_401_when_unauthenticated(self, api_client):
        response = api_client.get(URL)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False
