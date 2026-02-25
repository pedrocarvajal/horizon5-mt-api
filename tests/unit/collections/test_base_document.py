from datetime import UTC, datetime

from bson import ObjectId
from django.utils import timezone

from tests.conftest import ConcreteDocument, ConcreteDocumentWithIndexes


class TestCollection:
    def test_returns_pymongo_collection_with_correct_name(self):
        collection = ConcreteDocument.collection()

        assert collection.name == "test_collection"


class TestEnsureIndexes:
    def test_creates_indexes_when_indexes_defined(self):
        ConcreteDocumentWithIndexes.ensure_indexes()

        index_info = ConcreteDocumentWithIndexes.collection().index_information()
        assert "name_index" in index_info

    def test_does_nothing_when_no_indexes(self):
        ConcreteDocument.create({"name": "seed"})

        ConcreteDocument.ensure_indexes()

        index_info = ConcreteDocument.collection().index_information()
        assert "name_index" not in index_info


class TestCreate:
    def test_inserts_document_and_returns_it_with_id(self):
        result = ConcreteDocument.create({"name": "test"})

        assert isinstance(result["_id"], ObjectId)
        assert result["name"] == "test"

    def test_persists_document_in_database(self):
        result = ConcreteDocument.create({"name": "test"})

        found = ConcreteDocument.find(str(result["_id"]))
        assert found is not None
        assert found["name"] == "test"

    def test_sets_created_at_and_updated_at_timestamps(self):
        before = timezone.now()
        result = ConcreteDocument.create({"name": "test"})
        after = timezone.now()

        assert before <= result["created_at"] <= after
        assert before <= result["updated_at"] <= after

    def test_does_not_overwrite_existing_created_at(self):
        existing_time = datetime(2024, 1, 1, tzinfo=UTC)

        result = ConcreteDocument.create({"created_at": existing_time})

        assert result["created_at"] == existing_time

    def test_does_not_overwrite_existing_updated_at(self):
        existing_time = datetime(2024, 1, 1, tzinfo=UTC)

        result = ConcreteDocument.create({"updated_at": existing_time})

        assert result["updated_at"] == existing_time


class TestFind:
    def test_returns_document_by_id(self):
        created = ConcreteDocument.create({"name": "findable"})

        result = ConcreteDocument.find(str(created["_id"]))

        assert result is not None
        assert result["name"] == "findable"

    def test_returns_none_when_document_not_found(self):
        result = ConcreteDocument.find(str(ObjectId()))

        assert result is None


class TestFindOne:
    def test_returns_document_matching_query(self):
        ConcreteDocument.create({"email": "test@example.com"})

        result = ConcreteDocument.find_one({"email": "test@example.com"})

        assert result is not None
        assert result["email"] == "test@example.com"

    def test_returns_none_when_no_match(self):
        result = ConcreteDocument.find_one({"email": "nonexistent@example.com"})

        assert result is None


class TestWhere:
    def test_returns_cursor_with_matching_documents(self):
        ConcreteDocument.create({"status": "active", "name": "one"})
        ConcreteDocument.create({"status": "active", "name": "two"})
        ConcreteDocument.create({"status": "inactive", "name": "three"})

        results = list(ConcreteDocument.where({"status": "active"}))

        assert len(results) == 2
        names = {document["name"] for document in results}
        assert names == {"one", "two"}

    def test_passes_kwargs_to_pymongo_find(self):
        ConcreteDocument.create({"status": "active", "name": "test"})

        results = list(ConcreteDocument.where({"status": "active"}, projection={"name": 1, "_id": 0}))

        assert results[0] == {"name": "test"}


class TestAll:
    def test_returns_all_documents(self):
        ConcreteDocument.create({"name": "first"})
        ConcreteDocument.create({"name": "second"})

        results = list(ConcreteDocument.all())

        assert len(results) == 2


class TestCount:
    def test_counts_documents_matching_query(self):
        ConcreteDocument.create({"status": "active"})
        ConcreteDocument.create({"status": "active"})
        ConcreteDocument.create({"status": "inactive"})

        result = ConcreteDocument.count({"status": "active"})

        assert result == 2

    def test_counts_all_documents_when_no_query(self):
        ConcreteDocument.create({"name": "one"})
        ConcreteDocument.create({"name": "two"})
        ConcreteDocument.create({"name": "three"})

        result = ConcreteDocument.count()

        assert result == 3


class TestUpdateOne:
    def test_updates_document_and_returns_it(self):
        created = ConcreteDocument.create({"name": "original"})

        result = ConcreteDocument.update_one(str(created["_id"]), {"name": "updated"})

        assert result is not None
        assert result["name"] == "updated"

    def test_sets_updated_at_timestamp(self):
        created = ConcreteDocument.create({"name": "original"})
        original_updated_at = created["updated_at"]

        result = ConcreteDocument.update_one(str(created["_id"]), {"name": "updated"})

        assert result["updated_at"] > original_updated_at

    def test_persists_changes_in_database(self):
        created = ConcreteDocument.create({"name": "original"})

        ConcreteDocument.update_one(str(created["_id"]), {"name": "updated"})

        found = ConcreteDocument.find(str(created["_id"]))
        assert found["name"] == "updated"


class TestFindOneAndUpdate:
    def test_updates_and_returns_matching_document(self):
        ConcreteDocument.create({"status": "pending", "name": "test"})

        result = ConcreteDocument.find_one_and_update(
            {"status": "pending"},
            {"$set": {"status": "active"}},
            return_document=True,
        )

        assert result is not None
        assert result["status"] == "active"


class TestDelete:
    def test_removes_document_from_database(self):
        created = ConcreteDocument.create({"name": "deletable"})
        document_id = str(created["_id"])

        ConcreteDocument.delete(document_id)

        assert ConcreteDocument.find(document_id) is None

    def test_returns_delete_result(self):
        created = ConcreteDocument.create({"name": "deletable"})

        result = ConcreteDocument.delete(str(created["_id"]))

        assert result.deleted_count == 1


class TestDeleteWhere:
    def test_removes_all_matching_documents(self):
        ConcreteDocument.create({"status": "expired"})
        ConcreteDocument.create({"status": "expired"})
        ConcreteDocument.create({"status": "active"})

        ConcreteDocument.delete_where({"status": "expired"})

        assert ConcreteDocument.count({"status": "expired"}) == 0
        assert ConcreteDocument.count({"status": "active"}) == 1

    def test_returns_delete_result_with_count(self):
        ConcreteDocument.create({"status": "expired"})
        ConcreteDocument.create({"status": "expired"})

        result = ConcreteDocument.delete_where({"status": "expired"})

        assert result.deleted_count == 2
