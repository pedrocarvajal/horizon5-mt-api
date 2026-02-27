from apscheduler.triggers.cron import CronTrigger

from app.jobs import (
    check_stuck_events,
    clean_expired_media,
    purge_account_snapshots,
    purge_events,
    purge_heartbeats,
    purge_logs,
    purge_strategy_snapshots,
)


def register_jobs(scheduler):
    scheduler.add_job(
        check_stuck_events.run,
        trigger=CronTrigger(hour=3, minute=0),
        id="check_stuck_events",
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        clean_expired_media.run,
        trigger=CronTrigger(hour=3, minute=5),
        id="clean_expired_media",
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        purge_logs.run,
        trigger=CronTrigger(day_of_week="sun", hour=4, minute=0),
        id="purge_logs",
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        purge_heartbeats.run,
        trigger=CronTrigger(day_of_week="sun", hour=4, minute=5),
        id="purge_heartbeats",
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        purge_events.run,
        trigger=CronTrigger(day_of_week="sun", hour=4, minute=10),
        id="purge_events",
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        purge_account_snapshots.run,
        trigger=CronTrigger(day_of_week="sun", hour=4, minute=15),
        id="purge_account_snapshots",
        max_instances=1,
        replace_existing=True,
    )

    scheduler.add_job(
        purge_strategy_snapshots.run,
        trigger=CronTrigger(day_of_week="sun", hour=4, minute=20),
        id="purge_strategy_snapshots",
        max_instances=1,
        replace_existing=True,
    )
