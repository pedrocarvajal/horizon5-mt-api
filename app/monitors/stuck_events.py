from datetime import UTC, datetime, timedelta

import structlog

from app.collections.event import Event
from app.enums import EventStatus

logger = structlog.get_logger("monitor")


class StuckEventsCheck:
    name = "stuck_events"

    def run(self):
        threshold = datetime.now(UTC) - timedelta(hours=24)
        count = Event.count(
            {
                "status": EventStatus.DELIVERED,
                "delivered_at": {"$lt": threshold},
            }
        )
        if count > 0:
            logger.warning("stuck_events_detected", count=count, threshold_hours=24)
        else:
            logger.info("stuck_events_ok", count=0)
        return {"check": self.name, "count": count, "status": "warning" if count > 0 else "ok"}
