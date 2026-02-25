from typing import ClassVar

from pymongo import ASCENDING, DESCENDING, IndexModel

from app.collections.base import BaseDocument


class Event(BaseDocument):
    collection_name = "events"
    indexes: ClassVar[list] = [
        IndexModel(
            [("account_id", ASCENDING), ("status", ASCENDING), ("created_at", DESCENDING)],
            name="account_status_created",
        ),
    ]
