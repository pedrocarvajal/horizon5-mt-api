import uuid

import pytest
from rest_framework import status

from app.models import Strategy

URL = "/api/v1/strategies/"


def create_strategy(account, **kwargs):
    defaults = {
        "id": uuid.uuid4(),
        "symbol": "BTCUSDT",
        "prefix": "BTC",
        "name": "BTC Scalper",
        "magic_number": 12345,
        "balance": "5000.00",
    }
    defaults.update(kwargs)
    return Strategy.objects.create(account=account, **defaults)


@pytest.mark.django_db
class TestListStrategies:
    def test_should_return_200_with_empty_list_when_no_strategies_exist(self, root_client):
        response = root_client.get(URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"] == []
        assert response.data["meta"]["count"] == 0

    def test_should_return_200_with_all_strategies_for_root(self, root_client, root_account, producer_account):
        create_strategy(root_account, name="Root Strategy")
        create_strategy(producer_account, name="Producer Strategy")

        response = root_client.get(URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        names = {strategy["name"] for strategy in response.data["data"]}
        assert names == {"Root Strategy", "Producer Strategy"}

    def test_should_return_correct_strategy_fields(self, root_client, root_account):
        create_strategy(
            root_account, symbol="ETHUSDT", prefix="ETH", name="ETH Scalper", magic_number=99999, balance="1500.00"
        )

        response = root_client.get(URL)

        strategy_data = response.data["data"][0]
        assert "id" in strategy_data
        assert strategy_data["account_id"] == root_account.id
        assert strategy_data["symbol"] == "ETHUSDT"
        assert strategy_data["prefix"] == "ETH"
        assert strategy_data["name"] == "ETH Scalper"
        assert strategy_data["magic_number"] == 99999
        assert strategy_data["balance"] == "1500.00"
        assert "created_at" in strategy_data
        assert "updated_at" in strategy_data

    def test_should_return_meta_with_correct_count(self, root_client, root_account):
        create_strategy(root_account, name="Strategy One", magic_number=1)
        create_strategy(root_account, name="Strategy Two", magic_number=2)
        create_strategy(root_account, name="Strategy Three", magic_number=3)

        response = root_client.get(URL)

        assert response.data["meta"]["count"] == 3

    def test_should_return_403_when_user_has_producer_role(self, producer_client):
        response = producer_client.get(URL)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_return_403_when_user_has_platform_role(self, platform_client):
        response = platform_client.get(URL)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_return_401_when_unauthenticated(self, api_client):
        response = api_client.get(URL)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False
