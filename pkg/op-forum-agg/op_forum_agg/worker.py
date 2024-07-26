from celery import Celery
from celery.schedules import crontab

from op_forum_agg.app import create_worker_app
from op_forum_agg.config import config
from op_forum_agg.src.sync.categories import execute_categories_sync


def create_celery(app):
    celery = Celery(
        app.import_name,
        backend=config["CELERY"]["RESULT_BACKEND"],
        broker=config["CELERY"]["BROKER_URL"],
    )
    celery.conf.update(app.config)
    celery.conf.timezone = "UTC"
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

    # Executes every Monday morning at 7:30 a.m.
    # sender.add_periodic_task(
    #     crontab(hour=7, minute=30, day_of_week=1),
    #     long_task,
    # )

    # each 10 seconds
    sender.add_periodic_task(10, long_task.s(), name="sync categories")


@celery.task
def long_task():
    #   execute_categories_sync()
    pass
