import pytest
from rest_framework import status

from app.enums import SystemRole


@pytest.mark.django_db
class TestMe:
    def test_should_return_200_with_user_profile(self, authenticated_client, active_user):
        response = authenticated_client.get("/api/v1/auth/me/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["id"] == str(active_user.pk)
        assert response.data["data"]["email"] == active_user.email
        assert response.data["data"]["role"] == active_user.role
        assert "created_at" in response.data["data"]

    def test_should_return_correct_role_for_root_user(self, root_client, root_user):  # noqa: ARG002
        response = root_client.get("/api/v1/auth/me/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["role"] == SystemRole.ROOT

    def test_should_return_correct_role_for_producer_user(self, producer_client, producer_user):  # noqa: ARG002
        response = producer_client.get("/api/v1/auth/me/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["role"] == SystemRole.PRODUCER

    def test_should_return_correct_role_for_platform_user(self, platform_client, platform_user):  # noqa: ARG002
        response = platform_client.get("/api/v1/auth/me/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["role"] == SystemRole.PLATFORM

    def test_should_return_401_when_not_authenticated(self, api_client):
        response = api_client.get("/api/v1/auth/me/")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_should_return_id_as_string(self, authenticated_client):
        response = authenticated_client.get("/api/v1/auth/me/")

        assert isinstance(response.data["data"]["id"], str)

    def test_should_return_created_at_in_iso_format(self, authenticated_client):
        response = authenticated_client.get("/api/v1/auth/me/")

        created_at = response.data["data"]["created_at"]
        assert "T" in created_at
