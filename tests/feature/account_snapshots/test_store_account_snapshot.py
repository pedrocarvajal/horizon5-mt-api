import pytest
from rest_framework import status

from app.collections.account_snapshot import AccountSnapshot

URL = "/api/v1/account-snapshot/"

VALID_PAYLOAD = {
    "account_id": 123456,
    "balance": "10000.00",
    "equity": "10500.00",
    "profit": "500.00",
    "margin_level": "1500.00",
    "open_positions": 3,
    "drawdown_pct": "2.5000",
    "daily_pnl": "150.00",
    "floating_pnl": "75.00",
    "open_order_count": 2,
    "exposure_lots": "0.3000",
}


@pytest.mark.django_db
class TestStoreAccountSnapshot:
    def test_should_return_201_with_valid_data(self, producer_client, producer_account):
        payload = {**VALID_PAYLOAD, "account_id": producer_account.id}

        response = producer_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True

    def test_should_create_snapshot_in_mongodb(self, producer_client, producer_account):
        payload = {**VALID_PAYLOAD, "account_id": producer_account.id}

        producer_client.post(URL, payload, format="json")

        assert AccountSnapshot.count({"account_id": producer_account.id}) == 1
        snapshot = AccountSnapshot.find_one({"account_id": producer_account.id})
        assert snapshot["account_id"] == producer_account.id
        assert snapshot["open_positions"] == 3

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

    def test_should_allow_root_user_to_store(self, root_client, root_account):
        payload = {**VALID_PAYLOAD, "account_id": root_account.id}

        response = root_client.post(URL, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
