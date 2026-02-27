from datetime import timedelta

import structlog
from django.utils import timezone

from app.collections.account_snapshot import AccountSnapshot

logger = structlog.get_logger("scheduler")

RETENTION_DAYS = 180


def run():
    logger.info("job_started", job="purge_account_snapshots")
    cutoff = timezone.now() - timedelta(days=RETENTION_DAYS)
    result = AccountSnapshot.delete_where({"created_at": {"$lt": cutoff}})

    logger.info(
        "job_completed",
        job="purge_account_snapshots",
        collection="account_snapshots",
        deleted_count=result.deleted_count,
        retention_days=RETENTION_DAYS,
    )
