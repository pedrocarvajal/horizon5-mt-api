from typing import ClassVar

from pymongo import ASCENDING, DESCENDING, IndexModel

from app.collections.base import BaseDocument


class Log(BaseDocument):
    collection_name = "logs"
    indexes: ClassVar[list] = [
        IndexModel(
            [("account_id", ASCENDING), ("created_at", DESCENDING)],
            name="account_created",
        ),
        IndexModel(
            [("level", ASCENDING)],
            name="level",
        ),
    ]
