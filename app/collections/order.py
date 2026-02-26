from typing import ClassVar

from pymongo import ASCENDING, IndexModel

from app.collections.base import BaseDocument


class Order(BaseDocument):
    collection_name = "orders"
    indexes: ClassVar[list] = [
        IndexModel(
            [("account_id", ASCENDING), ("status", ASCENDING)],
            name="account_status",
        ),
        IndexModel(
            [("strategy_id", ASCENDING)],
            name="strategy",
        ),
    ]
