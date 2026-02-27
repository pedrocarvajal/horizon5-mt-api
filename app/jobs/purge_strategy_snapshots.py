from datetime import timedelta

import structlog
from django.utils import timezone

from app.collections.strategy_snapshot import StrategySnapshot

logger = structlog.get_logger("scheduler")

RETENTION_DAYS = 180


def run():
    logger.info("job_started", job="purge_strategy_snapshots")
    cutoff = timezone.now() - timedelta(days=RETENTION_DAYS)
    result = StrategySnapshot.delete_where({"created_at": {"$lt": cutoff}})

    logger.info(
        "job_completed",
        job="purge_strategy_snapshots",
        collection="strategy_snapshots",
        deleted_count=result.deleted_count,
        retention_days=RETENTION_DAYS,
    )
