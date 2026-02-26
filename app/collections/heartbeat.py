from typing import ClassVar

from pymongo import ASCENDING, DESCENDING, IndexModel

from app.collections.base import BaseDocument


class Heartbeat(BaseDocument):
    collection_name = "heartbeats"
    indexes: ClassVar[list] = [
        IndexModel(
            [("account_id", ASCENDING), ("created_at", DESCENDING)],
            name="account_created",
        ),
        IndexModel(
            [("strategy_id", ASCENDING), ("created_at", DESCENDING)],
            name="strategy_created",
        ),
    ]
