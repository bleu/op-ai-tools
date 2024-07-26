import os
from dotenv import load_dotenv

load_dotenv()

BASEDIR = os.path.abspath(os.path.dirname(__name__))

config = {
    "SECRET": os.getenv("SECRET", "default_secret"),
    "DATABASE_URL": os.getenv("DATABASE_URL"),
    "CELERY": {
        "BROKER_URL": os.getenv("CELERY_BROKER_URL"),
        "RESULT_BACKEND": os.getenv("CELERY_RESULT_BACKEND"),
        "task_ignore_result": True,
    }
}
