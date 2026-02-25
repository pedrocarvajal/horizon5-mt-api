from enum import StrEnum


class EventStatus(StrEnum):
    PENDING = "pending"
    DELIVERED = "delivered"
    PROCESSED = "processed"
    FAILED = "failed"
