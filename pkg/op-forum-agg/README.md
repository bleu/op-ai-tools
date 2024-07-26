# run the app

FLASK_APP=app:create_app poetry run flask run

# run worker and flower

poetry run celery -A worker.celery worker --loglevel=DEBUG
poetry run celery -A worker.celery flower --port=5555 --broker=redis://redis:6379/0
poetry run celery -A worker.celery beat --loglevel=info

# run lint and format

poetry run black .
poetry run flake8 .
