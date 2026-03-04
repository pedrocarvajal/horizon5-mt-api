import uuid

import pytest
from rest_framework import status

from app.collections.heartbeat import Heartbeat
from app.enums import HeartbeatEvent, HeartbeatSystem

URL = "/api/v1/heartbeat/"

VALID_PAYLOAD = {
    "account_id": 123456,
    "event": HeartbeatEvent.ON_INIT,
    "system": HeartbeatSystem.STRATEGY,
}


@pytest.mark.django_db
class TestStoreHeartbeat:
    def test_should_return_201_with_valid_data(self, platform_client, platform_account):
        payload = {**VALID_PAYLOAD, "account_id": platform_account.id}

        response = platform_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True

    def test_should_create_heartbeat_in_mongodb(self, platform_client, platform_account):
        payload = {**VALID_PAYLOAD, "account_id": platform_account.id}

        platform_client.post(URL, payload, format="json")

        assert Heartbeat.count({"account_id": platform_account.id}) == 1
        heartbeat = Heartbeat.find_one({"account_id": platform_account.id})
        assert heartbeat["event"] == HeartbeatEvent.ON_INIT
        assert heartbeat["system"] == HeartbeatSystem.STRATEGY

    def test_should_accept_optional_strategy_id(self, platform_client, platform_account):
        strategy_id = str(uuid.uuid4())
        payload = {**VALID_PAYLOAD, "account_id": platform_account.id, "strategy_id": strategy_id}

        response = platform_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        heartbeat = Heartbeat.find_one({"account_id": platform_account.id})
        assert heartbeat["strategy_id"] == strategy_id

    def test_should_return_403_when_account_not_owned(self, producer_client, platform_account):
        payload = {**VALID_PAYLOAD, "account_id": platform_account.id}

        response = producer_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_return_400_when_required_fields_missing(self, platform_client, platform_account):
        payload = {"account_id": platform_account.id}

        response = platform_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_should_return_400_when_event_is_invalid(self, platform_client, platform_account):
        payload = {**VALID_PAYLOAD, "account_id": platform_account.id, "event": "invalid_event"}

        response = platform_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_return_400_when_system_is_invalid(self, platform_client, platform_account):
        payload = {**VALID_PAYLOAD, "account_id": platform_account.id, "system": "invalid_system"}

        response = platform_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_return_401_when_unauthenticated(self, api_client):
        response = api_client.post(URL, VALID_PAYLOAD, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_should_return_403_when_user_has_producer_role(self, producer_client, producer_account):
        payload = {**VALID_PAYLOAD, "account_id": producer_account.id}

        response = producer_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
