import pytest
from rest_framework import status

from app.enums import EventKey

URL = "/api/v1/events/keys/"


@pytest.mark.django_db
class TestListEventKeys:
    def test_should_return_200_with_all_event_keys(self, authenticated_client):
        response = authenticated_client.get(URL)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert len(response.data["data"]) == len(EventKey)

    def test_should_include_key_name_and_schema_for_each_entry(self, authenticated_client):
        response = authenticated_client.get(URL)

        for entry in response.data["data"]:
            assert "key" in entry
            assert "name" in entry
            assert "schema" in entry

    def test_should_return_401_when_unauthenticated(self, api_client):
        response = api_client.get(URL)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False
