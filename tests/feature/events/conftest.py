import pytest
from bson import ObjectId
from django.utils import timezone

from app.collections.event import Event
from app.enums import EventStatus
from app.models import Strategy


def create_event(account_id, user_id, **overrides):
    now = timezone.now()
    defaults = {
        "account_id": account_id,
        "user_id": str(user_id),
        "consumer_id": None,
        "key": "post.order",
        "payload": {
            "symbol": "BTCUSDT",
            "strategy": 1,
            "type": "buy",
            "volume": 0.5,
        },
        "response": None,
        "status": EventStatus.PENDING,
        "delivered_at": None,
        "processed_at": None,
        "attempts": 0,
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(overrides)
    return Event.create(defaults)


def fake_object_id():
    return str(ObjectId())


@pytest.fixture()
def producer_strategy(producer_account):
    return Strategy.objects.create(
        account=producer_account,
        symbol="BTCUSDT",
        prefix="BTC",
        name="BTC Scalper",
        magic_number=1,
        balance="0.00",
    )
