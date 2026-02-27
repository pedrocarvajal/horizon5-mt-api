import uuid

import pytest
from rest_framework import status

from app.collections.strategy_snapshot import StrategySnapshot

URL = "/api/v1/strategy-snapshots/"

STRATEGY_ID = str(uuid.uuid4())


def create_snapshot(strategy_id=STRATEGY_ID, account_id=123456, **kwargs):
    defaults = {
        "account_id": account_id,
        "strategy_id": strategy_id,
        "nav": 5000.0,
        "drawdown_pct": 1.25,
        "daily_pnl": 100.0,
        "floating_pnl": 50.0,
        "open_order_count": 1,
        "exposure_lots": 0.1,
    }
    defaults.update(kwargs)
    return StrategySnapshot.create(defaults)


@pytest.mark.django_db
class TestListStrategySnapshots:
    def test_should_return_200_with_snapshots_for_strategy(self, root_client):
        create_snapshot()
        create_snapshot()

        response = root_client.get(URL, {"strategy_id": STRATEGY_ID})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert len(response.data["data"]) == 2

    def test_should_return_200_with_empty_list_when_no_snapshots_exist(self, root_client):
        response = root_client.get(URL, {"strategy_id": STRATEGY_ID})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"] == []
        assert response.data["meta"]["count"] == 0
        assert response.data["meta"]["pagination"]["total"] == 0

    def test_should_return_only_snapshots_for_requested_strategy(self, root_client):
        other_strategy_id = str(uuid.uuid4())
        create_snapshot(strategy_id=STRATEGY_ID)
        create_snapshot(strategy_id=other_strategy_id)

        response = root_client.get(URL, {"strategy_id": STRATEGY_ID})

        assert len(response.data["data"]) == 1
        assert response.data["data"][0]["strategy_id"] == STRATEGY_ID

    def test_should_filter_by_account_id(self, root_client):
        create_snapshot(account_id=111)
        create_snapshot(account_id=222)

        response = root_client.get(URL, {"strategy_id": STRATEGY_ID, "account_id": 111})

        assert len(response.data["data"]) == 1
        assert response.data["data"][0]["account_id"] == 111

    def test_should_return_correct_snapshot_fields(self, root_client):
        create_snapshot(
            nav=8000.0, drawdown_pct=2.5, daily_pnl=200.0, floating_pnl=75.0, open_order_count=3, exposure_lots=0.5
        )

        response = root_client.get(URL, {"strategy_id": STRATEGY_ID})

        snapshot = response.data["data"][0]
        assert "id" in snapshot
        assert snapshot["account_id"] == 123456
        assert snapshot["strategy_id"] == STRATEGY_ID
        assert snapshot["nav"] == 8000.0
        assert snapshot["drawdown_pct"] == 2.5
        assert snapshot["daily_pnl"] == 200.0
        assert snapshot["floating_pnl"] == 75.0
        assert snapshot["open_order_count"] == 3
        assert snapshot["exposure_lots"] == 0.5
        assert "created_at" in snapshot

    def test_should_return_snapshots_ordered_by_created_at_descending(self, root_client):
        create_snapshot(nav=100.0)
        create_snapshot(nav=200.0)
        create_snapshot(nav=300.0)

        response = root_client.get(URL, {"strategy_id": STRATEGY_ID})

        navs = [snapshot["nav"] for snapshot in response.data["data"]]
        assert navs == [300.0, 200.0, 100.0]

    def test_should_respect_per_page_parameter(self, root_client):
        for i in range(5):
            create_snapshot(nav=float(i))

        response = root_client.get(URL, {"strategy_id": STRATEGY_ID, "per_page": 2})

        assert len(response.data["data"]) == 2
        assert response.data["meta"]["pagination"]["total"] == 5
        assert response.data["meta"]["pagination"]["per_page"] == 2

    def test_should_respect_page_parameter(self, root_client):
        for i in range(5):
            create_snapshot(nav=float(i))

        response = root_client.get(URL, {"strategy_id": STRATEGY_ID, "per_page": 2, "page": 2})

        assert len(response.data["data"]) == 2
        assert response.data["meta"]["pagination"]["page"] == 2

    def test_should_return_last_page_with_remaining_items(self, root_client):
        for i in range(5):
            create_snapshot(nav=float(i))

        response = root_client.get(URL, {"strategy_id": STRATEGY_ID, "per_page": 2, "page": 3})

        assert len(response.data["data"]) == 1
        assert response.data["meta"]["pagination"]["total_pages"] == 3

    def test_should_return_meta_with_pagination_fields(self, root_client):
        create_snapshot()
        create_snapshot()
        create_snapshot()

        response = root_client.get(URL, {"strategy_id": STRATEGY_ID})

        meta = response.data["meta"]
        assert meta["count"] == 3
        pagination = meta["pagination"]
        assert pagination["total"] == 3
        assert pagination["page"] == 1
        assert pagination["per_page"] == 50
        assert pagination["total_pages"] == 1

    def test_should_return_400_when_strategy_id_is_missing(self, root_client):
        response = root_client.get(URL)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_should_return_400_when_strategy_id_is_invalid(self, root_client):
        response = root_client.get(URL, {"strategy_id": "not-a-uuid"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_return_403_when_user_has_producer_role(self, producer_client):
        response = producer_client.get(URL, {"strategy_id": STRATEGY_ID})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_return_403_when_user_has_platform_role(self, platform_client):
        response = platform_client.get(URL, {"strategy_id": STRATEGY_ID})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_should_return_401_when_unauthenticated(self, api_client):
        response = api_client.get(URL, {"strategy_id": STRATEGY_ID})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_should_order_by_nav_ascending(self, root_client):
        create_snapshot(nav=300.0)
        create_snapshot(nav=100.0)
        create_snapshot(nav=200.0)

        response = root_client.get(URL, {"strategy_id": STRATEGY_ID, "order_by": "nav"})

        navs = [s["nav"] for s in response.data["data"]]
        assert navs == [100.0, 200.0, 300.0]

    def test_should_order_by_nav_descending(self, root_client):
        create_snapshot(nav=100.0)
        create_snapshot(nav=300.0)
        create_snapshot(nav=200.0)

        response = root_client.get(URL, {"strategy_id": STRATEGY_ID, "order_by": "-nav"})

        navs = [s["nav"] for s in response.data["data"]]
        assert navs == [300.0, 200.0, 100.0]

    def test_should_use_default_order_by_created_at_descending(self, root_client):
        create_snapshot(nav=100.0)
        create_snapshot(nav=200.0)
        create_snapshot(nav=300.0)

        response = root_client.get(URL, {"strategy_id": STRATEGY_ID})

        navs = [s["nav"] for s in response.data["data"]]
        assert navs == [300.0, 200.0, 100.0]

    def test_should_return_400_when_order_by_column_is_invalid(self, root_client):
        response = root_client.get(URL, {"strategy_id": STRATEGY_ID, "order_by": "invalid_column"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_return_400_when_filter_by_column_is_invalid(self, root_client):
        response = root_client.get(URL, {"strategy_id": STRATEGY_ID, "filter_by": "invalid", "filter_value": "100"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_should_include_filterable_and_orderable_columns_in_meta(self, root_client):
        response = root_client.get(URL, {"strategy_id": STRATEGY_ID})

        meta = response.data["meta"]
        assert meta["filterable_columns"] == []
        assert meta["orderable_columns"] == ["nav", "drawdown_pct", "created_at"]
