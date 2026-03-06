import pytest
from rest_framework import status

from app.enums import AccountStatus
from app.models import Account

URL = "/api/v1/account/{id}/"


@pytest.mark.django_db
class TestUpdateAccount:
    def test_should_return_200_when_updating_status(self, producer_client, producer_account):
        response = producer_client.patch(
            URL.format(id=producer_account.id),
            {"status": AccountStatus.INACTIVE},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["id"] == producer_account.id

    def test_should_persist_status_change_in_database(self, producer_client, producer_account):
        producer_client.patch(
            URL.format(id=producer_account.id),
            {"status": AccountStatus.INACTIVE},
            format="json",
        )

        producer_account.refresh_from_db()
        assert producer_account.status == AccountStatus.INACTIVE

    def test_should_return_200_when_updating_multiple_fields(self, producer_client, producer_account):
        response = producer_client.patch(
            URL.format(id=producer_account.id),
            {"status": AccountStatus.INACTIVE, "broker": "NewBroker"},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

    def test_should_persist_multiple_field_changes_in_database(self, producer_client, producer_account):
        producer_client.patch(
            URL.format(id=producer_account.id),
            {"status": AccountStatus.INACTIVE, "broker": "NewBroker"},
            format="json",
        )

        producer_account.refresh_from_db()
        assert producer_account.status == AccountStatus.INACTIVE
        assert producer_account.broker == "NewBroker"

    def test_should_return_200_when_root_updates_any_account(self, root_client, producer_account):
        response = root_client.patch(
            URL.format(id=producer_account.id),
            {"status": AccountStatus.INACTIVE},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

    def test_should_return_200_when_platform_updates_any_account(self, platform_client, producer_account):
        response = platform_client.patch(
            URL.format(id=producer_account.id),
            {"status": AccountStatus.INACTIVE},
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

    def test_should_return_403_when_producer_updates_account_they_do_not_own(self, producer_client, platform_account):
        response = producer_client.patch(
            URL.format(id=platform_account.id),
            {"status": AccountStatus.INACTIVE},
            format="json",
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_return_404_when_account_does_not_exist(self, producer_client):
        response = producer_client.patch(
            URL.format(id=999999999),
            {"status": AccountStatus.INACTIVE},
            format="json",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_should_return_400_when_no_fields_are_provided(self, producer_client, producer_account):
        response = producer_client.patch(
            URL.format(id=producer_account.id),
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_should_return_400_when_status_value_is_invalid(self, producer_client, producer_account):
        response = producer_client.patch(
            URL.format(id=producer_account.id),
            {"status": "unknown"},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_should_return_401_when_unauthenticated(self, api_client, producer_account):
        response = api_client.patch(
            URL.format(id=producer_account.id),
            {"status": AccountStatus.INACTIVE},
            format="json",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_should_default_status_to_active_on_new_accounts(self, producer_client, producer_user):
        account = Account.objects.create(id=555555, user=producer_user)

        assert account.status == AccountStatus.ACTIVE
