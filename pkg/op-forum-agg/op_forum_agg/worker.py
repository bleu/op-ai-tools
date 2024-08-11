from op_forum_agg.tasks.sync import (
    sync_all,
    sync_categories,
    sync_raw_threads,
    sync_forum_posts,
)

from celery import Celery
from celery.schedules import crontab
from op_forum_agg.app import create_worker_app
from op_forum_agg.config import config


def create_celery(app):
    celery = Celery(
        app.import_name,
        backend=config["CELERY"]["RESULT_BACKEND"],
        broker=config["CELERY"]["BROKER_URL"],
    )
    celery.conf.update(app.config)
    celery.timezone = "UTC"
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


flask_app = create_worker_app()
celery = create_celery(flask_app)


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Sync all data every day at midnight
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        sync_all.s().on_error(handle_task_error),
        name="sync all forum data"
    )

    # Sync categories every hour
    sender.add_periodic_task(
        crontab(minute=0),
        sync_categories.s().on_error(handle_task_error),
        name="sync categories"
    )

    # Sync raw threads every 30 minutes
    sender.add_periodic_task(
        30 * 60,
        sync_raw_threads.s().on_error(handle_task_error),
        name="sync raw threads"
    )

    # Sync forum posts every 15 minutes
    sender.add_periodic_task(
        15 * 60,
        sync_forum_posts.s().on_error(handle_task_error),
        name="sync forum posts"
    )

def handle_task_error(request, exc, traceback):
    logger.error(f"Task {request.id} raised exception: {exc}")
    # You can add additional error handling logic here, such as sending notifications
