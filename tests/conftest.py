from typing import ClassVar
from unittest.mock import patch

import pytest
from django.conf import settings
from pymongo import IndexModel, MongoClient

from app.collections.base import BaseDocument


class ConcreteDocument(BaseDocument):
    collection_name = "test_collection"
    indexes: ClassVar[list] = []


class ConcreteDocumentWithIndexes(BaseDocument):
    collection_name = "test_indexed_collection"
    indexes: ClassVar[list] = [IndexModel([("name", 1)], name="name_index")]


@pytest.fixture(scope="session")
def mongodb_client():
    client = MongoClient(settings.MONGODB_URI, tz_aware=True)
    yield client
    client.close()


@pytest.fixture(scope="session")
def mongodb_database(mongodb_client):
    return mongodb_client.get_default_database()


@pytest.fixture(autouse=True)
def patch_get_collection(mongodb_database):
    with patch("app.collections.base.get_collection") as patched:
        patched.side_effect = lambda name: mongodb_database[name]
        yield


@pytest.fixture(autouse=True)
def clean_collections(mongodb_database):
    yield
    for name in mongodb_database.list_collection_names():
        mongodb_database.drop_collection(name)
