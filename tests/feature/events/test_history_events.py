import uuid
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status

from app.enums import EventStatus
from tests.feature.events.conftest import create_event


def history_url(account_id):
    return f"/api/v1/account/{account_id}/events/history/"


@pytest.mark.django_db
class TestHistoryEvents:
    def test_should_return_200_with_event_history(self, producer_client, producer_account, producer_user):
        create_event(producer_account.id, producer_user.pk)

        response = producer_client.get(history_url(producer_account.id))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert len(response.data["data"]) == 1

    def test_should_return_events_ordered_by_created_at_descending(
        self, producer_client, producer_account, producer_user
    ):
        now = timezone.now()
        create_event(
            producer_account.id,
            producer_user.pk,
            key="get.order",
            payload={"id": 1},
            created_at=now - timedelta(seconds=2),
        )
        create_event(producer_account.id, producer_user.pk, key="delete.order", payload={"id": 2}, created_at=now)

        response = producer_client.get(history_url(producer_account.id))

        assert response.data["data"][0]["key"] == "delete.order"
        assert response.data["data"][1]["key"] == "get.order"

    def test_should_respect_limit_parameter(self, producer_client, producer_account, producer_user):
        for _ in range(5):
            create_event(producer_account.id, producer_user.pk)

        response = producer_client.get(f"{history_url(producer_account.id)}?limit=2")

        assert len(response.data["data"]) == 2

    def test_should_filter_by_status(self, producer_client, producer_account, producer_user):
        create_event(producer_account.id, producer_user.pk, status=EventStatus.PENDING)
        create_event(producer_account.id, producer_user.pk, status=EventStatus.DELIVERED)

        response = producer_client.get(f"{history_url(producer_account.id)}?status=delivered")

        assert len(response.data["data"]) == 1
        assert response.data["data"][0]["status"] == EventStatus.DELIVERED

    def test_should_filter_by_key(self, producer_client, producer_account, producer_user):
        create_event(
            producer_account.id,
            producer_user.pk,
            key="post.order",
            payload={"symbol": "BTCUSDT", "strategy": 1, "type": "buy", "volume": 0.5},
        )
        create_event(producer_account.id, producer_user.pk, key="get.account.info", payload={})

        response = producer_client.get(f"{history_url(producer_account.id)}?key=get.account.info")

        assert len(response.data["data"]) == 1
        assert response.data["data"][0]["key"] == "get.account.info"

    def test_should_return_empty_list_when_no_events(self, producer_client, producer_account):
        response = producer_client.get(history_url(producer_account.id))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"] == []

    def test_should_return_400_when_account_does_not_exist(self, root_client):
        response = root_client.get(history_url(uuid.uuid4()))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_return_401_when_unauthenticated(self, api_client, producer_account):
        response = api_client.get(history_url(producer_account.id))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_should_return_403_when_user_is_not_account_owner(self, authenticated_client, producer_account):
        response = authenticated_client.get(history_url(producer_account.id))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_allow_root_user_to_read_history(self, root_client, producer_account, producer_user):
        create_event(producer_account.id, producer_user.pk)

        response = root_client.get(history_url(producer_account.id))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1

    def test_should_allow_platform_user_to_read_own_history(self, platform_client, platform_account, platform_user):
        create_event(platform_account.id, platform_user.pk)

        response = platform_client.get(history_url(platform_account.id))

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1
