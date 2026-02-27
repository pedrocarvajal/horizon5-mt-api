from datetime import timedelta

import structlog
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.collections.account_snapshot import AccountSnapshot

logger = structlog.get_logger("purge")

RETENTION_DAYS = 180


class Command(BaseCommand):
    help = "Purge account snapshots older than 180 days"

    def handle(self, *_args, **_options) -> None:
        cutoff = timezone.now() - timedelta(days=RETENTION_DAYS)
        result = AccountSnapshot.delete_where({"created_at": {"$lt": cutoff}})

        logger.info(
            "purge_completed",
            collection="account_snapshots",
            deleted_count=result.deleted_count,
            retention_days=RETENTION_DAYS,
        )
