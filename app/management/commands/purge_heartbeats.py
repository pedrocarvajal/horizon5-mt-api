from datetime import timedelta

import structlog
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.collections.heartbeat import Heartbeat

logger = structlog.get_logger("purge")

RETENTION_DAYS = 30


class Command(BaseCommand):
    help = "Purge heartbeats older than 30 days"

    def handle(self, *_args, **_options) -> None:
        cutoff = timezone.now() - timedelta(days=RETENTION_DAYS)
        result = Heartbeat.delete_where({"created_at": {"$lt": cutoff}})

        logger.info(
            "purge_completed",
            collection="heartbeats",
            deleted_count=result.deleted_count,
            retention_days=RETENTION_DAYS,
        )
