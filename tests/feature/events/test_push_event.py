import pytest
from rest_framework import status

from app.collections.event import Event
from app.enums import EventStatus


def push_url(account_id):
    return f"/api/v1/account/{account_id}/events/"


VALID_PAYLOAD = {
    "key": "post.order",
    "payload": {
        "symbol": "BTCUSDT",
        "strategy": 1,
        "type": "buy",
        "volume": 0.5,
    },
}


@pytest.mark.django_db
class TestPushEvent:
    def test_should_return_201_with_event_data(self, producer_client, producer_account):
        response = producer_client.post(push_url(producer_account.id), VALID_PAYLOAD, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        data = response.data["data"]
        assert "id" in data
        assert data["account_id"] == str(producer_account.id)
        assert data["key"] == "post.order"
        assert data["status"] == EventStatus.PENDING

    def test_should_create_event_in_database(self, producer_client, producer_account, producer_user):
        producer_client.post(push_url(producer_account.id), VALID_PAYLOAD, format="json")

        assert Event.count({"account_id": producer_account.id}) == 1
        event = Event.find_one({"account_id": producer_account.id})
        assert event["user_id"] == str(producer_user.pk)
        assert event["status"] == EventStatus.PENDING
        assert event["consumer_id"] is None
        assert event["response"] is None
        assert event["attempts"] == 0

    def test_should_return_all_resource_fields(self, producer_client, producer_account):
        response = producer_client.post(push_url(producer_account.id), VALID_PAYLOAD, format="json")

        data = response.data["data"]
        expected_fields = {
            "id",
            "consumer_id",
            "account_id",
            "user_id",
            "key",
            "payload",
            "response",
            "status",
            "delivered_at",
            "processed_at",
            "attempts",
            "created_at",
            "updated_at",
        }
        assert set(data.keys()) == expected_fields

    def test_should_validate_payload_against_key_schema(self, producer_client, producer_account):
        payload = {
            "key": "post.order",
            "payload": {"symbol": "BTCUSDT"},
        }

        response = producer_client.post(push_url(producer_account.id), payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_accept_event_key_with_empty_schema(self, producer_client, producer_account):
        payload = {"key": "get.account.info", "payload": {}}

        response = producer_client.post(push_url(producer_account.id), payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED

    def test_should_return_400_when_key_is_missing(self, producer_client, producer_account):
        payload = {"payload": {"symbol": "BTCUSDT"}}

        response = producer_client.post(push_url(producer_account.id), payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_should_return_400_when_key_is_invalid(self, producer_client, producer_account):
        payload = {"key": "invalid.key", "payload": {}}

        response = producer_client.post(push_url(producer_account.id), payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_return_400_when_payload_is_missing(self, producer_client, producer_account):
        payload = {"key": "post.order"}

        response = producer_client.post(push_url(producer_account.id), payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_return_400_when_account_does_not_exist(self, root_client):
        response = root_client.post(push_url(999999999), VALID_PAYLOAD, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_return_401_when_unauthenticated(self, api_client, producer_account):
        response = api_client.post(push_url(producer_account.id), VALID_PAYLOAD, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_should_return_403_when_user_is_not_account_owner(self, authenticated_client, producer_account):
        response = authenticated_client.post(push_url(producer_account.id), VALID_PAYLOAD, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_return_403_when_account_owner_has_platform_role(self, platform_client, platform_account):
        response = platform_client.post(push_url(platform_account.id), VALID_PAYLOAD, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_allow_root_user_to_push(self, root_client, producer_account):
        response = root_client.post(push_url(producer_account.id), VALID_PAYLOAD, format="json")

        assert response.status_code == status.HTTP_201_CREATED
