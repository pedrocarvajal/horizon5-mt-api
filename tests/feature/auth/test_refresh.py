import pytest
from rest_framework import status

from tests.feature.conftest import TEST_PASSWORD


def get_refresh_token(api_client, login_url, user):
    response = api_client.post(login_url, {"email": user.email, "password": TEST_PASSWORD})
    return response.data["data"]["refresh"]


@pytest.mark.django_db
class TestRefresh:
    def test_should_return_200_with_new_token_pair(self, api_client, login_url, active_user):
        refresh_token = get_refresh_token(api_client, login_url, active_user)

        response = api_client.post("/api/v1/auth/refresh/", {"refresh": refresh_token})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert "access" in response.data["data"]
        assert "refresh" in response.data["data"]
        assert "expires_at" in response.data["data"]

    def test_should_return_new_access_token_as_valid_jwt(self, api_client, login_url, active_user):
        refresh_token = get_refresh_token(api_client, login_url, active_user)

        response = api_client.post("/api/v1/auth/refresh/", {"refresh": refresh_token})

        parts = response.data["data"]["access"].split(".")
        assert len(parts) == 3

    def test_should_return_rotated_refresh_token(self, api_client, login_url, active_user):
        refresh_token = get_refresh_token(api_client, login_url, active_user)

        response = api_client.post("/api/v1/auth/refresh/", {"refresh": refresh_token})

        assert response.data["data"]["refresh"] != refresh_token

    def test_should_return_expires_at_as_integer(self, api_client, login_url, active_user):
        refresh_token = get_refresh_token(api_client, login_url, active_user)

        response = api_client.post("/api/v1/auth/refresh/", {"refresh": refresh_token})

        assert isinstance(response.data["data"]["expires_at"], int)
        assert response.data["data"]["expires_at"] > 0

    def test_should_blacklist_old_refresh_token_after_rotation(self, api_client, login_url, active_user):
        refresh_token = get_refresh_token(api_client, login_url, active_user)

        api_client.post("/api/v1/auth/refresh/", {"refresh": refresh_token})

        response = api_client.post("/api/v1/auth/refresh/", {"refresh": refresh_token})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False
        assert response.data["message"] == "Token is invalid or expired"

    def test_should_return_401_when_refresh_token_is_invalid(self, api_client):
        response = api_client.post("/api/v1/auth/refresh/", {"refresh": "invalid-token"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False
        assert response.data["message"] == "Token is invalid or expired"

    def test_should_return_400_when_refresh_field_is_missing(self, api_client):
        response = api_client.post("/api/v1/auth/refresh/", {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_should_allow_chained_refresh(self, api_client, login_url, active_user):
        refresh_token = get_refresh_token(api_client, login_url, active_user)

        first_response = api_client.post("/api/v1/auth/refresh/", {"refresh": refresh_token})
        new_refresh = first_response.data["data"]["refresh"]

        second_response = api_client.post("/api/v1/auth/refresh/", {"refresh": new_refresh})

        assert second_response.status_code == status.HTTP_200_OK
        assert second_response.data["success"] is True

    def test_should_return_429_when_rate_limit_exceeded(self, api_client, login_url, active_user):
        refresh_token = get_refresh_token(api_client, login_url, active_user)

        for _ in range(10):
            response = api_client.post("/api/v1/auth/refresh/", {"refresh": "invalid-token"})
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                break

        response = api_client.post("/api/v1/auth/refresh/", {"refresh": refresh_token})

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert response.data["success"] is False
