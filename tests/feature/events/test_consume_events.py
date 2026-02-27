from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status

from app.collections.event import Event
from app.enums import EventStatus
from tests.feature.events.conftest import create_event


def consume_url(account_id):
    return f"/api/v1/account/{account_id}/events/consume/"


@pytest.mark.django_db
class TestConsumeEvents:
    def test_should_return_200_with_consumed_events(self, platform_client, platform_account, platform_user):
        create_event(platform_account.id, platform_user.pk)

        response = platform_client.post(consume_url(platform_account.id))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert len(response.data["data"]) == 1
        assert response.data["meta"]["count"] == 1

    def test_should_update_event_status_to_delivered(self, platform_client, platform_account, platform_user):
        create_event(platform_account.id, platform_user.pk)

        platform_client.post(consume_url(platform_account.id))

        event = Event.find_one({"account_id": platform_account.id})
        assert event["status"] == EventStatus.DELIVERED
        assert event["consumer_id"] == str(platform_user.pk)
        assert event["delivered_at"] is not None
        assert event["attempts"] == 1

    def test_should_return_events_ordered_by_created_at_ascending(
        self, platform_client, platform_account, platform_user
    ):
        now = timezone.now()
        create_event(
            platform_account.id,
            platform_user.pk,
            key="get.order",
            payload={"id": 1},
            created_at=now + timedelta(seconds=2),
        )
        create_event(platform_account.id, platform_user.pk, key="delete.order", payload={"id": 2}, created_at=now)

        response = platform_client.post(consume_url(platform_account.id))

        assert response.data["data"][0]["key"] == "delete.order"
        assert response.data["data"][1]["key"] == "get.order"

    def test_should_respect_limit_parameter(self, platform_client, platform_account, platform_user):
        for _ in range(5):
            create_event(platform_account.id, platform_user.pk)

        response = platform_client.post(f"{consume_url(platform_account.id)}?limit=2")

        assert len(response.data["data"]) == 2
        assert response.data["meta"]["count"] == 2

    def test_should_filter_by_single_key(self, platform_client, platform_account, platform_user):
        create_event(
            platform_account.id,
            platform_user.pk,
            key="post.order",
            payload={"symbol": "BTCUSDT", "strategy": 1, "type": "buy", "volume": 0.5},
        )
        create_event(platform_account.id, platform_user.pk, key="get.account.info", payload={})

        response = platform_client.post(f"{consume_url(platform_account.id)}?key=get.account.info")

        assert len(response.data["data"]) == 1
        assert response.data["data"][0]["key"] == "get.account.info"

    def test_should_filter_by_multiple_comma_separated_keys(self, platform_client, platform_account, platform_user):
        create_event(
            platform_account.id,
            platform_user.pk,
            key="post.order",
            payload={"symbol": "BTCUSDT", "strategy": 1, "type": "buy", "volume": 0.5},
        )
        create_event(platform_account.id, platform_user.pk, key="get.account.info", payload={})
        create_event(platform_account.id, platform_user.pk, key="get.ticker", payload={})

        response = platform_client.post(f"{consume_url(platform_account.id)}?key=get.account.info,get.ticker")

        assert len(response.data["data"]) == 2
        keys = {event["key"] for event in response.data["data"]}
        assert keys == {"get.account.info", "get.ticker"}

    def test_should_not_consume_already_delivered_events(self, platform_client, platform_account, platform_user):
        create_event(platform_account.id, platform_user.pk, status=EventStatus.DELIVERED)

        response = platform_client.post(consume_url(platform_account.id))

        assert len(response.data["data"]) == 0
        assert response.data["meta"]["count"] == 0

    def test_should_return_empty_list_when_no_pending_events(self, platform_client, platform_account):
        response = platform_client.post(consume_url(platform_account.id))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"] == []
        assert response.data["meta"]["count"] == 0

    def test_should_return_400_when_account_does_not_exist(self, root_client):
        response = root_client.post(consume_url(999999999))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_return_400_when_key_is_invalid(self, platform_client, platform_account):
        response = platform_client.post(f"{consume_url(platform_account.id)}?key=invalid.key")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_return_401_when_unauthenticated(self, api_client, platform_account):
        response = api_client.post(consume_url(platform_account.id))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_should_return_403_when_user_is_not_account_owner(self, authenticated_client, platform_account):
        response = authenticated_client.post(consume_url(platform_account.id))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_return_403_when_account_owner_has_producer_role(self, producer_client, producer_account):
        response = producer_client.post(consume_url(producer_account.id))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_allow_root_user_to_consume(self, root_client, platform_account, platform_user):
        create_event(platform_account.id, platform_user.pk)

        response = root_client.post(consume_url(platform_account.id))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1
