import pytest
from rest_framework import status

from tests.feature.conftest import TEST_PASSWORD


def get_tokens(api_client, user):
    response = api_client.post("/api/v1/auth/login/", {"email": user.email, "password": TEST_PASSWORD})
    return response.data["data"]["access"], response.data["data"]["refresh"]


@pytest.mark.django_db
class TestLogout:
    def test_should_return_200_on_successful_logout(self, api_client, active_user):
        access_token, refresh_token = get_tokens(api_client, active_user)

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = api_client.post("/api/v1/auth/logout/", {"refresh": refresh_token})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["message"] == "Logged out successfully"

    def test_should_blacklist_refresh_token_after_logout(self, api_client, active_user):
        access_token, refresh_token = get_tokens(api_client, active_user)

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        api_client.post("/api/v1/auth/logout/", {"refresh": refresh_token})

        api_client.credentials()
        response = api_client.post("/api/v1/auth/refresh/", {"refresh": refresh_token})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_should_return_200_when_refresh_token_is_already_blacklisted(self, api_client, active_user):
        access_token, refresh_token = get_tokens(api_client, active_user)

        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        api_client.post("/api/v1/auth/logout/", {"refresh": refresh_token})

        response = api_client.post("/api/v1/auth/logout/", {"refresh": refresh_token})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

    def test_should_return_401_when_not_authenticated(self, api_client, active_user):
        _, refresh_token = get_tokens(api_client, active_user)

        response = api_client.post("/api/v1/auth/logout/", {"refresh": refresh_token})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_should_return_400_when_refresh_field_is_missing(self, authenticated_client):
        response = authenticated_client.post("/api/v1/auth/logout/", {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_should_return_200_when_refresh_token_is_invalid(self, authenticated_client):
        response = authenticated_client.post("/api/v1/auth/logout/", {"refresh": "invalid-token"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["message"] == "Logged out successfully"
