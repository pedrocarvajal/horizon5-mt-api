import pytest
from rest_framework import status

from app.collections.event import Event
from app.enums import EventStatus
from tests.feature.events.conftest import create_event, fake_object_id


def ack_url(account_id, event_id):
    return f"/api/v1/account/{account_id}/event/{event_id}/ack/"


@pytest.mark.django_db
class TestAckEvent:
    def test_should_return_200_with_updated_event(self, platform_client, platform_account, platform_user):
        event = create_event(platform_account.id, platform_user.pk, status=EventStatus.DELIVERED)

        response = platform_client.patch(ack_url(platform_account.id, event["_id"]), format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["status"] == EventStatus.PROCESSED

    def test_should_set_processed_at_timestamp(self, platform_client, platform_account, platform_user):
        event = create_event(platform_account.id, platform_user.pk, status=EventStatus.DELIVERED)

        platform_client.patch(ack_url(platform_account.id, event["_id"]), format="json")

        updated = Event.find_one({"_id": event["_id"]})
        assert updated["status"] == EventStatus.PROCESSED
        assert updated["processed_at"] is not None

    def test_should_accept_optional_response_data(self, platform_client, platform_account, platform_user):
        event = create_event(platform_account.id, platform_user.pk, status=EventStatus.DELIVERED)
        response_payload = {"result": "success", "order_id": 12345}

        response = platform_client.patch(
            ack_url(platform_account.id, event["_id"]),
            {"response": response_payload},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        updated = Event.find_one({"_id": event["_id"]})
        assert updated["response"] == response_payload

    def test_should_not_overwrite_response_when_not_provided(self, platform_client, platform_account, platform_user):
        event = create_event(platform_account.id, platform_user.pk, status=EventStatus.DELIVERED)

        platform_client.patch(ack_url(platform_account.id, event["_id"]), format="json")

        updated = Event.find_one({"_id": event["_id"]})
        assert updated["response"] is None

    def test_should_return_404_when_event_does_not_exist(self, platform_client, platform_account):
        response = platform_client.patch(ack_url(platform_account.id, fake_object_id()), format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_should_return_404_when_event_is_not_in_delivered_status(
        self, platform_client, platform_account, platform_user
    ):
        event = create_event(platform_account.id, platform_user.pk, status=EventStatus.PENDING)

        response = platform_client.patch(ack_url(platform_account.id, event["_id"]), format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_should_return_400_when_event_id_is_invalid(self, platform_client, platform_account):
        response = platform_client.patch(ack_url(platform_account.id, "invalid-id"), format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_return_401_when_unauthenticated(self, api_client, platform_account):
        response = api_client.patch(ack_url(platform_account.id, fake_object_id()), format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_should_return_403_when_user_is_not_account_owner(self, authenticated_client, platform_account):
        response = authenticated_client.patch(ack_url(platform_account.id, fake_object_id()), format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_return_403_when_account_owner_has_producer_role(self, producer_client, producer_account):
        response = producer_client.patch(ack_url(producer_account.id, fake_object_id()), format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_allow_root_user_to_ack(self, root_client, platform_account, platform_user):
        event = create_event(platform_account.id, platform_user.pk, status=EventStatus.DELIVERED)

        response = root_client.patch(ack_url(platform_account.id, event["_id"]), format="json")

        assert response.status_code == status.HTTP_200_OK
