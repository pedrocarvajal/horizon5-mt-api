from functools import lru_cache

from pymongo import MongoClient
from pymongo.database import Database


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    from django.conf import settings  # noqa: PLC0415

    return MongoClient(settings.MONGODB_URI)


def get_database() -> Database:
    client = get_client()
    return client.get_default_database()


def get_collection(name: str):
    return get_database()[name]
