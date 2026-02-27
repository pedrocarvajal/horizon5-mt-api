import sys
from typing import Final

import structlog
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from app.scheduler import register_jobs

logger = structlog.get_logger()

SECONDS_IN_ONE_WEEK: Final = 604_800


class Command(BaseCommand):
    help = "Runs the APScheduler daemon for periodic tasks."

    @staticmethod
    def delete_old_job_executions(max_age=SECONDS_IN_ONE_WEEK):
        DjangoJobExecution.objects.delete_old_job_executions(max_age)  # type: ignore[attr-defined]
        logger.info("old_job_executions_deleted", max_age_seconds=max_age)

    def handle(self, *_args, **_options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        register_jobs(scheduler)

        scheduler.add_job(
            self.delete_old_job_executions,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )

        logger.info("scheduler_started")

        try:
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("scheduler_stopped")
            scheduler.shutdown()
            sys.exit(0)
