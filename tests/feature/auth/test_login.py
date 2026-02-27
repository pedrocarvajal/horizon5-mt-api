import pytest
from django.core.cache import cache
from rest_framework import status

from tests.feature.conftest import TEST_PASSWORD


@pytest.mark.django_db
class TestLogin:
    def test_should_return_200_with_access_token(self, api_client, login_url, active_user):
        response = api_client.post(login_url, {"email": active_user.email, "password": TEST_PASSWORD})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert "access" in response.data["data"]
        assert "refresh" in response.data["data"]
        assert "expires_at" in response.data["data"]

    def test_should_return_valid_jwt_access_token(self, api_client, login_url, active_user):
        response = api_client.post(login_url, {"email": active_user.email, "password": TEST_PASSWORD})

        token = response.data["data"]["access"]
        parts = token.split(".")
        assert len(parts) == 3

    def test_should_return_valid_jwt_refresh_token(self, api_client, login_url, active_user):
        response = api_client.post(login_url, {"email": active_user.email, "password": TEST_PASSWORD})

        token = response.data["data"]["refresh"]
        parts = token.split(".")
        assert len(parts) == 3

    def test_should_return_expires_at_as_integer(self, api_client, login_url, active_user):
        response = api_client.post(login_url, {"email": active_user.email, "password": TEST_PASSWORD})

        assert isinstance(response.data["data"]["expires_at"], int)
        assert response.data["data"]["expires_at"] > 0

    def test_should_return_401_when_email_does_not_exist(self, api_client, login_url):
        response = api_client.post(login_url, {"email": "unknown@test.co", "password": TEST_PASSWORD})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False
        assert response.data["message"] == "Invalid credentials."

    def test_should_return_401_when_password_is_incorrect(self, api_client, login_url, active_user):
        response = api_client.post(login_url, {"email": active_user.email, "password": "wrongpassword123"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False
        assert response.data["message"] == "Invalid credentials."

    def test_should_return_401_when_account_is_inactive(self, api_client, login_url, inactive_user):
        response = api_client.post(login_url, {"email": inactive_user.email, "password": TEST_PASSWORD})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_should_return_400_when_email_is_missing(self, api_client, login_url):
        response = api_client.post(login_url, {"password": TEST_PASSWORD})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
        assert response.data["message"] == "Validation failed."
        assert "non_field_errors" in response.data["data"]["errors"]

    def test_should_return_400_when_password_is_missing(self, api_client, login_url):
        response = api_client.post(login_url, {"email": "user@test.co"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
        assert response.data["message"] == "Validation failed."
        assert "non_field_errors" in response.data["data"]["errors"]

    def test_should_return_400_when_email_format_is_invalid(self, api_client, login_url):
        response = api_client.post(login_url, {"email": "not-an-email", "password": TEST_PASSWORD})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
        assert "email" in response.data["data"]["errors"]

    def test_should_return_400_when_password_is_shorter_than_8_characters(self, api_client, login_url):
        response = api_client.post(login_url, {"email": "user@test.co", "password": "short"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
        assert "password" in response.data["data"]["errors"]

    def test_should_return_400_when_body_is_empty(self, api_client, login_url):
        response = api_client.post(login_url, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
        assert response.data["message"] == "Validation failed."

    def test_should_return_429_when_ip_rate_limit_exceeded(self, api_client, login_url, active_user):
        for _ in range(5):
            api_client.post(login_url, {"email": active_user.email, "password": TEST_PASSWORD})

        response = api_client.post(login_url, {"email": active_user.email, "password": TEST_PASSWORD})

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert response.data["success"] is False
        assert response.data["message"] == "Request was throttled."

    def test_should_return_429_when_account_is_locked_after_failed_attempts(self, api_client, login_url, active_user):
        for i in range(10):
            api_client.post(
                login_url,
                {"email": active_user.email, "password": "wrongpassword123"},
                REMOTE_ADDR=f"10.0.0.{i % 5}",
            )

        response = api_client.post(
            login_url,
            {"email": active_user.email, "password": TEST_PASSWORD},
            REMOTE_ADDR="10.0.1.0",
        )

        assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert response.data["success"] is False

    def test_should_clear_failed_attempts_after_successful_login(self, api_client, login_url, active_user):
        for i in range(3):
            api_client.post(
                login_url,
                {"email": active_user.email, "password": "wrongpassword123"},
                REMOTE_ADDR=f"10.0.0.{i}",
            )

        attempts_key = f"login_attempts:{active_user.email}"
        assert cache.get(attempts_key) == 3

        api_client.post(
            login_url,
            {"email": active_user.email, "password": TEST_PASSWORD},
            REMOTE_ADDR="10.0.1.0",
        )

        assert cache.get(attempts_key) is None
