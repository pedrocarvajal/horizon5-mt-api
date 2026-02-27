from datetime import timedelta

import structlog
from django.utils import timezone

from app.collections.log import Log

logger = structlog.get_logger("scheduler")

RETENTION_DAYS = 90


def run():
    logger.info("job_started", job="purge_logs")
    cutoff = timezone.now() - timedelta(days=RETENTION_DAYS)
    result = Log.delete_where({"created_at": {"$lt": cutoff}})

    logger.info(
        "job_completed",
        job="purge_logs",
        collection="logs",
        deleted_count=result.deleted_count,
        retention_days=RETENTION_DAYS,
    )
