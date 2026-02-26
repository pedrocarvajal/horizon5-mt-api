from typing import ClassVar

from pymongo import ASCENDING, DESCENDING, IndexModel

from app.collections.base import BaseDocument


class AccountSnapshot(BaseDocument):
    collection_name = "account_snapshots"
    indexes: ClassVar[list] = [
        IndexModel(
            [("account_id", ASCENDING), ("created_at", DESCENDING)],
            name="account_created",
        ),
    ]
