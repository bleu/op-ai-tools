from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import atexit
from op_data.cli import SYNC_COMMANDS, run_sync
import logging

logger = logging.getLogger(__name__)


def configure_scheduler():
    scheduler = BackgroundScheduler()

    # Schedule jobs with CronTrigger
    # Run 'sync_categories' every day at 00:00
    scheduler.add_job(
        run_sync,
        trigger=CronTrigger(hour=0, minute=0),
        args=[SYNC_COMMANDS['categories']],
        id='sync_categories'
    )

     # Run 'raw_topics' every day at 00:20
    scheduler.add_job(
        run_sync,
        trigger=CronTrigger(hour=0, minute=20),
        args=[SYNC_COMMANDS['raw_topics']],
        id='sync_raw_topics'
    )

     # Run 'sync_summaries' every day at 01:20
    scheduler.add_job(
        run_sync,
        trigger=CronTrigger(hour=1, minute=20),
        args=[SYNC_COMMANDS['summaries']],
        id='sync_summaries'
    )

    # Run 'sync_topics' every day at 02:00
    scheduler.add_job(
        run_sync,
        trigger=CronTrigger(hour=2, minute=10),
        args=[SYNC_COMMANDS['topics']],
        id='sync_topics'
    )

    # Run 'sync_snapshot' every day at 02:30
    scheduler.add_job(
        run_sync,
        trigger=CronTrigger(hour=2, minute=30),
        args=[SYNC_COMMANDS['snapshot']],
        id='sync_snapshot'
    )

    # Run 'sync_agora' every day at 02:30
    scheduler.add_job(
        run_sync,
        trigger=CronTrigger(hour=0, minute=40),
        args=[SYNC_COMMANDS['agora']],
        id='sync_agora'
    )

    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())

    return scheduler
