from datetime import timedelta

import structlog
from django.utils import timezone

from app.collections.heartbeat import Heartbeat

logger = structlog.get_logger("scheduler")

RETENTION_DAYS = 30


def run():
    logger.info("job_started", job="purge_heartbeats")
    cutoff = timezone.now() - timedelta(days=RETENTION_DAYS)
    result = Heartbeat.delete_where({"created_at": {"$lt": cutoff}})

    logger.info(
        "job_completed",
        job="purge_heartbeats",
        collection="heartbeats",
        deleted_count=result.deleted_count,
        retention_days=RETENTION_DAYS,
    )
