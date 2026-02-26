from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status

from app.models import ApiKey

URL = "/api/v1/api-keys/"


@pytest.mark.django_db
class TestCreateApiKey:
    def test_should_return_201_with_api_key_data(self, authenticated_client):
        response = authenticated_client.post(URL, {"name": "My Key"})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert response.data["data"]["name"] == "My Key"
        assert "id" in response.data["data"]
        assert "prefix" in response.data["data"]
        assert "created_at" in response.data["data"]

    def test_should_return_raw_key_only_on_creation(self, authenticated_client):
        response = authenticated_client.post(URL, {"name": "My Key"})

        assert "key" in response.data["data"]
        assert len(response.data["data"]["key"]) == ApiKey.KEY_LENGTH * 2

    def test_should_hash_key_before_storing(self, authenticated_client):
        response = authenticated_client.post(URL, {"name": "My Key"})

        raw_key = response.data["data"]["key"]
        expected_hash = ApiKey.hash_key(raw_key)
        api_key = ApiKey.objects.get(id=response.data["data"]["id"])

        assert api_key.key_hash == expected_hash

    def test_should_set_prefix_from_first_8_chars_of_raw_key(self, authenticated_client):
        response = authenticated_client.post(URL, {"name": "My Key"})

        raw_key = response.data["data"]["key"]
        prefix = response.data["data"]["prefix"]

        assert prefix == raw_key[: ApiKey.PREFIX_LENGTH]

    def test_should_create_with_empty_allowed_ips_by_default(self, authenticated_client):
        response = authenticated_client.post(URL, {"name": "My Key"})

        assert response.data["data"]["allowed_ips"] == []

    def test_should_create_with_valid_allowed_ips(self, authenticated_client):
        payload = {"name": "My Key", "allowed_ips": ["192.168.1.1", "10.0.0.1"]}

        response = authenticated_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["data"]["allowed_ips"] == ["192.168.1.1", "10.0.0.1"]

    def test_should_create_with_expires_at_in_the_future(self, authenticated_client):
        future = (timezone.now() + timedelta(days=30)).isoformat()
        payload = {"name": "My Key", "expires_at": future}

        response = authenticated_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["data"]["expires_at"] is not None

    def test_should_create_without_expires_at_by_default(self, authenticated_client):
        response = authenticated_client.post(URL, {"name": "My Key"})

        assert response.data["data"]["expires_at"] is None

    def test_should_include_user_fields_when_requester_is_root(self, root_client, active_user):
        ApiKey.objects.create(
            user=active_user,
            name="Other Key",
            key_hash="a" * 64,
            prefix="a" * 8,
        )

        response = root_client.post(URL, {"name": "Root Key"})

        assert "user_id" in response.data["data"]
        assert "user_email" in response.data["data"]

    def test_should_not_include_user_fields_for_regular_user(self, authenticated_client):
        response = authenticated_client.post(URL, {"name": "My Key"})

        assert "user_id" not in response.data["data"]
        assert "user_email" not in response.data["data"]

    def test_should_return_401_when_unauthenticated(self, api_client):
        response = api_client.post(URL, {"name": "My Key"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_should_return_400_when_name_is_missing(self, authenticated_client):
        response = authenticated_client.post(URL, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
        assert "name" in response.data["data"]["errors"]

    def test_should_return_400_when_name_exceeds_100_characters(self, authenticated_client):
        response = authenticated_client.post(URL, {"name": "x" * 101})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
        assert "name" in response.data["data"]["errors"]

    def test_should_return_400_when_allowed_ips_contains_invalid_ip(self, authenticated_client):
        payload = {"name": "My Key", "allowed_ips": ["not-an-ip"]}

        response = authenticated_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_should_return_400_when_allowed_ips_exceeds_20_items(self, authenticated_client):
        payload = {"name": "My Key", "allowed_ips": [f"10.0.0.{i}" for i in range(21)]}

        response = authenticated_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_should_return_400_when_expires_at_is_in_the_past(self, authenticated_client):
        past = (timezone.now() - timedelta(days=1)).isoformat()
        payload = {"name": "My Key", "expires_at": past}

        response = authenticated_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
