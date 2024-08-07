import os
from dotenv import load_dotenv

load_dotenv()

BASEDIR = os.path.abspath(os.path.dirname(__name__))

if os.getenv("DATABASE_URL"):
    raise ValueError("DATABASE_URL is not set")

TORTOISE_ORM = {
    "connections": {"default": os.getenv("DATABASE_URL")},
    "apps": {
        "models": {
            "models": ["op_forum_agg.db.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

config = {
    "SECRET": os.getenv("SECRET", "default_secret"),
    "DATABASE_URL": os.getenv("DATABASE_URL"),
    "CELERY": {
        "BROKER_URL": os.getenv("CELERY_BROKER_URL"),
        "RESULT_BACKEND": os.getenv("CELERY_RESULT_BACKEND"),
        "task_ignore_result": True,
    },
    "TORTOISE_ORM": TORTOISE_ORM,
}
