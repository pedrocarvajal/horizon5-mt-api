from datetime import timedelta

import structlog
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.collections.strategy_snapshot import StrategySnapshot

logger = structlog.get_logger("purge")

RETENTION_DAYS = 180


class Command(BaseCommand):
    help = "Purge strategy snapshots older than 180 days"

    def handle(self, *_args, **_options) -> None:
        cutoff = timezone.now() - timedelta(days=RETENTION_DAYS)
        result = StrategySnapshot.delete_where({"created_at": {"$lt": cutoff}})

        logger.info(
            "purge_completed",
            collection="strategy_snapshots",
            deleted_count=result.deleted_count,
            retention_days=RETENTION_DAYS,
        )
