from typing import ClassVar

from pymongo import ASCENDING, DESCENDING, IndexModel

from app.collections.base import BaseDocument


class StrategySnapshot(BaseDocument):
    collection_name = "strategy_snapshots"
    indexes: ClassVar[list] = [
        IndexModel(
            [("account_id", ASCENDING), ("strategy_id", ASCENDING), ("created_at", DESCENDING)],
            name="account_strategy_created",
        ),
    ]
