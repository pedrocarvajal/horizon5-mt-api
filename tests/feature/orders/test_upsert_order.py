import uuid

import pytest
from rest_framework import status

from app.collections.order import Order
from app.enums import OrderStatus

URL = "/api/v1/order/"

ORDER_ID = str(uuid.uuid4())

VALID_PAYLOAD = {
    "id": ORDER_ID,
    "account_id": 123456,
    "symbol": "BTCUSDT",
    "side": "buy",
    "status": OrderStatus.OPEN,
    "volume": "0.1000",
}


@pytest.mark.django_db
class TestUpsertOrder:
    def test_should_return_201_when_creating_new_order(self, producer_client, producer_account):
        order_id = str(uuid.uuid4())
        payload = {**VALID_PAYLOAD, "id": order_id, "account_id": producer_account.id}

        response = producer_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert response.data["data"]["id"] == order_id

    def test_should_return_200_when_updating_existing_order(self, producer_client, producer_account):
        order_id = str(uuid.uuid4())
        payload = {**VALID_PAYLOAD, "id": order_id, "account_id": producer_account.id}
        producer_client.post(URL, payload, format="json")

        updated_payload = {**payload, "status": OrderStatus.CLOSED}
        response = producer_client.post(URL, updated_payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

    def test_should_create_order_in_mongodb(self, producer_client, producer_account):
        order_id = str(uuid.uuid4())
        payload = {**VALID_PAYLOAD, "id": order_id, "account_id": producer_account.id}

        producer_client.post(URL, payload, format="json")

        assert Order.count({"account_id": producer_account.id}) == 1
        order = Order.collection().find_one({"_id": order_id})
        assert order["symbol"] == "BTCUSDT"
        assert order["side"] == "buy"

    def test_should_return_403_when_account_not_owned(self, producer_client, platform_account):
        payload = {**VALID_PAYLOAD, "account_id": platform_account.id}

        response = producer_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_return_400_when_required_fields_missing(self, producer_client, producer_account):
        payload = {"account_id": producer_account.id}

        response = producer_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_should_return_400_when_status_is_invalid(self, producer_client, producer_account):
        payload = {**VALID_PAYLOAD, "account_id": producer_account.id, "status": "invalid_status"}

        response = producer_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_accept_optional_strategy_id(self, producer_client, producer_account):
        order_id = str(uuid.uuid4())
        strategy_id = str(uuid.uuid4())
        payload = {
            **VALID_PAYLOAD,
            "id": order_id,
            "account_id": producer_account.id,
            "strategy_id": strategy_id,
        }

        response = producer_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        order = Order.collection().find_one({"_id": order_id})
        assert order["strategy_id"] == strategy_id

    def test_should_return_401_when_unauthenticated(self, api_client):
        response = api_client.post(URL, VALID_PAYLOAD, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_should_return_403_when_user_has_platform_role(self, platform_client, platform_account):
        payload = {**VALID_PAYLOAD, "account_id": platform_account.id}

        response = platform_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN
