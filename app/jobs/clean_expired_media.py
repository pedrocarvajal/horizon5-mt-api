import structlog

from app.monitors.expired_media import ExpiredMediaCleanup

logger = structlog.get_logger("scheduler")


def run():
    check = ExpiredMediaCleanup()
    logger.info("job_started", job="clean_expired_media")

    try:
        result = check.run()
    except Exception as exception:
        logger.error("job_failed", job="clean_expired_media", error=str(exception))

        return

    logger.info(
        "job_completed",
        job="clean_expired_media",
        status=result["status"],
        deleted=result.get("deleted"),
        errors=result.get("errors"),
    )
