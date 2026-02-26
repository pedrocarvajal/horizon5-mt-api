import pytest
from django.core.cache import cache
from rest_framework.test import APIClient

from app.models.user import User

TEST_PASSWORD = "securepassword123"  # noqa: S105


def create_user(email: str, password: str = TEST_PASSWORD, **kwargs) -> User:
    return User.objects.create_user(email=email, password=password, **kwargs)


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
