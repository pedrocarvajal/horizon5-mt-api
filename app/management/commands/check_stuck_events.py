import structlog
from django.core.management.base import BaseCommand

from app.monitors.stuck_events import StuckEventsCheck

logger = structlog.get_logger("monitor")


class Command(BaseCommand):
    help = "Check for events stuck in delivered status beyond the threshold"

    def handle(self, *_args, **_options) -> None:
        check = StuckEventsCheck()
        logger.info("check_started", check=check.name)

        try:
            result = check.run()
        except Exception as exception:
            logger.error("check_failed", check=check.name, error=str(exception))
            return

        logger.info("check_completed", check=check.name, status=result["status"], count=result.get("count"))
