from bson import ObjectId
from django.utils import timezone

from app.collections.event import Event
from app.enums import EventStatus


def create_event(account_id, user_id, **overrides):
    now = timezone.now()
    defaults = {
        "account_id": str(account_id),
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
