from datetime import timedelta

import structlog
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.collections.event import Event
from app.enums import EventStatus

logger = structlog.get_logger("purge")

RETENTION_DAYS = 90


class Command(BaseCommand):
    help = "Purge terminal events (processed/failed) older than 90 days"

    def handle(self, *_args, **_options) -> None:
        cutoff = timezone.now() - timedelta(days=RETENTION_DAYS)
        query = {
            "status": {"$in": [EventStatus.PROCESSED, EventStatus.FAILED]},
            "created_at": {"$lt": cutoff},
        }

        result = Event.delete_where(query)

        logger.info(
            "purge_completed", collection="events", deleted_count=result.deleted_count, retention_days=RETENTION_DAYS
        )
