import uuid

import pytest
from rest_framework import status

from app.enums import EventStatus
from tests.feature.events.conftest import create_event, fake_object_id


def response_url(account_id, event_id):
    return f"/api/v1/account/{account_id}/event/{event_id}/response/"


@pytest.mark.django_db
class TestEventResponse:
    def test_should_return_200_with_response_data(self, producer_client, producer_account, producer_user):
        event = create_event(
            producer_account.id,
            producer_user.pk,
            status=EventStatus.PROCESSED,
            response={"result": "success", "order_id": 12345},
        )

        response = producer_client.get(response_url(producer_account.id, event["_id"]))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["response"] == {"result": "success", "order_id": 12345}

    def test_should_return_404_when_event_does_not_exist(self, producer_client, producer_account):
        response = producer_client.get(response_url(producer_account.id, fake_object_id()))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_should_return_404_when_event_has_no_response(self, producer_client, producer_account, producer_user):
        event = create_event(
            producer_account.id,
            producer_user.pk,
            status=EventStatus.PENDING,
            response=None,
        )

        response = producer_client.get(response_url(producer_account.id, event["_id"]))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_should_return_400_when_account_does_not_exist(self, root_client):
        response = root_client.get(response_url(uuid.uuid4(), fake_object_id()))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_return_400_when_event_id_is_invalid(self, producer_client, producer_account):
        response = producer_client.get(response_url(producer_account.id, "invalid-id"))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_return_401_when_unauthenticated(self, api_client, producer_account):
        response = api_client.get(response_url(producer_account.id, fake_object_id()))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_should_return_403_when_user_is_not_account_owner(self, authenticated_client, producer_account):
        response = authenticated_client.get(response_url(producer_account.id, fake_object_id()))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_return_403_when_account_owner_has_platform_role(self, platform_client, platform_account):
        response = platform_client.get(response_url(platform_account.id, fake_object_id()))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_allow_root_user_to_read_response(self, root_client, producer_account, producer_user):
        event = create_event(
            producer_account.id,
            producer_user.pk,
            status=EventStatus.PROCESSED,
            response={"result": "done"},
        )

        response = root_client.get(response_url(producer_account.id, event["_id"]))

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["response"] == {"result": "done"}
