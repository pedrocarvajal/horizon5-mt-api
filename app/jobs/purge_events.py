from datetime import timedelta

import structlog
from django.utils import timezone

from app.collections.event import Event
from app.enums import EventStatus

logger = structlog.get_logger("scheduler")

RETENTION_DAYS = 90


def run():
    logger.info("job_started", job="purge_events")
    cutoff = timezone.now() - timedelta(days=RETENTION_DAYS)
    query = {
        "status": {"$in": [EventStatus.PROCESSED, EventStatus.FAILED]},
        "created_at": {"$lt": cutoff},
    }

    result = Event.delete_where(query)

    logger.info(
        "job_completed",
        job="purge_events",
        collection="events",
        deleted_count=result.deleted_count,
        retention_days=RETENTION_DAYS,
    )
