import structlog
from django.core.management.base import BaseCommand

from app.monitors.stuck_events import StuckEventsCheck

logger = structlog.get_logger("monitor")

CHECKS = [
    StuckEventsCheck,
]


class Command(BaseCommand):
    help = "Run all monitor checks"

    def handle(self, *_args, **_options):
        logger.info("monitor_started", checks=len(CHECKS))
        results = []
        for check_class in CHECKS:
            check = check_class()
            try:
                result = check.run()
                results.append(result)
            except Exception as exc:
                logger.error("monitor_check_failed", check=check.name, error=str(exc))
                results.append({"check": check.name, "status": "error", "error": str(exc)})

        warnings = [r for r in results if r["status"] == "warning"]
        errors = [r for r in results if r["status"] == "error"]
        logger.info(
            "monitor_completed",
            total=len(results),
            warnings=len(warnings),
            errors=len(errors),
        )
