import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from app.enums import SystemRole
from app.models import Account
from app.models.user import User

TEST_PASSWORD = "securepassword123"  # noqa: S105


def create_user(email: str, password: str = TEST_PASSWORD, **kwargs) -> User:
    return User.objects.create_user(email=email, password=password, **kwargs)


@pytest.fixture()
def root_user(db):  # noqa: ARG001
    return create_user(email="root@test.co", role=SystemRole.ROOT)


@pytest.fixture()
def authenticated_client(active_user):
    client = APIClient()
    client.force_authenticate(user=active_user)
    return client


@pytest.fixture()
def root_client(root_user):
    client = APIClient()
    client.force_authenticate(user=root_user)
    return client


@pytest.fixture(autouse=True)
def clear_cache():
    yield
    cache.clear()


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture()
def login_url():
    return "/api/v1/auth/login/"


@pytest.fixture()
def active_user(db):  # noqa: ARG001
    return create_user(email="active@test.co")


@pytest.fixture()
def inactive_user(db):  # noqa: ARG001
    return create_user(email="inactive@test.co", is_active=False)


@pytest.fixture()
def producer_user(db):  # noqa: ARG001
    return create_user(email="producer@test.co", role=SystemRole.PRODUCER)


@pytest.fixture()
def producer_client(producer_user):
    client = APIClient()
    client.force_authenticate(user=producer_user)
    return client


@pytest.fixture()
def platform_user(db):  # noqa: ARG001
    return create_user(email="platform@test.co", role=SystemRole.PLATFORM)


@pytest.fixture()
def platform_client(platform_user):
    client = APIClient()
    client.force_authenticate(user=platform_user)
    return client


@pytest.fixture()
def producer_account(producer_user):
    return Account.objects.create(id=123456, user=producer_user)


@pytest.fixture()
def platform_account(platform_user):
    return Account.objects.create(id=789012, user=platform_user)


@pytest.fixture()
def root_account(root_user):
    return Account.objects.create(id=999999, user=root_user)
