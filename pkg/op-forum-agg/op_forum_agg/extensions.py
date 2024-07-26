from celery import Celery

celery = Celery()


def register_extensions(app, worker=False):
    celery.config_from_object(app.config["CELERY"])

    if not worker:
        # register celery irrelevant extensions
        pass
