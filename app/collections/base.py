from datetime import UTC, datetime
from typing import ClassVar

from bson import ObjectId

from app.database.mongodb import get_collection


class BaseDocument:
    collection_name: ClassVar[str]
    indexes: ClassVar[list] = []

    @classmethod
    def collection(cls):
        return get_collection(cls.collection_name)

    @classmethod
    def ensure_indexes(cls):
        if cls.indexes:
            cls.collection().create_indexes(cls.indexes)

    @classmethod
    def create(cls, data: dict) -> dict:
        now = datetime.now(UTC)
        data.setdefault("created_at", now)
        data.setdefault("updated_at", now)
        result = cls.collection().insert_one(data)
        data["_id"] = result.inserted_id
        return data

    @classmethod
    def find(cls, document_id: str) -> dict | None:
        return cls.collection().find_one({"_id": ObjectId(document_id)})

    @classmethod
    def find_one(cls, query: dict) -> dict | None:
        return cls.collection().find_one(query)

    @classmethod
    def where(cls, query: dict, **kwargs):
        return cls.collection().find(query, **kwargs)

    @classmethod
    def all(cls):
        return cls.collection().find()

    @classmethod
    def count(cls, query: dict | None = None) -> int:
        return cls.collection().count_documents(query or {})

    @classmethod
    def update_one(cls, document_id: str, data: dict) -> dict | None:
        data["updated_at"] = datetime.now(UTC)
        return cls.collection().find_one_and_update(
            {"_id": ObjectId(document_id)},
            {"$set": data},
            return_document=True,
        )

    @classmethod
    def find_one_and_update(cls, query: dict, update: dict, **kwargs):
        return cls.collection().find_one_and_update(query, update, **kwargs)

    @classmethod
    def delete(cls, document_id: str):
        return cls.collection().delete_one({"_id": ObjectId(document_id)})

    @classmethod
    def delete_where(cls, query: dict):
        return cls.collection().delete_many(query)
