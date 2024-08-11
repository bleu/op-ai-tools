from flask import Flask

from op_forum_agg.config import config
from op_forum_agg.extensions import register_extensions


def create_app():
    """Create and configure the main Flask application."""
    app = Flask(__name__)
    app.config.from_mapping(**config)
    app.url_map.strict_slashes = False

    register_extensions(app)

    return app


def create_worker_app():
    """Create a minimal Flask application for Celery worker without routes."""
    app = Flask(__name__)
    app.config.from_mapping(**config)

    register_extensions(app, worker=True)

    return app
