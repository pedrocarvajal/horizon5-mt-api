import pytest
from rest_framework import status

from app.models import Account

URL = "/api/v1/account/"

VALID_PAYLOAD = {
    "account_id": 100001,
    "broker": "ICMarkets",
    "server": "ICMarketsSC-Demo",
    "currency": "USD",
    "leverage": 500,
    "balance": "10000.00",
    "equity": "10000.00",
    "margin": "0.00",
    "free_margin": "10000.00",
    "profit": "0.00",
    "margin_level": "0.00",
}


@pytest.mark.django_db
class TestUpsertAccount:
    def test_should_return_201_when_creating_new_account(self, producer_client):
        response = producer_client.post(URL, VALID_PAYLOAD, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert response.data["data"]["id"] == VALID_PAYLOAD["account_id"]

    def test_should_return_200_when_updating_existing_account(self, producer_client, producer_account):
        payload = {**VALID_PAYLOAD, "account_id": producer_account.id, "broker": "Updated Broker"}

        response = producer_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

    def test_should_create_account_in_database(self, producer_client, producer_user):
        producer_client.post(URL, VALID_PAYLOAD, format="json")

        account = Account.objects.get(id=VALID_PAYLOAD["account_id"])
        assert account.user_id == producer_user.pk
        assert account.broker == "ICMarkets"
        assert account.currency == "USD"
        assert account.leverage == 500

    def test_should_update_account_fields_in_database(self, producer_client, producer_account):
        payload = {**VALID_PAYLOAD, "account_id": producer_account.id, "broker": "NewBroker"}

        producer_client.post(URL, payload, format="json")

        producer_account.refresh_from_db()
        assert producer_account.broker == "NewBroker"

    def test_should_return_403_when_updating_account_not_owned(self, producer_client, platform_account):
        payload = {**VALID_PAYLOAD, "account_id": platform_account.id}

        response = producer_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_return_400_when_account_id_is_missing(self, producer_client):
        payload = {key: value for key, value in VALID_PAYLOAD.items() if key != "account_id"}

        response = producer_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_should_return_401_when_unauthenticated(self, api_client):
        response = api_client.post(URL, VALID_PAYLOAD, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_should_return_403_when_user_has_platform_role(self, platform_client):
        response = platform_client.post(URL, VALID_PAYLOAD, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_allow_root_user_to_create(self, root_client):
        response = root_client.post(URL, VALID_PAYLOAD, format="json")

        assert response.status_code == status.HTTP_201_CREATED
