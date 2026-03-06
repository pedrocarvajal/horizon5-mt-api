import pytest
from rest_framework import status

from app.enums import AccountStatus
from app.models import Account
from tests.feature.conftest import create_user

URL = "/api/v1/accounts/"


@pytest.mark.django_db
class TestListAccounts:
    def test_should_return_200_with_all_accounts(self, root_client, root_account, producer_account):
        response = root_client.get(URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        ids = {account["id"] for account in response.data["data"]}
        assert ids == {root_account.id, producer_account.id}

    def test_should_return_200_with_empty_list_when_no_accounts_exist(self, root_client):
        response = root_client.get(URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"] == []
        assert response.data["meta"]["count"] == 0

    def test_should_return_correct_account_fields(self, root_client, root_user):
        Account.objects.create(
            id=111111,
            user=root_user,
            broker="ICMarkets",
            server="ICMarketsSC-Demo",
            currency="USD",
            leverage=500,
            balance="10000.00",
            equity="10500.00",
            margin="200.00",
            free_margin="10300.00",
            profit="500.00",
            margin_level="5250.00",
        )

        response = root_client.get(URL)

        account_data = response.data["data"][0]
        assert account_data["id"] == 111111
        assert account_data["user_id"] == str(root_user.pk)
        assert account_data["user_email"] == root_user.email
        assert account_data["broker"] == "ICMarkets"
        assert account_data["server"] == "ICMarketsSC-Demo"
        assert account_data["currency"] == "USD"
        assert account_data["leverage"] == 500
        assert account_data["balance"] == "10000.00"
        assert account_data["equity"] == "10500.00"
        assert account_data["margin"] == "200.00"
        assert account_data["free_margin"] == "10300.00"
        assert account_data["profit"] == "500.00"
        assert account_data["margin_level"] == "5250.00"
        assert account_data["status"] == "active"
        assert "created_at" in account_data
        assert "updated_at" in account_data

    def test_should_include_user_info_for_all_accounts(self, root_client, root_user):
        other_user = create_user(email="other@test.co")
        Account.objects.create(id=111111, user=root_user)
        Account.objects.create(id=222222, user=other_user)

        response = root_client.get(URL)

        emails = {account["user_email"] for account in response.data["data"]}
        assert emails == {root_user.email, other_user.email}

    def test_should_return_meta_with_correct_count(self, root_client, root_account, producer_account, platform_account):
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

    def test_should_return_pagination_meta(self, root_client, root_account):
        response = root_client.get(URL)

        assert response.status_code == status.HTTP_200_OK
        pagination = response.data["meta"]["pagination"]
        assert "total" in pagination
        assert "page" in pagination
        assert "per_page" in pagination
        assert "total_pages" in pagination

    def test_should_return_filterable_and_orderable_columns_in_meta(self, root_client):
        response = root_client.get(URL)

        assert "filterable_columns" in response.data["meta"]
        assert "orderable_columns" in response.data["meta"]


@pytest.mark.django_db
class TestListAccountsFiltering:
    def test_should_filter_by_id(self, root_client, root_account, producer_account):
        response = root_client.get(URL, {"filter_by": "id", "filter_value": root_account.id})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["meta"]["pagination"]["total"] == 1
        assert response.data["data"][0]["id"] == root_account.id

    def test_should_filter_by_status_active(self, root_client, root_user, producer_user):
        Account.objects.create(id=111111, user=root_user, status=AccountStatus.ACTIVE)
        Account.objects.create(id=222222, user=producer_user, status=AccountStatus.INACTIVE)

        response = root_client.get(URL, {"filter_by": "status", "filter_value": AccountStatus.ACTIVE})

        assert response.status_code == status.HTTP_200_OK
        returned_ids = {a["id"] for a in response.data["data"]}
        assert 111111 in returned_ids
        assert 222222 not in returned_ids

    def test_should_filter_by_status_inactive(self, root_client, root_user, producer_user):
        Account.objects.create(id=111111, user=root_user, status=AccountStatus.ACTIVE)
        Account.objects.create(id=222222, user=producer_user, status=AccountStatus.INACTIVE)

        response = root_client.get(URL, {"filter_by": "status", "filter_value": AccountStatus.INACTIVE})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["meta"]["pagination"]["total"] == 1
        assert response.data["data"][0]["id"] == 222222

    def test_should_return_empty_when_id_does_not_exist(self, root_client):
        response = root_client.get(URL, {"filter_by": "id", "filter_value": 999999999})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"] == []
        assert response.data["meta"]["pagination"]["total"] == 0

    def test_should_return_400_when_filter_by_is_invalid_column(self, root_client):
        response = root_client.get(URL, {"filter_by": "broker", "filter_value": "ICMarkets"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_should_return_400_when_filter_value_is_missing(self, root_client):
        response = root_client.get(URL, {"filter_by": "status"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_should_return_400_when_filter_by_is_missing(self, root_client):
        response = root_client.get(URL, {"filter_value": "active"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False


@pytest.mark.django_db
class TestListAccountsOrdering:
    def test_should_order_by_id_ascending(self, root_client, root_user):
        Account.objects.create(id=300, user=root_user)
        Account.objects.create(id=100, user=root_user)
        Account.objects.create(id=200, user=root_user)

        response = root_client.get(URL, {"order_by": "id"})

        assert response.status_code == status.HTTP_200_OK
        ids = [a["id"] for a in response.data["data"]]
        assert ids == sorted(ids)

    def test_should_order_by_id_descending(self, root_client, root_user):
        Account.objects.create(id=300, user=root_user)
        Account.objects.create(id=100, user=root_user)
        Account.objects.create(id=200, user=root_user)

        response = root_client.get(URL, {"order_by": "-id"})

        assert response.status_code == status.HTTP_200_OK
        ids = [a["id"] for a in response.data["data"]]
        assert ids == sorted(ids, reverse=True)

    def test_should_return_400_when_order_by_column_is_not_allowed(self, root_client):
        response = root_client.get(URL, {"order_by": "broker"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
