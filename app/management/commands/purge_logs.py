from datetime import timedelta

import structlog
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.collections.log import Log

logger = structlog.get_logger("purge")

RETENTION_DAYS = 90


class Command(BaseCommand):
    help = "Purge logs older than 90 days"

    def handle(self, *_args, **_options) -> None:
        cutoff = timezone.now() - timedelta(days=RETENTION_DAYS)
        result = Log.delete_where({"created_at": {"$lt": cutoff}})

        logger.info(
            "purge_completed", collection="logs", deleted_count=result.deleted_count, retention_days=RETENTION_DAYS
        )
