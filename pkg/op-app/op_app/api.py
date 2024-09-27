from quart import Quart, request, jsonify
from quart_cors import cors
from quart_rate_limiter import RateLimiter, rate_limit
from op_brains.exceptions import UnsupportedVectorstoreError
from op_brains.config import POSTHOG_API_KEY
from op_brains.chat.utils import process_question
from posthog import Posthog
from datetime import timedelta
from functools import wraps
import os
from op_core.config import Config
from tortoise.contrib.quart import register_tortoise
from quart_tasks import QuartTasks
import asyncio
from op_app.utils.model_predicted_answer import model_predicted_answer
from op_data.cli import (
    sync_categories,
    sync_raw_topics,
    sync_topics,
    sync_summaries,
    sync_snapshot,
    sync_agora,
)
from honeybadger import honeybadger
from op_data.sources.incremental_indexer import IncrementalIndexerService
from op_brains.chat.classify import classify_question

app = Quart(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_API_SECRET_KEY")
app.config["HONEYBADGER_ENVIRONMENT"] = os.getenv("ENV")
app.config["HONEYBADGER_API_KEY"] = os.getenv("HONEYBADGER_API_KEY")

app = cors(app)
tasks = QuartTasks(app)
posthog = Posthog(POSTHOG_API_KEY, host="https://us.i.posthog.com", sync_mode=True)
limiter = RateLimiter(app)

honeybadger.configure(
    api_key=app.config["HONEYBADGER_API_KEY"],
    environment=app.config["HONEYBADGER_ENVIRONMENT"],
)

register_tortoise(
    app,
    config=Config.get_tortoise_config(),
    generate_schemas=False,
)


def handle_question(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        data = await request.get_json()
        if data is not None:
            question = data.get("question")
            memory = data.get("memory", [])
        else:
            question = None
            memory = []

        if not question:
            return jsonify({"error": "No question provided"}), 400

        return await func(question, memory, *args, **kwargs)

    return wrapper


@app.errorhandler(Exception)
def handle_exception(e):
    honeybadger.notify(e)
    if isinstance(e, UnsupportedVectorstoreError):
        return jsonify({"error": str(e)}), 400
    return jsonify({"error": "An unexpected error occurred during prediction"}), 500


async def capture_predict_event(question, result, user_token):
    answer = result["data"]["answer"] if result["data"] else ""
    classifications = await classify_question(result)

    posthog_event = (
        "MODEL_PREDICTED_ANSWER"
        if model_predicted_answer(answer)
        else "MODEL_FAILED_TO_PREDICT"
    )

    posthog.capture(
        user_token,
        posthog_event,
        {
            "endpoint": "predict",
            "question": question,
            "classifications": classifications,
            "answer": answer,
            "error": result.get("error"),
        },
    )


@app.route("/predict", methods=["POST"])
@rate_limit(100, timedelta(minutes=1))
@handle_question
async def predict(question, memory):
    user_token = request.headers.get("x-user-id")
    result = await process_question(question, memory)

    # enqueue background task to capture predict event
    app.add_background_task(capture_predict_event, question, result, user_token)

    return jsonify(result)


@app.after_request
def after_request(response):
    posthog.flush()
    return response


@tasks.cron("0 */6 * * *")
async def sync_all():
    await sync_categories()
    await sync_raw_topics()
    await sync_topics()
    await sync_summaries()
    await sync_snapshot()
    await sync_agora()


@tasks.cron("0 0 1 * *")
async def sync_indexes():
    indexer = IncrementalIndexerService()
    await indexer.acquire_and_save()


if __name__ == "__main__":
    app.run(host="0.0.0.0")
