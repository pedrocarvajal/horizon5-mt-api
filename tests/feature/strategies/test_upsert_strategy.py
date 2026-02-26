import uuid

import pytest
from rest_framework import status

from app.models import Strategy

URL = "/api/v1/strategy/"

STRATEGY_ID = str(uuid.uuid4())

VALID_PAYLOAD = {
    "account_id": 123456,
    "id": STRATEGY_ID,
    "symbol": "BTCUSDT",
    "prefix": "BTC",
    "name": "BTC Scalper",
    "magic_number": 12345,
    "balance": "5000.00",
}


@pytest.mark.django_db
class TestUpsertStrategy:
    def test_should_return_201_when_creating_new_strategy(self, producer_client, producer_account):
        payload = {**VALID_PAYLOAD, "account_id": producer_account.id}

        response = producer_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert response.data["data"]["id"] == STRATEGY_ID

    def test_should_return_200_when_updating_existing_strategy(self, producer_client, producer_account):
        payload = {**VALID_PAYLOAD, "account_id": producer_account.id}
        producer_client.post(URL, payload, format="json")

        updated_payload = {**payload, "name": "Updated Scalper"}
        response = producer_client.post(URL, updated_payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

    def test_should_create_strategy_in_database(self, producer_client, producer_account):
        payload = {**VALID_PAYLOAD, "account_id": producer_account.id}

        producer_client.post(URL, payload, format="json")

        strategy = Strategy.objects.get(id=STRATEGY_ID)
        assert strategy.account_id == producer_account.id
        assert strategy.symbol == "BTCUSDT"
        assert strategy.name == "BTC Scalper"
        assert strategy.magic_number == 12345

    def test_should_return_403_when_account_not_owned(self, producer_client, platform_account):
        payload = {**VALID_PAYLOAD, "account_id": platform_account.id}

        response = producer_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_return_400_when_required_fields_missing(self, producer_client, producer_account):
        payload = {"account_id": producer_account.id}

        response = producer_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_should_return_401_when_unauthenticated(self, api_client):
        response = api_client.post(URL, VALID_PAYLOAD, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_should_return_403_when_user_has_platform_role(self, platform_client, platform_account):
        payload = {**VALID_PAYLOAD, "account_id": platform_account.id}

        response = platform_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_allow_root_user_to_create(self, root_client, root_account):
        payload = {**VALID_PAYLOAD, "account_id": root_account.id}

        response = root_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
