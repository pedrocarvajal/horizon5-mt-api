import pytest
from rest_framework import status

from app.collections.account_snapshot import AccountSnapshot

URL = "/api/v1/account-snapshots/"

ACCOUNT_ID = 123456


def create_snapshot(account_id=ACCOUNT_ID, **kwargs):
    defaults = {
        "account_id": account_id,
        "balance": 10000.0,
        "equity": 10500.0,
        "profit": 500.0,
        "margin_level": 1500.0,
        "open_positions": 3,
        "drawdown_pct": 2.5,
        "daily_pnl": 150.0,
        "floating_pnl": 75.0,
        "open_order_count": 2,
        "exposure_lots": 0.3,
    }
    defaults.update(kwargs)
    return AccountSnapshot.create(defaults)


@pytest.mark.django_db
class TestListAccountSnapshots:
    def test_should_return_200_with_snapshots_for_account(self, root_client):
        create_snapshot()
        create_snapshot()

        response = root_client.get(URL, {"account_id": ACCOUNT_ID})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert len(response.data["data"]) == 2

    def test_should_return_200_with_empty_list_when_no_snapshots_exist(self, root_client):
        response = root_client.get(URL, {"account_id": ACCOUNT_ID})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"] == []
        assert response.data["meta"]["count"] == 0
        assert response.data["meta"]["pagination"]["total"] == 0

    def test_should_return_only_snapshots_for_requested_account(self, root_client):
        create_snapshot(account_id=ACCOUNT_ID)
        create_snapshot(account_id=999999)

        response = root_client.get(URL, {"account_id": ACCOUNT_ID})

        assert len(response.data["data"]) == 1
        assert response.data["data"][0]["account_id"] == ACCOUNT_ID

    def test_should_return_correct_snapshot_fields(self, root_client):
        create_snapshot(
            balance=20000.0,
            equity=21000.0,
            profit=1000.0,
            margin_level=3000.0,
            open_positions=5,
            drawdown_pct=1.5,
            daily_pnl=300.0,
            floating_pnl=150.0,
            open_order_count=4,
            exposure_lots=0.8,
        )

        response = root_client.get(URL, {"account_id": ACCOUNT_ID})

        snapshot = response.data["data"][0]
        assert "id" in snapshot
        assert snapshot["account_id"] == ACCOUNT_ID
        assert snapshot["balance"] == 20000.0
        assert snapshot["equity"] == 21000.0
        assert snapshot["profit"] == 1000.0
        assert snapshot["margin_level"] == 3000.0
        assert snapshot["open_positions"] == 5
        assert snapshot["drawdown_pct"] == 1.5
        assert snapshot["daily_pnl"] == 300.0
        assert snapshot["floating_pnl"] == 150.0
        assert snapshot["open_order_count"] == 4
        assert snapshot["exposure_lots"] == 0.8
        assert "created_at" in snapshot

    def test_should_return_snapshots_ordered_by_created_at_descending(self, root_client):
        create_snapshot(balance=100.0)
        create_snapshot(balance=200.0)
        create_snapshot(balance=300.0)

        response = root_client.get(URL, {"account_id": ACCOUNT_ID})

        balances = [snapshot["balance"] for snapshot in response.data["data"]]
        assert balances == [300.0, 200.0, 100.0]

    def test_should_respect_per_page_parameter(self, root_client):
        for i in range(5):
            create_snapshot(balance=float(i))

        response = root_client.get(URL, {"account_id": ACCOUNT_ID, "per_page": 2})

        assert len(response.data["data"]) == 2
        assert response.data["meta"]["pagination"]["total"] == 5
        assert response.data["meta"]["pagination"]["per_page"] == 2

    def test_should_respect_page_parameter(self, root_client):
        for i in range(5):
            create_snapshot(balance=float(i))

        response = root_client.get(URL, {"account_id": ACCOUNT_ID, "per_page": 2, "page": 2})

        assert len(response.data["data"]) == 2
        assert response.data["meta"]["pagination"]["page"] == 2

    def test_should_return_last_page_with_remaining_items(self, root_client):
        for i in range(5):
            create_snapshot(balance=float(i))

        response = root_client.get(URL, {"account_id": ACCOUNT_ID, "per_page": 2, "page": 3})

        assert len(response.data["data"]) == 1
        assert response.data["meta"]["pagination"]["total_pages"] == 3

    def test_should_return_meta_with_pagination_fields(self, root_client):
        create_snapshot()
        create_snapshot()
        create_snapshot()

        response = root_client.get(URL, {"account_id": ACCOUNT_ID})

        meta = response.data["meta"]
        assert meta["count"] == 3
        pagination = meta["pagination"]
        assert pagination["total"] == 3
        assert pagination["page"] == 1
        assert pagination["per_page"] == 50
        assert pagination["total_pages"] == 1

    def test_should_return_400_when_account_id_is_missing(self, root_client):
        response = root_client.get(URL)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_should_return_403_when_user_has_producer_role(self, producer_client):
        response = producer_client.get(URL, {"account_id": ACCOUNT_ID})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_return_403_when_user_has_platform_role(self, platform_client):
        response = platform_client.get(URL, {"account_id": ACCOUNT_ID})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_return_401_when_unauthenticated(self, api_client):
        response = api_client.get(URL, {"account_id": ACCOUNT_ID})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_should_order_by_balance_ascending(self, root_client):
        create_snapshot(balance=300.0)
        create_snapshot(balance=100.0)
        create_snapshot(balance=200.0)

        response = root_client.get(URL, {"account_id": ACCOUNT_ID, "order_by": "balance"})

        balances = [s["balance"] for s in response.data["data"]]
        assert balances == [100.0, 200.0, 300.0]

    def test_should_order_by_balance_descending(self, root_client):
        create_snapshot(balance=100.0)
        create_snapshot(balance=300.0)
        create_snapshot(balance=200.0)

        response = root_client.get(URL, {"account_id": ACCOUNT_ID, "order_by": "-balance"})

        balances = [s["balance"] for s in response.data["data"]]
        assert balances == [300.0, 200.0, 100.0]

    def test_should_use_default_order_by_created_at_descending(self, root_client):
        create_snapshot(balance=100.0)
        create_snapshot(balance=200.0)
        create_snapshot(balance=300.0)

        response = root_client.get(URL, {"account_id": ACCOUNT_ID})

        balances = [s["balance"] for s in response.data["data"]]
        assert balances == [300.0, 200.0, 100.0]

    def test_should_return_400_when_order_by_column_is_invalid(self, root_client):
        response = root_client.get(URL, {"account_id": ACCOUNT_ID, "order_by": "invalid_column"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_return_400_when_filter_by_column_is_invalid(self, root_client):
        response = root_client.get(URL, {"account_id": ACCOUNT_ID, "filter_by": "invalid", "filter_value": "100"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_include_filterable_and_orderable_columns_in_meta(self, root_client):
        response = root_client.get(URL, {"account_id": ACCOUNT_ID})

        meta = response.data["meta"]
        assert meta["filterable_columns"] == []
        assert meta["orderable_columns"] == ["balance", "equity", "profit", "drawdown_pct", "created_at"]
