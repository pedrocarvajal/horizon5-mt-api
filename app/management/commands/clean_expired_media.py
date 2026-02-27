import structlog
from django.core.management.base import BaseCommand

from app.monitors.expired_media import ExpiredMediaCleanup

logger = structlog.get_logger("monitor")


class Command(BaseCommand):
    help = "Clean up expired media files from storage and database"

    def handle(self, *_args, **_options) -> None:
        check = ExpiredMediaCleanup()
        logger.info("check_started", check=check.name)

        try:
            result = check.run()
        except Exception as exception:
            logger.error("check_failed", check=check.name, error=str(exception))
            return

        logger.info(
            "check_completed",
            check=check.name,
            status=result["status"],
            deleted=result.get("deleted"),
            errors=result.get("errors"),
        )
