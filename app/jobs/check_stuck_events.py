import structlog

from app.monitors.stuck_events import StuckEventsCheck

logger = structlog.get_logger("scheduler")


def run():
    check = StuckEventsCheck()
    logger.info("job_started", job="check_stuck_events")

    try:
        result = check.run()
    except Exception as exception:
        logger.error("job_failed", job="check_stuck_events", error=str(exception))

        return

    logger.info("job_completed", job="check_stuck_events", status=result["status"], count=result.get("count"))
